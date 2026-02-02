import flet as ft
from typing import List, Dict, Any

MAROON = "#7B0C0C"
YELLOW = "#FFD400"

# Light theme colors
BG = "#FAFAFA"
CARD_BG = "#FFFFFF"
TEXT_COLOR = "#121212"
HEADING_ROW = MAROON  # header background set to maroon
LIGHT_BORDER = "#E0E0E0"
SHADOW_SOFT = "#0000001A"


def build_attendance_table(attendance_data: List[Dict[str, Any]], width: int = 1200) -> ft.Container:
    """
    UI-only attendance table builder.
    """
    rows = []

    for idx, r in enumerate(attendance_data):
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(r.get("ID", ""), color=TEXT_COLOR)),
                    ft.DataCell(ft.Text(r.get("Name", ""), color=TEXT_COLOR)),
                    ft.DataCell(ft.Text(r.get("Status", ""), color=TEXT_COLOR)),
                    ft.DataCell(ft.Text(r.get("TimeIn", ""), color=TEXT_COLOR)),
                    ft.DataCell(ft.Text(r.get("TimeOut", ""), color=TEXT_COLOR)),
                ]
            )
        )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Student ID", color="white")),
            ft.DataColumn(ft.Text("Student Name", color="white")),
            ft.DataColumn(ft.Text("Status", color="white")),
            ft.DataColumn(ft.Text("Time In", color="white")),
            ft.DataColumn(ft.Text("Time Out", color="white")),
        ],
        rows=rows,
        heading_row_color=HEADING_ROW,
        border=ft.border.all(0.5, LIGHT_BORDER),
        column_spacing=100,
        data_row_min_height=46,
    )

    # Wrap table in a horizontally scrollable column
    inner_table = ft.Container(
        ft.Column([table], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0),
        padding=ft.padding.all(8),
    )

    inner = ft.Container(
        ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [table],
                        expand=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.all(12),
                ),
            ],
            spacing=12,
            expand=True,
            alignment=ft.alignment.center,
        ),
        width=width,
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        bgcolor=CARD_BG,
        border_radius=10,
        border=ft.border.all(1, LIGHT_BORDER),
        shadow=ft.BoxShadow(
            blur_radius=8,
            color=SHADOW_SOFT,
            offset=ft.Offset(0, 6),
        ),
    )

    outer = ft.Container(
        ft.Row([ft.Container(expand=True), inner, ft.Container(expand=True)], alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.padding.symmetric(horizontal=24, vertical=12),
        bgcolor=BG,
    )

    return outer
