"""Mapeamento estrutural dos cabeçalhos de planilhas legadas, sem dados pessoais.

Nunca retorna texto fornecido pelo XLSX, nomes de abas ou valores de células.
As colunas monetárias são marcadas como ambíguas e NÃO são usadas para pagamentos.
"""
from __future__ import annotations

import io
import re
import unicodedata
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from xml.etree import ElementTree as ET

from app.payment_import import WorkbookPreflight, WorkbookPreviewError, inspect_xlsx

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
PART_RE = re.compile(r"^xl/worksheets/sheet([1-9][0-9]*)\.xml$")
CELL_RE = re.compile(r"^([A-Z]{1,3})([1-9][0-9]*)$")
MAX_HEADER_ROWS = 20
MAX_SHEETS = 250
FIELDS = {
    "employee": "Funcionário",
    "position": "Função/cargo",
    "days": "Dias trabalhados",
    "worked_hours": "Horas trabalhadas",
    "daily": "Diária",
    "hour_unit": "Valor unitário por hora (rótulo original)",
    "total": "Valor total (rótulo original)",
    "sunday_holiday_hours": "Horas de domingo/feriado",
    "sunday_holiday": "Domingos e feriados",
    "holiday_hour_unit": "Valor unitário hora dom./feriado (rótulo original)",
    "sunday_holiday_total": "Total de domingo/feriado",
    "hours_payable_total": "Total a pagar por horas",
    "additional": "Adicional (rótulo original)",
    "discount": "Descontos",
    "total_payable": "Total a pagar (rótulo original)",
    "payment_type": "Tipo (rótulo original)",
    "pix": "Campo PIX (sem revelar a chave)",
}
SENSITIVE_FIELDS = frozenset({"daily", "hour_unit", "holiday_hour_unit", "total", "sunday_holiday_total", "hours_payable_total", "additional", "discount", "total_payable", "payment_type", "pix"})


def _normalize(source: str) -> str:
    source = unicodedata.normalize("NFKD", source[:128])
    source = "".join(ch for ch in source if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", source.upper())).strip()


def _recognize(source: str) -> str | None:
    """Reconhece apenas rótulos de campos, nunca conteúdos de célula."""
    name = _normalize(source)
    if not name or len(name) > 54:
        return None
    exact = {
        "NOME": "employee",
        "FUNCIONARIO": "employee",
        "FUNCIONARIOS": "employee",
        "NOME DO FUNCIONARIO": "employee",
        "FUNCAO": "position",
        "CARGO": "position",
        "FUNCAO CARGO": "position",
        "DIAS": "days",
        "DIAS TRAB": "days",
        "DIAS TRABALHADOS": "days",
        "HS TRAB": "worked_hours",
        "HS TRABALHADAS": "worked_hours",
        "HORAS": "worked_hours",
        "HORAS TRABALHADAS": "worked_hours",
        "DIARIA": "daily",
        "VALOR DIARIA": "daily",
        "VALOR DA DIARIA": "daily",
        "VALOR UNIT DA HS": "hour_unit",
        "VALOR UNIT DA HORA": "hour_unit",
        "VALOR": "total",
        "VALOR TOTAL": "total",
        "VALOR BRUTO": "total",
        "HORAS DOM FER": "sunday_holiday_hours",
        "HS TRAB DOM FERIADO": "sunday_holiday_hours",
        "VALOR UNIT DA HS DOM E FERIADO": "holiday_hour_unit",
        "DOM E FERIADO": "sunday_holiday",
        "DOMINGO E FERIADO": "sunday_holiday",
        "TOTAL DOM FER": "sunday_holiday_total",
        "TOTAL HS DOM FERIADO": "sunday_holiday_total",
        "TOTAL A PAGAR HORAS": "hours_payable_total",
        "ADICIONAL": "additional",
        "ADICIONAIS": "additional",
        "DESCONTO": "discount",
        "DESCONTOS": "discount",
        "TOTAL": "total",
        "TOTAL A PAGAR": "total_payable",
        "TIPO": "payment_type",
        "PIX": "pix",
        "CHAVE PIX": "pix",
    }
    return exact.get(name)


@dataclass(frozen=True)
class ColumnHint:
    field: str
    label: str
    column: str
    sensitive: bool


@dataclass(frozen=True)
class WorksheetHint:
    technical_id: int
    header_row: int
    fields: tuple[ColumnHint, ...]
    ambiguous: tuple[str, ...]

    @property
    def can_import(self) -> bool:
        return False  # Explicitamente sem persistência/migração financeira.


@dataclass(frozen=True)
class MappingPreview:
    sha256_prefix: str
    candidates: tuple[WorksheetHint, ...]
    inspected_sheet_parts: int
    limited: bool
    warnings: tuple[str, ...]

    @property
    def requires_manual_review(self) -> bool:
        return True


def _text_fragments(element):
    total = 0
    parts = []
    for node in element.iter(NS + "t"):
        chunk = (node.text or "")[: max(0, 128 - total)]
        parts.append(chunk)
        total += len(chunk)
        if total >= 128:
            break
    return "".join(parts)


def _read_label_ids(book: zipfile.ZipFile) -> dict[str, str]:
    """Consome sharedStrings sem armazenar valores; retém só índice -> enum conhecido."""
    if "xl/sharedStrings.xml" not in book.namelist():
        return {}
    result: dict[str, str] = {}
    index = 0
    try:
        with book.open("xl/sharedStrings.xml") as stream:
            for _, element in ET.iterparse(stream, events=("end",)):
                if element.tag != NS + "si":
                    continue
                known = _recognize(_text_fragments(element))
                if known is not None:
                    result[str(index)] = known
                index += 1
                element.clear()
    except ET.ParseError as exc:
        raise WorkbookPreviewError("Tabela de rótulos XLSX inválida.") from exc
    return result


def _labels_in_header_rows(stream, string_labels: dict[str, str]):
    """Lê somente até MAX_HEADER_ROWS e devolve enum de campos e coordenadas."""
    rows: dict[int, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    try:
        for event, element in ET.iterparse(stream, events=("start", "end")):
            if event == "start" and element.tag == NS + "row":
                row = element.get("r", "0")
                if row.isdecimal() and int(row) > MAX_HEADER_ROWS:
                    break
            if event != "end":
                continue
            if element.tag == NS + "c":
                address = CELL_RE.fullmatch(element.get("r", ""))
                if not address:
                    element.clear()
                    continue
                column, row_txt = address.groups()
                row = int(row_txt)
                if row > MAX_HEADER_ROWS or element.find(NS + "f") is not None:
                    element.clear()
                    continue
                field = None
                if element.get("t") == "s":
                    value = element.find(NS + "v")
                    if value is not None:
                        field = string_labels.get(value.text or "")
                elif element.get("t") == "inlineStr":
                    inline = element.find(NS + "is")
                    if inline is not None:
                        field = _recognize(_text_fragments(inline))
                if field is not None:
                    rows[row][field].add(column)
                element.clear()
            elif element.tag == NS + "row":
                element.clear()
    except ET.ParseError as exc:
        raise WorkbookPreviewError("XML de cabeçalhos XLSX inválido.") from exc
    return rows


def inspect_payment_mapping(source: bytes, preflight: WorkbookPreflight | None = None) -> MappingPreview:
    """Identifica possíveis linhas de cabeçalho, sem ler linhas de trabalhadores.

    Requer validação ZIP do pré-analisador, incluindo limite de tamanho/partes e
    rejeição de macros. A origem do pré-analisador é a mesma fonte bytes.
    """
    inspected = preflight or inspect_xlsx(source)
    # Nunca aceita uma pré-análise fornecida por entrada do usuário: só por chamada Python.
    candidates: list[WorksheetHint] = []
    with zipfile.ZipFile(io.BytesIO(source)) as book:
        names = [
            (int(match.group(1)), name)
            for name in book.namelist()
            if (match := PART_RE.fullmatch(name))
        ]
        names.sort()
        string_labels = _read_label_ids(book)
        for sheet_id, path in names[:MAX_SHEETS]:
            with book.open(path) as stream:
                rows = _labels_in_header_rows(stream, string_labels)
            for row_number, labels in rows.items():
                unique = set(labels)
                if not ("employee" in unique and bool({"total", "total_payable"} & unique) and len(unique) >= 6):
                    continue
                mapped = tuple(
                    ColumnHint(field=f, label=FIELDS[f], column=col, sensitive=f in SENSITIVE_FIELDS)
                    for f in FIELDS for col in sorted(labels.get(f, ()))
                )
                ambiguous = tuple(FIELDS[f] for f, cols in labels.items() if len(cols) > 1)
                candidates.append(
                    WorksheetHint(
                        technical_id=sheet_id,
                        header_row=row_number,
                        fields=mapped,
                        ambiguous=tuple(sorted(ambiguous)),
                    )
                )
    candidates.sort(key=lambda item: (-len({c.field for c in item.fields}), item.technical_id, item.header_row))
    warnings = ["Nenhuma linha de trabalhador, valor financeiro, CPF ou chave PIX foi exibida ou importada."]
    if inspected.requires_manual_review:
        warnings.append("A planilha contém riscos estruturais e exige validação contábil.")
    if not candidates:
        warnings.append("Nenhum cabeçalho confiável encontrado: mapeamento manual obrigatório.")
    if any(candidate.ambiguous for candidate in candidates):
        warnings.append("Há rótulos repetidos; suas finalidades não foram inferidas.")
    if any(
        len({"total", "sunday_holiday_total", "hours_payable_total", "total_payable"} &
            {item.field for item in candidate.fields}) > 1
        for candidate in candidates
    ):
        warnings.append("Existem totalizadores distintos: nenhuma rubrica financeira foi conciliada.")
    if len(names) > MAX_SHEETS:
        warnings.append("A varredura de cabeçalhos foi limitada; nenhuma migração foi realizada.")
    return MappingPreview(
        sha256_prefix=inspected.sha256_prefix,
        candidates=tuple(candidates[:10]),
        inspected_sheet_parts=min(len(names), MAX_SHEETS),
        limited=len(names) > MAX_SHEETS or len(candidates) > 10,
        warnings=tuple(warnings),
    )
