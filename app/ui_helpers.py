"""UI helper utilities."""
from __future__ import annotations

import math

import streamlit as st


def format_currency(value: float | int | None) -> str:
    """Format a numeric value as USD currency."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return f"${value:,.2f}"


def safe_metric(label: str, value: float | int | None, help_text: str | None = None) -> None:
    """Render a metric safely even when values are missing."""
    display_value = value if value is not None else 0
    st.metric(label, display_value, help=help_text)


def empty_state(message: str) -> None:
    """Display a friendly empty state message."""
    st.info(message)
