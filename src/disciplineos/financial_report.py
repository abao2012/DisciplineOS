from __future__ import annotations

import re
import zipfile
from xml.etree import ElementTree
from pathlib import Path

from .models import FinancialReportSummary


METRIC_PATTERNS = {
    "revenue": r"(?:revenue|sales|营业收入|收入)[^\n。.;；]{0,40}",
    "profit": r"(?:net profit|profit|净利润|利润)[^\n。.;；]{0,40}",
    "gross_margin": r"(?:gross margin|毛利率)[^\n。.;；]{0,40}",
    "cash_flow": r"(?:cash flow|operating cash|现金流|经营现金)[^\n。.;；]{0,50}",
    "guidance": r"(?:guidance|outlook|指引|展望)[^\n。.;；]{0,80}",
}


def summarize_financial_report(
    path: str | Path,
    symbol: str,
    period: str,
    material_type: str = "financial_report",
    ai_online_search: bool = False,
) -> FinancialReportSummary:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Financial report not found: {source}")
    text = _read_document_text(source)
    return summarize_financial_report_text(
        text=text,
        symbol=symbol,
        period=period,
        source=str(source),
        material_type=material_type,
        ai_online_search=ai_online_search,
    )


def summarize_financial_report_text(
    text: str,
    symbol: str,
    period: str,
    source: str = "inline",
    material_type: str = "financial_report",
    ai_online_search: bool = False,
) -> FinancialReportSummary:
    metrics = {
        key: _first_match(pattern, text)
        for key, pattern in METRIC_PATTERNS.items()
    }
    evidence = [value for value in metrics.values() if value]
    if not evidence:
        evidence = ["No key financial metric phrase was detected."]
    local_analysis = build_local_analysis(evidence, metrics)

    return FinancialReportSummary(
        symbol=symbol.upper(),
        period=period,
        source=source,
        material_type=material_type,
        ai_online_search=ai_online_search,
        analysis_mode="local_rules",
        ai_status="not_requested",
        revenue=metrics["revenue"],
        profit=metrics["profit"],
        gross_margin=metrics["gross_margin"],
        cash_flow=metrics["cash_flow"],
        guidance=metrics["guidance"],
        evidence_summary=evidence,
        key_insights=local_analysis["key_insights"],
        positive_factors=local_analysis["positive_factors"],
        negative_factors=local_analysis["negative_factors"],
        risk_flags=local_analysis["risk_flags"],
        discipline_suggestions=local_analysis["discipline_suggestions"],
        card_suggestions=local_analysis["card_suggestions"],
    )


def report_to_evidence(summary: FinancialReportSummary) -> list[str]:
    return [
        f"{summary.symbol} {summary.period}: {item}"
        for item in summary.evidence_summary
    ]


def read_document_text(source: str | Path) -> str:
    return _read_document_text(Path(source))


def apply_analysis_payload(
    summary: FinancialReportSummary,
    payload: dict,
    *,
    mode: str,
    ai_status: str = "pass",
    ai_error: str = "",
) -> FinancialReportSummary:
    summary.analysis_mode = mode
    summary.ai_status = ai_status
    summary.ai_error = ai_error
    summary.key_insights = _string_list(payload.get("key_insights")) or summary.key_insights
    summary.positive_factors = _string_list(payload.get("positive_factors")) or summary.positive_factors
    summary.negative_factors = _string_list(payload.get("negative_factors")) or summary.negative_factors
    summary.risk_flags = _string_list(payload.get("risk_flags")) or summary.risk_flags
    summary.discipline_suggestions = _string_list(payload.get("discipline_suggestions")) or summary.discipline_suggestions
    summary.card_suggestions = _card_suggestions(payload.get("card_suggestions")) or summary.card_suggestions
    summary.evidence_summary = _string_list(
        payload.get("evidence_summary")
    ) or summary.evidence_summary
    return summary


def build_local_analysis(evidence: list[str], metrics: dict[str, str]) -> dict:
    joined = " ".join(evidence).lower()
    positives = []
    negatives = []
    risks = []
    if any(word in joined for word in ("increase", "improve", "growth", "positive", "增长", "提升", "改善", "转正")):
        positives.append("Detected improving language in the material.")
    if any(word in joined for word in ("decline", "drop", "decrease", "negative", "下滑", "下降", "转负", "承压")):
        negatives.append("Detected weakening or pressure language in the material.")
    if not metrics.get("cash_flow"):
        risks.append("Cash-flow evidence was not detected; verify cash conversion manually.")
    if not metrics.get("guidance"):
        risks.append("Forward-looking guidance was not detected; avoid raising exposure without new evidence.")
    if evidence == ["No key financial metric phrase was detected."]:
        risks.append("No core metric phrase was detected; the material may need AI/manual review.")
    return {
        "key_insights": evidence[:5],
        "positive_factors": positives,
        "negative_factors": negatives,
        "risk_flags": risks,
        "discipline_suggestions": [
            "Use this material as evidence only after checking whether it changes the original thesis.",
            "Do not raise the position limit unless growth, profit quality, and cash flow evidence improve together.",
            "Lower the position limit if profit quality weakens, cash flow deteriorates, or guidance is cut.",
        ],
        "card_suggestions": {
            "why_buy": evidence[:2],
            "raise_position": [
                "Growth, profit quality, cash flow, and guidance improve together."
            ],
            "lower_position": [
                "Core financial evidence weakens or becomes inconsistent with the thesis."
            ],
            "reduce_when": [
                "New evidence shows thesis deterioration, cash-flow pressure, or position risk."
            ],
        },
    }


def _read_document_text(source: Path) -> str:
    suffix = source.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError(
                "PDF reading requires the pypdf package. Run pip install -e . first."
            ) from exc
        reader = PdfReader(str(source))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        return _read_docx_text(source)
    if suffix == ".doc":
        raise RuntimeError(
            "Legacy .doc binary files are not supported yet. Save the file as .docx, PDF, Markdown, or TXT first."
        )
    return source.read_text(encoding="utf-8-sig")


def _read_docx_text(source: Path) -> str:
    try:
        with zipfile.ZipFile(source) as archive:
            document_xml = archive.read("word/document.xml")
    except KeyError as exc:
        raise RuntimeError(f"DOCX document is missing word/document.xml: {source}") from exc
    except zipfile.BadZipFile as exc:
        raise RuntimeError(f"DOCX document is not a valid zip package: {source}") from exc

    root = ElementTree.fromstring(document_xml)
    paragraphs: list[str] = []
    for paragraph in root.iter(_w_tag("p")):
        text = _docx_paragraph_text(paragraph)
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def _docx_paragraph_text(paragraph: ElementTree.Element) -> str:
    parts: list[str] = []
    for node in paragraph.iter():
        if node.tag == _w_tag("t") and node.text:
            parts.append(node.text)
        elif node.tag == _w_tag("tab"):
            parts.append("\t")
        elif node.tag in {_w_tag("br"), _w_tag("cr")}:
            parts.append("\n")
    return "".join(parts).strip()


def _w_tag(name: str) -> str:
    return f"{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}{name}"


def _first_match(pattern: str, text: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return ""
    return " ".join(match.group(0).split())


def _string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _card_suggestions(value: object) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key): _string_list(items)
        for key, items in value.items()
        if _string_list(items)
    }
