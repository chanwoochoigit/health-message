"""Layout components for consistent page structure."""

import reflex as rx
from .sidebar import sidebar


def page_layout(content: rx.Component, active_page: str = "dashboard") -> rx.Component:
    """Standard page layout with sidebar and main content area."""
    return rx.box(
        sidebar(active_page),
        rx.box(
            content,
            margin_left="250px",  # Account for sidebar width
            padding="8",
            bg="#F9FAFB",  # Light gray background
            min_height="100vh",
        ),
    )


def page_header(title: str, date_range: str = "Jan 20, 2022 - Feb 09, 2022") -> rx.Component:
    """Standard page header with title and date range."""
    return rx.vstack(
        rx.box(height="5px"),  
        rx.hstack(
        rx.box(width="10px"),  
        rx.heading(title, size="8", weight="bold", color="#111827"),
        rx.spacer(),
        rx.hstack(
            rx.icon("calendar", size=16, color="#6B7280"),
            rx.text(date_range, color="#6B7280", size="3", weight="medium"),
            spacing="2",
            align="center",
        ),
        justify="between",
        align="center",
        width="100%",
        padding_bottom="8",
    )
    )

def stats_grid(stats_cards: list) -> rx.Component:
    """Grid layout for statistics cards."""
    return rx.hstack(
        *stats_cards,
        spacing="6",
        width="100%",
    )


def charts_grid(charts: list) -> rx.Component:
    """Grid layout for charts."""
    return rx.hstack(
        *charts,
        spacing="6",
        width="100%",
        align="start",
    ) 