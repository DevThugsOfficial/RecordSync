import flet as ft
from typing import List, Dict, Any, Callable
from pathlib import Path

MAROON = "#7B0C0C"
YELLOW = "#FFD400"

# Light theme
BG = "#FAFAFA"
CARD_BG = "#FFFFFF"
TEXT_COLOR = "#121212"
HEADING_ROW = MAROON
LIGHT_BORDER = "#E0E0E0"
SHADOW_SOFT = "#0000001A"


def _default_on_add_student(e=None):
    page = None
    try:
        if e is not None and hasattr(e, "page"):
            page = e.page
    except Exception:
        page = None

    if page is not None:
        page.dialog = ft.AlertDialog(
            title=ft.Text("Add Student"),
            content=ft.Text("Add Student button clicked (stub)"),
            actions=[
                ft.ElevatedButton(
                    "OK",
                    on_click=lambda ev: (
                        setattr(page.dialog, "open", False),
                        page.update(),
                    ),
                )
            ],
        )
        page.dialog.open = True
        page.update()
    else:
        print("Add Student button clicked")


def build_student_table(
    student_data: List[Dict[str, Any]],
    on_add: Callable[[], None] = None,
    on_edit: Callable[[Dict[str, Any]], None] = None,
    on_delete: Callable[[Dict[str, Any]], None] = None,
    width: int = 1000,
):

    def _avatar_control(s: Dict[str, Any]):
        src = (s.get("photo") or "").strip()
        try:
            if src:
                # If it’s a URL, use as-is
                if src.startswith(("http://", "https://")):
                    return ft.Image(src=src, width=36, height=36, fit=ft.ImageFit.COVER)

                # Try relative path (relative to project root)
                p = Path(src)
                if not p.is_absolute():
                    p = Path.cwd() / p  # cwd is where main.py runs
                if p.exists():
                    return ft.Image(src=str(p), width=36, height=36, fit=ft.ImageFit.COVER)

        except Exception:
            pass

        # fallback avatar
        return ft.Container(
            ft.Icon(ft.Icons.PERSON, color="white", size=22),
            width=36,
            height=36,
            alignment=ft.alignment.center,
            bgcolor=MAROON,
            border_radius=18,
        )

    btn_on_add = on_add if callable(on_add) else _default_on_add_student

    rows = []

    for s in student_data:
        attended = s.get("attended", 0)
        total = s.get("classes_total", 20)

        classes_text = f"{attended}/{total}"

        rows.append(
            ft.DataRow(
                cells=[
                    # ID
                    ft.DataCell(ft.Text(s.get("id", ""), color=TEXT_COLOR)),

                    # Avatar + Name
                    ft.DataCell(
                        ft.Row(
                            [
                                _avatar_control(s),
                                ft.Container(width=8),
                                ft.Text(s.get("name", ""), color=TEXT_COLOR),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ),

                    # Classes
                    ft.DataCell(ft.Text(classes_text, color=TEXT_COLOR)),

                    # Actions
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    on_click=lambda e, st=s: on_edit(st)
                                    if callable(on_edit)
                                    else None,
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    on_click=lambda e, st=s: on_delete(st)
                                    if callable(on_delete)
                                    else None,
                                ),
                            ]
                        )
                    ),
                ]
            )
        )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", color="white")),
            ft.DataColumn(ft.Text("Student", color="white")),
            ft.DataColumn(ft.Text("Classes", color="white")),
            ft.DataColumn(ft.Text("Actions", color="white")),
        ],
        rows=rows,
        heading_row_color=HEADING_ROW,
        border=ft.border.all(0.5, LIGHT_BORDER),
        column_spacing=150,
        data_row_min_height=56,
    )

    header = ft.Row(
        [
            ft.Text("Students", size=20, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
            ft.Container(expand=True),
            ft.ElevatedButton(
                "Add Student",
                icon=ft.Icons.PERSON_ADD,
                on_click=btn_on_add,
                bgcolor=YELLOW,
                color=MAROON,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
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
        shadow=ft.BoxShadow(blur_radius=8, color=SHADOW_SOFT, offset=ft.Offset(0, 6)),
    )

    outer = ft.Container(
        ft.Column(
            [
                header,
                ft.Row(
                    [
                        ft.Container(expand=True),
                        inner,
                        ft.Container(expand=True),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=12,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=12),
        bgcolor=BG,
    )

    return outer


# ✅ RESTORED FUNCTION (Required by dashboard import)
def build_student_form(initial: Dict[str, Any] | None, on_submit: Callable[[Dict[str, Any]], None]) -> ft.Column:

    name = ft.TextField(label="Name", value=(initial.get("name") if initial else ""), width=360)
    photo = ft.TextField(label="Photo path (optional)", value=(initial.get("photo") if initial else ""), width=360)

    classes = ft.TextField(
        label="Total classes",
        value="20",
        width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    def _submit(e):
        payload = {
            "name": (name.value or "").strip(),
            "photo": (photo.value or "").strip(),
            "classes": int(classes.value or 20),
        }
        on_submit(payload)

    form = ft.Column(
        [
            name,
            photo,
            classes,
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Save",
                        on_click=_submit,
                        bgcolor=YELLOW,
                        color=MAROON,
                    )
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
        ],
        tight=False,
        spacing=8,
    )

    return form
