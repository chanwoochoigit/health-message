"""Reusable card components."""

import reflex as rx


def stat_card(title: str, value: str, icon: str, icon_color: str = "#3B82F6") -> rx.Component:
    """Enhanced statistics card component using built-in rx.card."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=24, color=icon_color),
                    padding="3",
                    border_radius="8px",
                    bg=f"rgba({int(icon_color[1:3], 16)}, {int(icon_color[3:5], 16)}, {int(icon_color[5:7], 16)}, 0.1)",
                ),
                rx.spacer(),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.vstack(
                rx.text(title, size="3", color="#6B7280", weight="medium", line_height="1.2"),
                rx.text(
                    value, 
                    size="7", 
                    weight="bold", 
                    color="#111827",
                ),
                spacing="1",
                align="start",
                width="100%",
            ),
            spacing="4",
            align="start",
            width="100%",
        ),
        size="3",
        width="100%",
        min_height="140px",
    )


def chart_container(chart_component: rx.Component) -> rx.Component:
    """Reusable container for charts with consistent styling."""
    return rx.box(
        chart_component,
        padding="12",
        border_radius="16px",
        bg="white",
        border="1px solid #E5E7EB",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        width="100%",
        height="420px",
        overflow="hidden",
        _hover={"box_shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"},
        transition="box-shadow 0.3s ease",
    ) 