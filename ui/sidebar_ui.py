import flet as ft
from typing import Callable

# primary accent kept as maroon
MAROON = "#7B0C0C"
YELLOW = "#FFD400"

# Sidebar background / theme
SIDEBAR_BG = None

# Light theme text and borders
TEXT_DARK = "#121212"
LIGHT_BORDER = "#E0E0E0"
SHADOW_SOFT = "#0000001A"  # subtle shadow

def _normalize_route(route: str) -> str:
    """Return canonical section name for a route string."""
    r = (route or "").lower()
    if "attendance" in r:
        return "attendance"
    if "settings" in r:
        return "settings"
    if "students" in r:
        return "students"
    # default to attendance
    return "attendance"


def create_sidebar(page: ft.Page, active_route: str, on_nav_click: Callable[[str], None], width: int = 240) -> ft.Container:
    """
    Create the sidebar UI. active_route may be '/students', '/attendance', '/settings' or simple names.
    on_nav_click(name) will be called with a route like '/students' when a button is clicked.
    """
    section = _normalize_route(active_route)

    def _btn(label: str, key: str, icon) -> ft.Container:
        selected = (section == key)
        txt = ft.Text(label, size=14, color=(MAROON if selected else TEXT_DARK))
        row = ft.Row(
            [
                ft.Icon(icon, color=MAROON, size=18),
                ft.Container(width=10),
                txt,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
        )
        c = ft.Container(
            content=row,
            padding=ft.padding.symmetric(vertical=10, horizontal=12),
            margin=ft.margin.only(bottom=8),
            bgcolor=(YELLOW if selected else None),
            border_radius=8,
            on_click=lambda e, k=key: on_nav_click(f"/{k}"),
        )
        return c

    logo = ft.Image(src="stc.png", width=88, height=88, fit=ft.ImageFit.CONTAIN)

    logout_btn = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.LOGOUT, color=MAROON, size=18),
                ft.Container(width=10),
                ft.Text("Logout", size=14, color=TEXT_DARK),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=6,
        ),
        padding=ft.padding.symmetric(vertical=10, horizontal=12),
        margin=ft.margin.only(top=12),
        border_radius=8,
        # call the provided navigation callback so higher-level code handles logout/close
        on_click=lambda e: on_nav_click("/logout"),
    )

    sidebar_col = ft.Column(
        [
            ft.Container(logo, alignment=ft.alignment.center, padding=ft.padding.only(top=12, bottom=8)),
            ft.Divider(thickness=1, color=LIGHT_BORDER),
            _btn("Attendance", "attendance", ft.Icons.CHECK),
            _btn("Students", "students", ft.Icons.PEOPLE),
            _btn("Settings", "settings", ft.Icons.SETTINGS),
            ft.Container(expand=True),
            logout_btn,
            ft.Container(ft.Text("RecordSync", color=MAROON, size=12), alignment=ft.alignment.center, padding=8),
        ],
        spacing=8,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        tight=False,
    )

    sidebar = ft.Container(
        sidebar_col,
        width=width,
        padding=16,
        bgcolor=SIDEBAR_BG,
        border=ft.border.all(1, LIGHT_BORDER),
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=12, color=SHADOW_SOFT, offset=ft.Offset(2, 6)),
        alignment=ft.alignment.top_center,
        margin=ft.margin.only(right=12),
    )
    return sidebar