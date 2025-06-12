"""Sidebar navigation component."""

import reflex as rx
from ..pages.auth import AuthState


def sidebar(active_page: str = "dashboard") -> rx.Component:
    return rx.vstack(
        # Header with TTSH logo
        rx.box(
            rx.center(
                rx.image(
                    src="/ttsh.png",
                    width="60px",
                    height="60px",
                    alt="TTSH Logo",
                ),
            ),
            padding="6",
            width="100%",
            height="80px",
            border_bottom="0px solid #E5E7EB",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        # Navigation items - Left-inclined with 2:8 margin ratio
        rx.vstack(
            rx.cond(
                active_page == "dashboard",
                rx.box(
                    rx.hstack(
                        rx.icon("layout-dashboard", size=18, color="white"),
                        rx.text("Dashboard", color="white", weight="medium", size="4"),
                        spacing="3",
                        align="center",
                        justify="start",
                    ),
                    padding="12px 16px",  # Top/bottom: 12px, Left/right: 16px
                    bg="#181C62",
                    border_radius="12px",
                    margin_left="1rem",   # 2 parts (smaller margin)
                    margin_right="2rem",  # 8 parts (larger margin)
                    width="calc(100% - 2rem)",  # Account for both margins
                ),
                rx.box(
                    rx.hstack(
                        rx.icon("layout-dashboard", size=18, color="#6B7280"),
                        rx.text("Dashboard", color="#6B7280", weight="medium", size="4"),
                        spacing="3",
                        align="center",
                        justify="start",
                    ),
                    padding="12px 16px",  # Top/bottom: 12px, Left/right: 16px
                    cursor="pointer",
                    on_click=rx.redirect("/dashboard"),
                    _hover={"bg": "#181C62", "color": "white"},
                    border_radius="12px",
                    margin_left="1rem", 
                    margin_right="2rem",
                    width="calc(100% - 2rem)",  # Account for both margins
                ),
            ),
            rx.cond(
                active_page == "patients",
                rx.box(
                    rx.hstack(
                        rx.icon("users", size=18, color="white"),
                        rx.text("Patients", color="white", weight="medium", size="4"),
                        spacing="3",
                        align="center",
                        justify="start",
                    ),
                    padding="12px 16px",  # Top/bottom: 12px, Left/right: 16px
                    bg="#181C62",
                    border_radius="12px",
                    margin_left="1rem",   # 2 parts (smaller margin)
                    margin_right="2rem",  # 8 parts (larger margin)
                    width="calc(100% - 2rem)",  # Account for both margins
                ),
                rx.box(
                    rx.hstack(
                        rx.icon("users", size=18, color="#6B7280"),
                        rx.text("Patients", color="#6B7280", weight="medium", size="4"),
                        spacing="3",
                        align="center",
                        justify="start",
                    ),
                    padding="12px 16px",  # Top/bottom: 12px, Left/right: 16px
                    cursor="pointer",
                    on_click=rx.redirect("/patients"),
                    _hover={"bg": "#181C62", "color": "white"},
                    border_radius="12px",
                    margin_left="1rem",   # 2 parts (smaller margin)
                    margin_right="2rem",  # 8 parts (larger margin)
                    width="calc(100% - 2rem)",  # Account for both margins
                ),
            ),
            spacing="2",
            width="100%",
            padding_y="6",
            align="start",
        ),
        
        # Spacer
        rx.spacer(),
        
        rx.vstack(
            rx.hstack(
                rx.avatar(
                    src="https://lh3.googleusercontent.com/COxitqgJr1sJnIDe8-jiKhxDx1FrYbtRHKJ9z_hELisAlapwE9LUPh6fcXIfb5vwpbMl4xl9H9TRFPc5NOO8Sb3VSgIBrfRYvW6cUA",
                    size="2",
                    fallback="G",
                ),
                rx.vstack(
                    rx.text("Username", color="#111827", weight="bold", size="3"),
                    rx.text("2390819937@qq.com", color="#9CA3AF", size="2"),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="center",
                width="100%",
            ),
            rx.box(
                rx.hstack(
                    rx.icon("log-out", size=18, color="#6B7280"),
                    rx.text("Log out", color="#6B7280", weight="medium", size="3"),
                    spacing="3",
                    align="center",
                    justify="start",
                ),
                padding="12px 12px",  # Top/bottom: 12px, Left/right: 12px
                cursor="pointer",
                on_click=AuthState.logout,
                _hover={"bg": "#181C62", "color": "white"},
                border_radius="12px",
                margin_left="3rem", 
                margin_right="3rem", 
            ),
            spacing="4",
            width="100%",
            padding="6",
            border_top="1px solid #E5E7EB",
        ),
        
        bg="white",  # Clean white background
        width="250px",
        height="100vh",
        position="fixed",
        left="0",
        top="0",
        spacing="0",
        justify="between",
        border_right="1px solid #E5E7EB",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    ) 