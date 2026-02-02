import flet as ft
from typing import Callable

# primary accent kept as maroon
MAROON = "#7B0C0C"
YELLOW = "#FFD400"

# Sidebar should be transparent per theme guidelines
SIDEBAR_BG = None

# Light theme text and borders
TEXT_DARK = "#121212"
LIGHT_BORDER = "#E0E0E0"
SHADOW_SOFT = "#0000001A"  # subtle shadow

def create_sidebar(page: ft.Page, active_route: str, on_nav_click: Callable[[str], None], width: int = 220) -> ft.Container:
    """
    Pure UI: returns a sidebar Container with icon + label buttons.
    - active_route: one of "attendance","students","settings"
    - on_nav_click: callback(name) - UI does not perform navigation itself
    """
    def _btn(label: str, key: str, icon) -> ft.Control:
        selected = (key == active_route)
        # On light sidebar, unpressed buttons have white background and dark text.
        btn_bg = YELLOW if selected else "#FFFFFF"
        icon_color = MAROON
        text_color = TEXT_DARK
        content_row = ft.Row(
            [
                ft.Icon(icon, color=icon_color, size=18),
                ft.Container(width=10),
                ft.Text(label, color=text_color, size=14),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        )

        return ft.Container(
            ft.ElevatedButton(
                content=content_row,
                on_click=lambda e, k=key: on_nav_click(k),
                style=ft.ButtonStyle(
                    bgcolor=btn_bg,
                    color=text_color,
                    shape=ft.RoundedRectangleBorder(radius=10),
                    elevation=6 if selected else 0,
                    overlay_color="#00000006",
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                ),
            ),
            bgcolor=SIDEBAR_BG,
            padding=ft.padding.symmetric(vertical=0),
            width=width - 32,
        )

    logo = ft.Image(src="stc.png", width=88, height=88, fit=ft.ImageFit.CONTAIN)

    sidebar_col = ft.Column(
        [
            ft.Container(logo, alignment=ft.alignment.center, padding=ft.padding.only(top=12, bottom=8)),
            ft.Divider(thickness=1, color=LIGHT_BORDER),
            _btn("Students", "students", ft.Icons.PEOPLE),
            _btn("Attendance", "attendance", ft.Icons.CHECK),
            _btn("Settings", "settings", ft.Icons.SETTINGS),
            ft.Container(expand=True),  # spacer
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
        border=ft.border.all(1, MAROON),  # keep maroon stroke
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=12, color=SHADOW_SOFT, offset=ft.Offset(2, 6)),
        alignment=ft.alignment.top_center,
        margin=ft.margin.only(right=12),
    )
    return sidebar