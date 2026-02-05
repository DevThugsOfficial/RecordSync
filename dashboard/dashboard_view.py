from ui.dashboard_ui import build_dashboard_layout
from ui import attendance_ui
from ui.attendance_ui import build_attendance_table
from ui.student_ui import build_student_table, build_student_form
from ui.sidebar_ui import create_sidebar
from dashboard.dashboard_controller import DashboardController
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
import flet as ft
from core.attendance_manager import sync_students_data
import os

# Theme colors for view (light)
MAROON = "#7B0C0C"
TEXT_DARK = "#121212"
CARD_BG = "#FFFFFF"
LIGHT_BORDER = "#E0E0E0"
SHADOW_SOFT = "#0000001A"
YELLOW = "#FFD600"


def _route_to_section(route: str) -> str:
    if not route:
        return "students"
    parts = route.split("/")
    for p in parts:
        if p in ("attendance", "students", "settings"):
            return p
    return "students"


def _build_small_bar_chart(weeks: List[Dict[str, int]]) -> ft.Container:
    """
    Simple grouped bar chart (UI-only). weeks: list of {"label","present","absent"}
    Uses colored Containers to represent bars.
    """
    max_val = max((max(w.get("present", 0), w.get("absent", 0)) for w in weeks), default=1)
    rows = []
    for w in weeks:
        p = w.get("present", 0)
        a = w.get("absent", 0)
        p_width = int((p / max_val * 200)) if max_val else 0
        a_width = int((a / max_val * 200)) if max_val else 0
        rows.append(
            ft.Row(
                [
                    ft.Text(w.get("label", ""), width=40),
                    ft.Container(
                        ft.Text(f"{p}", color="white", size=10),
                        width=p_width,
                        bgcolor="#4CAF50",
                        border_radius=2,
                        padding=2,
                    ),
                    ft.Container(
                        ft.Text(f"{a}", color="white", size=10),
                        width=a_width,
                        bgcolor="#F44336",
                        border_radius=2,
                        padding=2,
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
            )
        )

    chart = ft.Column(rows, spacing=8)
    return ft.Container(
        chart,
        padding=ft.padding.all(12),
        bgcolor=CARD_BG,
        border_radius=10,
        border=ft.border.all(1, LIGHT_BORDER),
        shadow=ft.BoxShadow(blur_radius=6, color=SHADOW_SOFT, offset=ft.Offset(0, 4)),
    )


def _build_pie_chart(present: int, absent: int, size: int = 140) -> ft.Container:
    total = present + absent
    if total > 0:
        pct = int(round((present / total) * 100))
        # ensure full presence shows 100%
        if present > 0 and absent == 0:
            pct = 100
        pct = max(0, min(100, pct))
    else:
        pct = 0

    # Circular percentage display (padding so it won't be clipped) and a compact legend
    circle = ft.Container(
        ft.Column(
            [
                ft.Text(f"{pct}%", size=20, weight=ft.FontWeight.BOLD, color=MAROON),
                ft.Text("Present", size=10, color=TEXT_DARK),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
        ),
        width=size,
        height=size,
        border_radius=size // 2,
        bgcolor=YELLOW,
        alignment=ft.alignment.center,
        padding=ft.padding.all(8),
    )

    legend = ft.Column(
        [
            ft.Row([ft.Container(width=12, height=12, bgcolor=YELLOW, border_radius=2), ft.Container(width=8), ft.Text(f"Present: {present}")]),
            ft.Row([ft.Container(width=12, height=12, bgcolor="#F44336", border_radius=2), ft.Container(width=8), ft.Text(f"Absent: {absent}")]),
        ],
        spacing=8,
    )

    # ensure the pie container has enough width so the circle + legend are not clipped
    return ft.Container(
        ft.Row(
            [
                circle,
                ft.Container(width=16),
                legend,
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=ft.padding.all(12),
        bgcolor=CARD_BG,
        border=ft.border.all(1, LIGHT_BORDER),
        border_radius=8,
    )


def _build_line_chart(weeks: List[Dict[str, int]], height: int = 120) -> ft.Container:
    """
    Build a simple dot-style line chart and compute a basic linear-fit 'AI' prediction.
    The prediction is shown as a highlighted dot and a small label below the chart.
    """
    values = [w.get("present", 0) for w in weeks]
    n = len(values)

    # Simple linear regression (least squares) to predict the next value
    predicted = 0
    if n >= 2:
        xs = list(range(n))
        mean_x = sum(xs) / n
        mean_y = sum(values) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values))
        den = sum((x - mean_x) ** 2 for x in xs)
        slope = (num / den) if den else 0
        intercept = mean_y - slope * mean_x
        predicted = max(0, int(round(intercept + slope * n)))
    elif n == 1:
        predicted = values[0]
    else:
        predicted = 0

    values_extended = values + [predicted]
    max_v = max(values_extended) if values_extended else 1

    points = []
    for i, v in enumerate(values_extended):
        is_pred = (i == n)
        dot_color = YELLOW if is_pred else MAROON
        label = f"{v}" + (" (pred)" if is_pred else "")
        p = ft.Column(
            [
                ft.Container(expand=True),  # spacer to simulate vertical position behavior
                ft.Container(width=8, height=8, border_radius=4, bgcolor=dot_color),
                ft.Text(label, size=10),
            ],
            alignment=ft.MainAxisAlignment.END,
            spacing=6,
            width=48,
        )
        points.append(p)

    row = ft.Row(points, alignment=ft.MainAxisAlignment.START, spacing=8)

    prediction_text = ft.Text(f"Next week prediction: {predicted}", size=12)

    return ft.Container(
        ft.Column(
            [
                ft.Text("AI Prediction", weight=ft.FontWeight.BOLD),
                row,
                ft.Container(prediction_text, padding=ft.padding.only(top=8)),
            ],
            spacing=8,
        ),
        padding=ft.padding.all(12),
        bgcolor=CARD_BG,
        border=ft.border.all(1, LIGHT_BORDER),
        border_radius=8,
    )


def dashboard_view(page: ft.Page) -> ft.View:
    controller = DashboardController(page)

    # Central content container (only this will be swapped/updated)
    content_container = ft.Container(expand=True)

    # Inline save message state (persistent controls so user can edit without losing focus)
    save_message = ""
    save_message_color = "green"
    save_status_label = ft.Text(save_message, size=12, color=save_message_color)

    # Persistent fields (created once so re-renders don't reset them and prevent typing)
    classes_field = ft.TextField(
        label="Classes per quarter",
        value=str(controller.get_class_settings()),
        width=260,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    time_text_field = ft.TextField(
        label="Class Start Time (e.g. 08:00 AM)",
        value=str(controller.get_class_time() or ""),
        width=260,
    )

    duration_field = ft.TextField(
        label="Class duration (minutes)",
        value=str(controller.get_class_duration_minutes()),
        width=260,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    time_picker = None
    time_picker_display = None
    if hasattr(ft, "TimePicker"):
        try:
            t_val = datetime.strptime(str(controller.get_class_time() or "").strip(), "%I:%M %p").time()
        except Exception:
            t_val = None
        time_picker = ft.TimePicker(value=t_val)
        time_picker_display = ft.Container(time_picker, padding=ft.padding.only(top=6))

    time_control_display = ft.Column(
        [time_text_field] + ([time_picker_display] if time_picker_display is not None else []),
        spacing=6,
    )

    # Save handler uses the persistent fields and updates controller + attendance statuses
    def _save_settings(e):
        nonlocal save_message, save_message_color
        try:
            cpq_raw = classes_field.value or ""
            cpq = int(cpq_raw) if str(cpq_raw).strip().isdigit() else controller.get_class_settings()
            controller.update_class_settings(cpq)

            tm_raw = (time_text_field.value or "").strip()
            if tm_raw:
                tm = tm_raw
            elif time_picker and getattr(time_picker, "value", None):
                tp = time_picker.value
                tm = datetime.combine(date.today(), tp).strftime("%I:%M %p")
            else:
                tm = controller.get_class_time()
            controller.set_class_time(str(tm))

            dur_raw = duration_field.value or ""
            dur = int(dur_raw) if str(dur_raw).strip().isdigit() else controller.get_class_duration_minutes()
            controller.set_class_duration_minutes(dur)

            # Recompute attendance statuses using 15 minute grace
            try:
                sync_students_data(str(tm), "03:00 PM", class_start_grace_minutes=15)
            except Exception as e:
                print(f"Warning: sync_students_data failed on save: {e}")

            save_message = "Saved successfully"
            save_message_color = "green"
            save_status_label.value = save_message
            save_status_label.color = save_message_color
        except Exception as err:
            save_message = f"Error saving: {err}"
            save_message_color = "red"
            save_status_label.value = save_message
            save_status_label.color = save_message_color

        # Re-render to update summary, analytics and attendance statuses
        render()

    # show an icon + "Save" text on the button (explicit content to guarantee both appear)
    save_btn = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.SAVE, color=MAROON, size=18),
                ft.Container(width=8),
                ft.Text("Save", size=14, weight=ft.FontWeight.BOLD, color=MAROON),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        on_click=_save_settings,
        bgcolor="#FFD600",
    )

    def nav_callback(name: str):
        n = (name or "").lstrip("/")
        if n == "attendance" or n == "":
            page.go("/attendance")
        elif n == "students":
            page.go("/students")
        elif n == "settings":
            page.go("/settings")
        elif n == "logout":
            try:
                controller.logout()
            except Exception as e:
                print(f"Logout error: {e}")

            # Stop watcher thread
            try:
                attendance_ui.stop_attendance_watcher(page)
            except Exception:
                pass

            # Exit the process (safe, immediate)
            try:
                os._exit(0)
            except Exception:
                try:
                    import sys
                    sys.exit(0)
                except Exception:
                    pass

        else:
            page.go("/attendance")

    def render():
        nonlocal save_message, save_message_color
        """Render content based on current page.route — only update content_container"""
        section = _route_to_section(page.route or "/students")

        if section == "attendance":
            # ensure statuses are computed with the current class start time and 15-minute grace
            try:
                sync_students_data(controller.get_class_time(), "03:00 PM", class_start_grace_minutes=15)
            except Exception:
                pass
            data = controller.get_attendance_data()

            # compute a human-friendly late-threshold string (class start + 15min)
            threshold_str = None
            try:
                cs = controller.get_class_time()
                if cs:
                    cs_parsed = datetime.strptime(cs, "%I:%M %p").time()
                    thr = datetime.combine(date.today(), cs_parsed) + timedelta(minutes=15)
                    threshold_str = thr.strftime("%I:%M %p")
            except Exception:
                threshold_str = None

            content_container.content = build_attendance_table(data, late_threshold=threshold_str)

        elif section == "students":
            data = controller.get_students()
            content_container.content = build_student_table(data)

        elif section == "settings":
            stats = controller.get_quarter_stats() or {}

            class_setup_card = ft.Container(
                ft.Column(
                    [
                        ft.Text("Class Setup", weight=ft.FontWeight.BOLD, size=16),
                        classes_field,
                        time_control_display,
                        duration_field,
                        ft.Row([save_btn, ft.Container(width=12), save_status_label], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ],
                    spacing=10
                ),
                padding=ft.padding.all(12),
                bgcolor=CARD_BG,
                border=ft.border.all(1, LIGHT_BORDER),
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=6, color=SHADOW_SOFT, offset=ft.Offset(0, 4)),
            )

            # --- Class Summary Cards (dynamic) ---
            total_students = stats.get("number_of_students", 0)
            total_present = stats.get("total_present", 0)
            total_absent = total_students - total_present

            def _stat_card(title: str, value: int) -> ft.Container:
                return ft.Container(
                    ft.Column(
                        [
                            ft.Text(title, size=12),
                            ft.Container(
                                ft.Text(str(value), size=28, weight=ft.FontWeight.BOLD, color=MAROON),
                                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                border=ft.border.all(1, LIGHT_BORDER),
                                border_radius=8,
                                bgcolor=CARD_BG,
                                alignment=ft.alignment.center,
                            ),
                        ],
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(8),
                )

            summary_card = ft.Container(
                ft.Column(
                    [
                        ft.Text("Class Summary", weight=ft.FontWeight.BOLD, size=16),
                        ft.Row(
                            [
                                _stat_card("Total Students", total_students),
                                ft.Container(width=12),
                                _stat_card("Present", total_present),
                                ft.Container(width=12),
                                _stat_card("Absent", total_absent),
                            ],
                            spacing=12,
                        ),
                        # Show saved settings in the summary so they appear after Save
                        ft.Container(
                            ft.Column(
                                [
                                    ft.Text(f"Classes per quarter: {controller.get_class_settings()}", size=12),
                                    ft.Text(f"Start Time: {controller.get_class_time()}", size=12),
                                    ft.Text(f"Duration: {controller.get_class_duration_minutes()} minutes", size=12),
                                ],
                                spacing=6,
                            ),
                            padding=ft.padding.only(top=8),
                        ),
                    ],
                    spacing=12
                ),
                padding=ft.padding.all(12),
                bgcolor=CARD_BG,
                border=ft.border.all(1, LIGHT_BORDER),
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=6, color=SHADOW_SOFT, offset=ft.Offset(0, 4)),
            )

            # --- Analytics (Bar / Pie / Line) ---
            bar = _build_small_bar_chart(stats.get("weeks", []))
            pie = _build_pie_chart(total_present, total_absent, size=160)  # increase size so it renders fully
            line = _build_line_chart(stats.get("weeks", []))

            analytics_card = ft.Container(
                ft.Column(
                    [
                        ft.Text("Analytics", weight=ft.FontWeight.BOLD, size=16),
                        ft.Row(
                            [
                                ft.Container(bar, expand=True),
                                ft.Container(pie, width=320),  # give more width so pie + legend aren't clipped
                            ],
                            spacing=12,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        ft.Container(line, padding=ft.padding.only(top=12)),
                    ],
                    spacing=12
                ),
                padding=ft.padding.all(12),
                bgcolor=CARD_BG,
                border=ft.border.all(1, LIGHT_BORDER),
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=6, color=SHADOW_SOFT, offset=ft.Offset(0, 4)),
            )

            # Layout: Class Setup (left) + Summary (right), Analytics below
            top_row = ft.Row([ft.Container(class_setup_card, expand=True), ft.Container(summary_card, width=340)], spacing=20, alignment=ft.MainAxisAlignment.START)

            content_container.content = ft.Column(
                [top_row, analytics_card],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            )

        page.update()

    # Use dashboard_ui to compose the page layout (sidebar is a placeholder inside that helper).
    active_route = page.route or "/students"
    page_bg = build_dashboard_layout(page, active_route, content_container, sidebar_width=240)

    # Replace placeholder sidebar with one wired to our nav callback and accurate active_route.
    try:
        new_sidebar = create_sidebar(page, page.route or "/students", nav_callback, width=240)
        existing_sidebar = page_bg.content.controls[0]
        existing_sidebar.content = new_sidebar.content
    except Exception:
        pass

    # page.on_route_change should update sidebar selection and render content
    def _on_route_change(e):
        try:
            new_sidebar = create_sidebar(page, page.route or "/students", nav_callback, width=240)
            page_bg.content.controls[0].content = new_sidebar.content
        except Exception:
            pass
        render()

    page.on_route_change = _on_route_change

    # Ensure watcher stops on page close to avoid thread leaks
    prev_on_close = getattr(page, "on_close", None)

    def _on_close(e):
        try:
            attendance_ui.stop_attendance_watcher(page)
        except Exception:
            pass
        if callable(prev_on_close):
            try:
                prev_on_close(e)
            except Exception:
                pass

    page.on_close = _on_close

    # Start attendance file watcher (idempotent)
    attendance_ui.start_attendance_watcher(page, controller, lambda: render())

    # Default route handling: ensure we land on /students when route is empty or "/"
    if page.route in ("", "/"):
        page.go("/students")
    else:
        render()

    return ft.View(
        route=(page.route or "/attendance"),
        controls=[page_bg],
        padding=0,
    )
