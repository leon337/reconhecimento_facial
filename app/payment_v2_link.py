"""Simulação de associação de trabalhadores do XLSX ao cadastro funcional Potiguar V2.

Dados nominativos são usados somente em memória durante a requisição, sem exibição,
persistência, CPF, chave PIX ou cálculos financeiros. Nenhuma associação é salva.
"""
from __future__ import annotations

import io
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from xml.etree import ElementTree as ET

from app.payment_import import WorkbookPreviewError
from app.payment_mapping import MappingPreview, NS, WorksheetHint

MAX_SOURCE_ROWS = 1600
MAX_IDENTITIES = 1000
MAX_EMPLOYEES_IN_SCOPE = 10000
MAX_VISIBLE_ROWS = 75
COL_PATTERN = re.compile(r"^([A-Z]{1,3})([1-9][0-9]*)$")
MERGE_PATTERN = re.compile(r"^([A-Z]{1,3})([1-9][0-9]*):([A-Z]{1,3})([1-9][0-9]*)$")


@dataclass(frozen=True)
class TransientName:
    row_number: int
    identity: str = field(repr=False)
    invalid: bool = False


@dataclass(frozen=True)
class V2EmployeeRef:
    employee_id: int = field(repr=False)
    full_name: str = field(repr=False)
    active: bool = False
    has_v2_record: bool = False


@dataclass(frozen=True)
class V2MatchRow:
    row_number: int
    status: str


@dataclass(frozen=True)
class V2LinkPreview:
    source_hash_prefix: str
    data_column: str
    examined: int
    counts: tuple[tuple[str, int], ...]
    sample: tuple[V2MatchRow, ...]
    limited: bool
    can_commit: bool = False

    @property
    def matched(self) -> int:
        return dict(self.counts).get("v2_match", 0)


STATUS_DESCRIPTIONS = {
    "v2_match": "Correspondência única na V2 (ainda não vinculada)",
    "unmatched": "Sem correspondência na V2",
    "legacy_only": "Cadastro legado, sem registro V2",
    "inactive": "Funcionário inativo",
    "ambiguous": "Mais de um cadastro com o mesmo nome",
    "duplicate_source": "Nome repetido na mesma planilha",
    "invalid_source": "Identificação inválida ou proveniente de fórmula",
}


def _key(text: str) -> str:
    """Normalização estrita de nome; nunca retorna o nome na visualização."""
    if not isinstance(text, str) or not 3 <= len(text.strip()) <= 120:
        return ""
    value = unicodedata.normalize("NFKD", text.strip().upper())
    value = "".join(c for c in value if not unicodedata.combining(c))
    # CPF, IDs numéricos ou sufixos com números não são nomes seguros.
    if any(c.isdigit() for c in value):
        return ""
    value = re.sub(r"[^A-Z ]", " ", value)
    value = " ".join(value.split())
    if len(value) < 3 or len(value.split()) < 2:
        return ""
    return value


def _inline_text(cell) -> str:
    inline = cell.find(NS + "is")
    if inline is None:
        return ""
    parts = []
    remaining = 122
    for node in inline.iter(NS + "t"):
        chunk = (node.text or "")[:remaining]
        parts.append(chunk)
        remaining -= len(chunk)
        if remaining <= 0:
            break
    return "".join(parts)


def _col_number(column: str) -> int:
    value = 0
    for char in column:
        value = value * 26 + (ord(char) - ord("A") + 1)
    return value


def _merged_name_column(book: zipfile.ZipFile, path: str, anchor: str, row: int) -> str:
    """Cabeçalho A3:B3 => nome em B. Não adivinha outras colunas."""
    try:
        with book.open(path) as stream:
            for _, element in ET.iterparse(stream, events=("end",)):
                if element.tag == NS + "mergeCell":
                    match = MERGE_PATTERN.fullmatch(element.get("ref", ""))
                    if match:
                        first_col, start_row, last_col, end_row = match.groups()
                        if (
                            first_col == anchor and int(start_row) == row and
                            int(end_row) == row and
                            _col_number(last_col) == _col_number(first_col) + 1
                        ):
                            return last_col
                element.clear()
    except (ET.ParseError, KeyError, OSError) as exc:
        raise WorkbookPreviewError("Não foi possível analisar as colunas mescladas.") from exc
    return anchor


def _read_name_cells(book: zipfile.ZipFile, candidate: WorksheetHint):
    cols = [item.column for item in candidate.fields if item.field == "employee"]
    if len(cols) != 1:
        raise WorkbookPreviewError("Cabeçalho de funcionários ambíguo.")
    name_cells = []
    stopped_early = False
    path = f"xl/worksheets/sheet{candidate.technical_id}.xml"
    source_col = _merged_name_column(book, path, cols[0], candidate.header_row)
    try:
        with book.open(path) as stream:
            for event, el in ET.iterparse(stream, events=("start", "end")):
                if event == "start" and el.tag == NS + "row":
                    row_no = el.get("r", "")
                    if row_no.isdecimal() and int(row_no) > MAX_SOURCE_ROWS:
                        stopped_early = True
                        break
                if event != "end":
                    continue
                if el.tag == NS + "c":
                    match = COL_PATTERN.fullmatch(el.get("r", ""))
                    if not match:
                        el.clear()
                        continue
                    column, num = match.groups()
                    row = int(num)
                    if column != source_col or row <= candidate.header_row:
                        el.clear()
                        continue
                    if row > MAX_SOURCE_ROWS:
                        stopped_early = True
                        break
                    if el.find(NS + "f") is not None or el.get("t") == "e":
                        name_cells.append((row, "invalid", None))
                    elif el.get("t") == "s":
                        cached = el.find(NS + "v")
                        idx = cached.text if cached is not None else ""
                        if idx and idx.isdecimal():
                            name_cells.append((row, "shared", idx))
                    elif el.get("t") == "inlineStr":
                        value = _inline_text(el)
                        if value.strip():
                            name_cells.append((row, "inline", value))
                    else:
                        # Números, fórmulas e resultados cacheados não são nomes confiáveis.
                        cached = el.find(NS + "v")
                        if cached is not None and (cached.text or "").strip():
                            name_cells.append((row, "invalid", None))
                    el.clear()
                elif el.tag == NS + "row":
                    el.clear()
                if len(name_cells) > MAX_IDENTITIES:
                    stopped_early = True
                    break
    except (ET.ParseError, KeyError, OSError) as exc:
        raise WorkbookPreviewError("Não foi possível analisar as identificações.") from exc
    return name_cells[:MAX_IDENTITIES], stopped_early, source_col


def _required_shared(book: zipfile.ZipFile, indices: set[str]) -> dict[str, str]:
    if not indices:
        return {}
    result: dict[str, str] = {}
    if "xl/sharedStrings.xml" not in book.namelist():
        return result
    count = 0
    try:
        with book.open("xl/sharedStrings.xml") as stream:
            for _, el in ET.iterparse(stream, events=("end",)):
                if el.tag != NS + "si":
                    continue
                if str(count) in indices:
                    chunks = []
                    remaining = 122
                    for node in el.iter(NS + "t"):
                        value = (node.text or "")[:remaining]
                        chunks.append(value)
                        remaining -= len(value)
                        if remaining <= 0:
                            break
                    result[str(count)] = "".join(chunks)
                count += 1
                el.clear()
    except (ET.ParseError, OSError) as exc:
        raise WorkbookPreviewError("Não foi possível analisar as identificações.") from exc
    return result


def _extract_names(source: bytes, candidate: WorksheetHint):
    with zipfile.ZipFile(io.BytesIO(source)) as book:
        name_cells, limited, source_col = _read_name_cells(book, candidate)
        needed = {value for _, kind, value in name_cells if kind == "shared"}
        shared = _required_shared(book, needed)
    names = []
    for row, kind, value in name_cells:
        if kind == "invalid":
            names.append(TransientName(row, "", True))
        else:
            name = shared.get(value, "") if kind == "shared" else value or ""
            normalized = _key(name)
            names.append(TransientName(row, normalized, not bool(normalized)))
    return names, limited, source_col


def simulate_v2_link(
    source: bytes,
    mapping: MappingPreview,
    employees: list[V2EmployeeRef],
) -> V2LinkPreview:
    """Calcula apenas a relação provisória; nunca consulta/coleta pagamentos."""
    if mapping.limited or len(mapping.candidates) != 1:
        raise WorkbookPreviewError("O mapeamento deve conter um único resumo confiável.")
    if not 0 <= len(employees) <= MAX_EMPLOYEES_IN_SCOPE:
        raise WorkbookPreviewError("Muitos funcionários no escopo.")
    candidate = mapping.candidates[0]
    raw_names, limited, source_col = _extract_names(source, candidate)
    index = defaultdict(list)
    for employee in employees:
        key = _key(employee.full_name)
        if key:
            index[key].append(employee)
    repeated = Counter(row.identity for row in raw_names if row.identity)
    result = []
    for item in raw_names:
        if item.invalid:
            state = "invalid_source"
        elif repeated[item.identity] > 1:
            state = "duplicate_source"
        else:
            matches = index.get(item.identity, [])
            if not matches:
                state = "unmatched"
            elif len(matches) > 1:
                state = "ambiguous"
            elif not matches[0].active:
                state = "inactive"
            elif not matches[0].has_v2_record:
                state = "legacy_only"
            else:
                state = "v2_match"
        result.append(V2MatchRow(item.row_number, state))
    statuses = Counter(row.status for row in result)
    return V2LinkPreview(
        source_hash_prefix=mapping.sha256_prefix,
        data_column=source_col,
        examined=len(result),
        counts=tuple((code, statuses.get(code, 0)) for code in STATUS_DESCRIPTIONS),
        sample=tuple(result[:MAX_VISIBLE_ROWS]),
        limited=limited or len(result) > MAX_VISIBLE_ROWS,
    )
