"""Pré-análise estrutural de arquivos XLSX sem ler nomes nem persistir dados.

Nenhum valor de célula, nome de trabalhador ou dado financeiro sai desta função.
A análise não calcula folha, não importa jornadas e não executa pagamentos.
"""
from __future__ import annotations

import hashlib
import io
import re
import zipfile
from dataclasses import dataclass
from xml.etree import ElementTree as ET

MAX_XLSX_BYTES = 12 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 160 * 1024 * 1024
MAX_ENTRY_BYTES = 64 * 1024 * 1024
MAX_ENTRIES = 2000
MAX_CELLS = 4_000_000
XML_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
SHEET_PART = re.compile(r"^xl/worksheets/sheet[1-9][0-9]*\.xml$")
EXTERNAL_PART = re.compile(r"^xl/externalLinks/externalLink[1-9][0-9]*\.xml$")


class WorkbookPreviewError(ValueError):
    """Arquivo rejeitado sem expor informações internas ao usuário."""


@dataclass(frozen=True)
class WorkbookPreflight:
    sha256_prefix: str
    sheets: int
    visible: int
    hidden: int
    formulas: int
    formula_errors: int
    broken_references: int
    cells_examined: int
    external_links: int
    source_bytes: int
    warnings: tuple[str, ...]

    @property
    def requires_manual_review(self) -> bool:
        return bool(self.formula_errors or self.broken_references or self.external_links)


def _read_sheet(stream) -> tuple[int, int, int, int]:
    cells = formulas = error_cells = broken_refs = 0
    try:
        parser = ET.iterparse(stream, events=("start", "end"))
        root = None
        for event, element in parser:
            if event == "start":
                if root is None:
                    root = element
                continue
            if element.tag == XML_NS + "c":
                cells += 1
                if cells > MAX_CELLS:
                    raise WorkbookPreviewError("Limite de células excedido.")
                formula = element.find(XML_NS + "f")
                cached = element.find(XML_NS + "v")
                if formula is not None:
                    formulas += 1
                is_error = element.get("t") == "e"
                if is_error:
                    error_cells += 1
                if (formula is not None and "#REF!" in (formula.text or "")) or (
                    is_error and cached is not None and (cached.text or "") == "#REF!"
                ):
                    broken_refs += 1
                element.clear()
            elif element.tag == XML_NS + "row":
                element.clear()
                if root is not None:
                    root.clear()
    except ET.ParseError as error:
        raise WorkbookPreviewError("XML de planilha inválido.") from error
    return cells, formulas, error_cells, broken_refs


def inspect_xlsx(source: bytes) -> WorkbookPreflight:
    """Retorna somente metadados agregados; rejeita anexos maliciosos."""
    if not source or len(source) > MAX_XLSX_BYTES:
        raise WorkbookPreviewError("Arquivo vazio ou maior que 12 MiB.")
    if not zipfile.is_zipfile(io.BytesIO(source)):
        raise WorkbookPreviewError("O arquivo não é um XLSX válido.")

    try:
        with zipfile.ZipFile(io.BytesIO(source)) as book:
            infos = book.infolist()
            if len(infos) > MAX_ENTRIES:
                raise WorkbookPreviewError("O arquivo contém entradas demais.")
            total = 0
            names = set()
            for entry in infos:
                name = entry.filename
                if (
                    name.startswith("/") or "\\" in name or
                    ".." in name.split("/") or entry.flag_bits & 0x1
                ):
                    raise WorkbookPreviewError("Estrutura ZIP não permitida.")
                if entry.file_size > MAX_ENTRY_BYTES:
                    raise WorkbookPreviewError("Uma entrada excede o limite de tamanho.")
                total += entry.file_size
                if total > MAX_UNCOMPRESSED_BYTES:
                    raise WorkbookPreviewError("O conteúdo descompactado é muito grande.")
                names.add(name)

            if {"xl/workbook.xml", "[Content_Types].xml"} - names:
                raise WorkbookPreviewError("Estrutura XLSX incompleta.")
            if any(
                "/embeddings/" in "/" + name.lower() or
                "vbaproject" in name.lower() or "/activex/" in "/" + name.lower()
                for name in names
            ):
                raise WorkbookPreviewError("Anexos executáveis/embutidos não permitidos.")

            try:
                workbook = ET.fromstring(book.read("xl/workbook.xml"))
            except ET.ParseError as error:
                raise WorkbookPreviewError("Metadados XLSX inválidos.") from error
            sheets = list(workbook.iter(XML_NS + "sheet"))
            if not sheets:
                raise WorkbookPreviewError("Não foram encontradas abas.")
            visible = sum(sheet.get("state", "visible") == "visible" for sheet in sheets)
            hidden = len(sheets) - visible

            formula_count = error_cells = ref_count = cell_count = 0
            sheet_parts = sorted(name for name in names if SHEET_PART.fullmatch(name))
            if len(sheet_parts) < len(sheets):
                raise WorkbookPreviewError("Algumas abas não possuem XML correspondente.")
            for name in sheet_parts:
                with book.open(name) as data:
                    cells, formulas, errors, broken = _read_sheet(data)
                cell_count += cells
                formula_count += formulas
                error_cells += errors
                ref_count += broken
                if cell_count > MAX_CELLS:
                    raise WorkbookPreviewError("Limite de células excedido.")
            external_links = sum(bool(EXTERNAL_PART.fullmatch(name)) for name in names)
    except (zipfile.BadZipFile, OSError, RuntimeError, EOFError) as error:
        raise WorkbookPreviewError("Falha ao interpretar o XLSX.") from error

    warnings = []
    if hidden:
        warnings.append("Existem abas ocultas que exigem conferência.")
    if external_links:
        warnings.append("Existem vínculos com planilhas externas.")
    if ref_count:
        warnings.append("Foram detectadas referências quebradas (#REF!).")
    if error_cells:
        warnings.append("Existem células com erros de cálculo.")
    warnings.append("Pré-análise apenas estrutural: nenhum registro ou valor financeiro foi importado.")
    return WorkbookPreflight(
        sha256_prefix=hashlib.sha256(source).hexdigest()[:16],
        sheets=len(sheets),
        visible=visible,
        hidden=hidden,
        formulas=formula_count,
        formula_errors=error_cells,
        broken_references=ref_count,
        cells_examined=cell_count,
        external_links=external_links,
        source_bytes=len(source),
        warnings=tuple(warnings),
    )
