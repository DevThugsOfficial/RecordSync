from ui.dashboard_ui import build_dashboard_layout
from ui.attendance_ui import build_attendance_table
from ui.student_ui import build_student_table, build_student_form
from ui.sidebar_ui import create_sidebar
from dashboard.dashboard_controller import DashboardController
from typing import Optional, Dict, Any, List
import flet as ft

# Theme colors for view (light)
MAROON = "#7B0C0C"
TEXT_DARK = "#121212"
CARD_BG = "#FFFFFF"
LIGHT_BORDER = "#E0E0E0"
SHADOW_SOFT = "#0000001A"


def _route_to_section(route: str) -> str:
    if not route:
        return "dashboard"
    parts = route.split("/")
    if len(parts) >= 3 and parts[2]:
        return parts[2]
    return "dashboard"


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


def dashboard_view(page: ft.Page) -> ft.View:
    controller = DashboardController(page)
    
    # Content area for dynamic sections
    attendance_table_container = ft.Container(expand=True)

    def on_nav_click(route: str):
        page.go(route)

    def render():
        """Render content based on current route"""
        section = _route_to_section(page.route)
        
        if section == "attendance":
            data = controller.get_attendance_data()
            attendance_table_container.content = build_attendance_table(data)
        elif section == "students":
            data = controller.get_students()
            attendance_table_container.content = build_student_table(data)
        else:  # dashboard
            stats = controller.get_quarter_stats()
            chart_widget = _build_small_bar_chart(stats.get("weeks", []))
            
            # Get attendance data for the dashboard content widget
            attendance_data = controller.get_attendance_data()
            content_widget = build_attendance_table(attendance_data)
            
            attendance_table_container.content = build_dashboard_layout(stats, chart_widget, content_widget)
        
        page.update()

    def on_attendance_changed():
        """Called when CSV file changes - refresh the UI"""
        print("Attendance data changed, refreshing UI...")
        render()

    # Register callback with controller
    controller.set_on_attendance_changed(on_attendance_changed)
    
    # Start file watcher
    controller.start_watching()

    # Create sidebar with required parameters
    sidebar = create_sidebar(page, active_route=page.route, on_nav_click=on_nav_click)

    # Initial render
    render()

    # Main layout: sidebar + content in a Row
    main_content = ft.Row(
        [
            sidebar,
            attendance_table_container,
        ],
        spacing=0,
        expand=True,
    )

    return ft.View(
        route=(page.route or "/dashboard"),
        controls=[main_content],
        padding=0,
    )