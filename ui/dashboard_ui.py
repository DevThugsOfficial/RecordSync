import flet as ft
from typing import Callable

# Re-use the create_sidebar, attendance/student UI builders from their modules.
from ui.sidebar_ui import create_sidebar

# Light app background for consistent light theme
APP_BG = "#FAFAFA"
CONTENT_PADDING = 16


def build_dashboard_layout(page: ft.Page, active_route: str, content_widget: ft.Control, sidebar_width: int = 240) -> ft.Container:
    """
    Compose the sidebar + main content into a responsive container.
    UI only: no data fetching or business logic.
    """
    sidebar = create_sidebar(page, active_route, lambda name: None, width=sidebar_width)  # placeholder nav callback - view will override
    # The view will replace the sidebar's on_nav_click by recreating sidebar with real callback.
    main = ft.Container(
        ft.Column([content_widget], expand=True, horizontal_alignment=ft.CrossAxisAlignment.START),
        expand=True,
        padding=ft.padding.all(CONTENT_PADDING),
        bgcolor=None,
    )

    layout = ft.Row([sidebar, main], expand=True, spacing=0)
    page_bg = ft.Container(layout, expand=True, bgcolor=APP_BG, padding=ft.padding.all(12))
    return page_bg