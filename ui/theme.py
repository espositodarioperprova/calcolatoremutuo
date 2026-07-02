"""Global Plotly chart theme and colour palette."""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

#: Seven-colour palette used across all charts and the pie chart marker.
PALETTE: list[str] = [
    "#3b82f6",  # blue
    "#10b981",  # emerald
    "#f59e0b",  # amber
    "#ef4444",  # red
    "#8b5cf6",  # violet
    "#06b6d4",  # cyan
    "#f97316",  # orange
]


def apply_theme() -> None:
    """Register and activate the application Plotly template.

    Call this once at app startup before any figures are created.
    """
    pio.templates["_cal"] = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="white",
            plot_bgcolor="#f8fafc",
            font_family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            font_color="#374151",
            font_size=12,
            colorway=PALETTE,
            xaxis_gridcolor="#e2e8f0",
            xaxis_linecolor="#cbd5e1",
            xaxis_zerolinecolor="#e2e8f0",
            yaxis_gridcolor="#e2e8f0",
            yaxis_linecolor="#cbd5e1",
            yaxis_zerolinecolor="#e2e8f0",
        )
    )
    pio.templates.default = "plotly+_cal"
