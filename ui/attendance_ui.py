import flet as ft
from typing import List, Dict, Any, Callable, Optional
import threading
import time
from core.attendance_manager import ATTENDANCE_CSV, sync_students_data

MAROON = "#7B0C0C"
YELLOW = "#FFD400"

# Light theme
BG = "#FAFAFA"
CARD_BG = "#FFFFFF"
TEXT_COLOR = "#121212"
HEADING_ROW = MAROON
LIGHT_BORDER = "#E0E0E0"
SHADOW_SOFT = "#0000001A"


def build_attendance_table(
    attendance_data: List[Dict[str, Any]],
    width: int = 1000,
    on_add: Optional[Callable[..., None]] = None,
    late_threshold: Optional[str] = None,
):
    """
    Build attendance table. late_threshold (e.g. "08:15 AM") is an optional string displayed in the header.
    """

    # ---------- DEFAULT ADD HANDLER ----------

    def _default_on_add(e=None):
        page = None
        try:
            if e and hasattr(e, "page"):
                page = e.page
        except Exception:
            pass

        if page:
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
            print("Add Student clicked")

    btn_on_add = on_add if callable(on_add) else _default_on_add

    # ---------- BUILD TABLE ROWS ----------

    rows = []

    for r in attendance_data:
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
        column_spacing=120,
        data_row_min_height=52,
    )

    # ---------- HEADER ----------

    header_children = [
        ft.Text("Attendance", size=20, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(expand=True),
    ]
    if late_threshold:
        header_children.insert(1, ft.Text(f"Late after {late_threshold}", size=12, color=TEXT_COLOR))

    header = ft.Row(
        header_children + [
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

    # ---------- TABLE CARD ----------

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

    # ---------- PAGE LAYOUT (MATCH STUDENT_UI) ----------

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


# ============================================================
# FILE WATCHER (UNCHANGED LOGIC)
# ============================================================

def start_attendance_watcher(page: ft.Page, controller, on_changed_callback, poll_interval: float = 1.0):
    """
    Start a background daemon thread that watches ATTENDANCE_CSV mtime and calls
    on_changed_callback() (scheduled with page.call_from_worker) whenever the file changes.

    - Ensures only one watcher per page.
    - Does not block UI thread.
    """
    if hasattr(page, "_attendance_watcher_running") and getattr(page, "_attendance_watcher_running"):
        return  # already running

    stop_flag = {"stop": False}
    page._attendance_watcher_stop_flag = stop_flag
    page._attendance_watcher_running = True

    # initialize last mtime
    try:
        last_mtime = ATTENDANCE_CSV.stat().st_mtime if ATTENDANCE_CSV.exists() else 0
    except Exception:
        last_mtime = 0

    def _watcher():
        nonlocal last_mtime
        try:
            while not stop_flag["stop"]:
                try:
                    if ATTENDANCE_CSV.exists():
                        current_mtime = ATTENDANCE_CSV.stat().st_mtime
                        if current_mtime > last_mtime:
                            last_mtime = current_mtime
                            # allow core to recompute statuses if needed
                            try:
                                class_start = controller.get_class_time()
                                class_end = "03:00 PM"
                                try:
                                    # use 15 minute grace for "Late"
                                    sync_students_data(class_start, class_end, class_start_grace_minutes=15)
                                except Exception as e:
                                    print(f"Warning: sync_students_data failed in watcher: {e}")
                            except Exception as e:
                                print(f"Error during watcher sync: {e}")

                            # Schedule UI update on main thread
                            try:
                                page.call_from_worker(lambda: on_changed_callback())
                            except Exception:
                                try:
                                    on_changed_callback()
                                except Exception as e:
                                    print(f"Error calling on_changed_callback: {e}")
                    time.sleep(poll_interval)
                except Exception as e:
                    print(f"Attendance watcher loop error: {e}")
                    time.sleep(1)
        finally:
            page._attendance_watcher_running = False

    t = threading.Thread(target=_watcher, daemon=True, name="attendance-watcher")
    page._attendance_watcher_thread = t
    t.start()


def stop_attendance_watcher(page: ft.Page):

    stop_flag = getattr(page, "_attendance_watcher_stop_flag", None)

    if stop_flag:
        stop_flag["stop"] = True

    thr = getattr(page, "_attendance_watcher_thread", None)

    if thr and thr.is_alive():
        thr.join(timeout=1)

    page._attendance_watcher_running = False
