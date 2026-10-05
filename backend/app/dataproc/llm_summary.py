"""Utility for generating asynchronous dataset summaries via local LLM."""

import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd
import requests

DEFAULT_OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434/api/generate')
DEFAULT_OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'gpt-oss:120b-cloud')
# Production has no Ollama to call; switching this off skips the background
# request and tells the UI to hide the Summary tab.
SUMMARY_ENABLED = os.getenv('SUMMARY_ENABLED', 'true').strip().lower() not in ('false', '0', 'no')
SUMMARY_FILENAME_TEMPLATE = "{session_id}_summary.json"
SUMMARY_FIELD = 'llm_summary'


def _sanitize(text: str) -> str:
    """Strip non-ASCII characters to keep payload lightweight."""
    if not text:
        return ''
    return text.encode('ascii', 'ignore').decode('ascii')


def _compile_dataset_brief(df: pd.DataFrame, tree_order: List[str], value_column: Optional[str], aggregation_mode: str) -> str:
    """Create a compact textual briefing for the LLM prompt."""
    row_count = len(df)
    col_names = df.columns.tolist()
    first_columns = col_names[:12]

    column_summaries = []
    for col in first_columns:
        series = df[col].dropna()
        dtype = str(series.dtype)
        unique_count = int(series.nunique()) if not series.empty else 0
        if not series.empty and pd.api.types.is_numeric_dtype(series):
            describe = series.describe()
            stats = f"mean={describe['mean']:.2f}, min={describe['min']:.2f}, max={describe['max']:.2f}"
        else:
            top_values = ', '.join(_sanitize(str(val))[:30] for val in series.head(3)) if not series.empty else 'n/a'
            stats = f"top_values={top_values}"
        column_summaries.append(f"- {col} ({dtype}, unique={unique_count}): {stats}")

    sample_csv = df.head(5).to_csv(index=False)

    briefing = [
        f"Total rows: {row_count}",
        f"Column count: {len(col_names)}",
        f"Hierarchy columns: {', '.join(tree_order)}",
        f"Aggregation mode: {aggregation_mode}",
        f"Value column: {value_column or 'COUNT'}",
        f"First columns: {', '.join(first_columns)}",
        "Column snapshots:",
        '\n'.join(column_summaries),
        "Sample rows (CSV):",
        sample_csv
    ]
    return '\n'.join(_sanitize(part) for part in briefing)


def _build_prompt(chart_name: str, briefing: str) -> str:
    """Craft the user prompt for the model."""
    return (
        "You are a senior data analyst. Review the dataset details below and write a plain-text "
        f"summary for stakeholders. Mention cohort sizes, notable trends, potential outliers, and "
        f"data quality concerns. Keep the tone professional and actionable. The summary must stay "
        f"between 50 and 200 words.\n\nDataset: {chart_name}\n\n{briefing}\n\nSummary:"
    )


def _persist_summary(summary_path: Path, status: str, summary_text: Optional[str]) -> None:
    """Write summary status to disk for later retrieval."""
    payload = {
        'status': status,
        'summary': summary_text,
        'generated_at': datetime.utcnow().isoformat() + 'Z'
    }
    with summary_path.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2)


def _update_metadata(metadata_path: Path, summary_path: Path, status: str) -> None:
    """Patch the sunburst metadata file with summary status."""
    if not metadata_path.exists():
        return

    try:
        with metadata_path.open('r', encoding='utf-8') as handle:
            data = json.load(handle)
    except json.JSONDecodeError:
        return

    data[SUMMARY_FIELD] = {
        'status': status,
        'summary_file': summary_path.name
    }

    with metadata_path.open('w', encoding='utf-8') as handle:
        json.dump(data, handle, indent=2)


def _call_model(prompt: str, model: str, url: str) -> str:
    """Invoke the Ollama endpoint and return the generated summary."""
    payload = {
        'model': model,
        'system': (
            "You analyze tabular data and return concise English summaries. "
            "Output plain text only, no lists or markdown. \n"
            "Keep word count between 50 and 200 words."
        ),
        'prompt': prompt,
        'stream': False
    }

    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    summary_text = data.get('response') or data.get('summary')
    if not summary_text:
        raise ValueError('LLM response missing summary text')
    return summary_text.strip()


def _generate_summary(df: pd.DataFrame,
                      session_id: str,
                      chart_name: str,
                      tree_order: List[str],
                      value_column: Optional[str],
                      aggregation_mode: str,
                      data_dir: Path,
                      metadata_path: Path,
                      model: str,
                      url: str) -> None:
    summary_path = data_dir / SUMMARY_FILENAME_TEMPLATE.format(session_id=session_id)
    try:
        briefing = _compile_dataset_brief(df, tree_order, value_column, aggregation_mode)
        prompt = _build_prompt(chart_name, briefing)
        summary_text = _call_model(prompt, model, url)
        _persist_summary(summary_path, 'ready', summary_text)
        _update_metadata(metadata_path, summary_path, 'ready')
    except Exception as exc:  # noqa: BLE001 - broad to ensure background thread never crashes silently
        fallback = f"Summary unavailable: {exc}"
        _persist_summary(summary_path, 'error', fallback)
        _update_metadata(metadata_path, summary_path, 'error')


def schedule_dataframe_summary(df: pd.DataFrame,
                               session_id: str,
                               chart_name: str,
                               tree_order: List[str],
                               value_column: Optional[str],
                               aggregation_mode: str,
                               data_dir: Path,
                               metadata_path: Path,
                               model: Optional[str] = None,
                               url: Optional[str] = None) -> None:
    """Spawn a daemon thread to generate a dataset summary with the configured LLM."""
    if not SUMMARY_ENABLED or df is None or df.empty:
        return

    resolved_model = model or DEFAULT_OLLAMA_MODEL
    resolved_url = url or DEFAULT_OLLAMA_URL
    summary_path = data_dir / SUMMARY_FILENAME_TEMPLATE.format(session_id=session_id)

    # Mark as pending so clients can poll before generation completes.
    _persist_summary(summary_path, 'pending', None)
    _update_metadata(metadata_path, summary_path, 'pending')

    thread = threading.Thread(
        target=_generate_summary,
        args=(df.copy(), session_id, chart_name, tree_order, value_column, aggregation_mode, data_dir, metadata_path, resolved_model, resolved_url),
        name=f"summary-{session_id}",
        daemon=True
    )
    thread.start()
