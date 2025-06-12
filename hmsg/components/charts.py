"""Chart components for data visualization."""

import reflex as rx
import plotly.graph_objects as go


def plotly_chart(figure_data: go.Figure) -> rx.Component:
    """Reusable Plotly chart component with consistent configuration."""
    return rx.plotly(
        data=figure_data,
        # Disable modebar to remove Plotly logo and toolbar
        config={
            "displayModeBar": False,
            "staticPlot": False,
            "doubleClick": False,
            "showTips": False,
            "displaylogo": False,
            "toImageButtonOptions": {
                "format": "png", 
                "filename": "chart", 
                "height": 500, 
                "width": 700, 
                "scale": 1
            }
        }
    )


def heart_rate_chart(chart_data: go.Figure) -> rx.Component:
    """Heart rate chart component."""
    return rx.card(
        plotly_chart(chart_data),
        size="3",
        width="100%",
        height="400px",
    )


def age_distribution_chart(chart_data: go.Figure) -> rx.Component:
    """Age distribution chart component."""
    return rx.card(
        plotly_chart(chart_data),
        size="3",
        width="100%",
        height="400px",
    ) 