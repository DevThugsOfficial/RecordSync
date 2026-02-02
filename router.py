from typing import Callable, Dict
import flet as ft
import sys
import traceback


def _route_map() -> Dict[str, Callable[[ft.Page], ft.View]]:
    """
    Map top-level routes to view factories. Keep dashboard factory mounted at "/dashboard".
    Subpaths like "/dashboard/attendance" will be routed to the same factory by route_handler.
    """
    from auth.admin_login import admin_login_view
    from auth.admin_signup import admin_signup_view

    dashboard_view = None
    try:
        # import the dashboard view factory from the dashboard package
        from dashboard.dashboard_view import dashboard_view as _dv
        dashboard_view = _dv
    except Exception:
        print("Failed to import dashboard.dashboard_view:", file=sys.stderr)
        traceback.print_exc()

    # fallback simple dashboard view factory if import fails
    if not callable(dashboard_view):

        def dashboard_view(page: ft.Page) -> ft.View:
            return ft.View(
                route="/dashboard",
                controls=[
                    ft.Column(
                        [
                            ft.Container(height=16),
                            ft.Text("Dashboard view not found in dashboard.dashboard_view", size=16),
                            ft.Container(height=8),
                            ft.ElevatedButton("Back to login", on_click=lambda e: page.go("/")),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    )
                ],
            )

    return {
        "/": admin_login_view,
        "/signup": admin_signup_view,
        "/dashboard": dashboard_view,
    }


def route_handler(page: ft.Page) -> Callable[[ft.RouteChangeEvent], None]:
    """
    Returns a handler bound to the provided page.
    Routes that start with "/dashboard" are handled by the dashboard view factory.
    """
    routes = _route_map()

    def _handler(route_event: ft.RouteChangeEvent):
        page.views.clear()
        target = page.route or "/"

        # Treat any /dashboard/* as dashboard root view so dashboard_view can parse subpath
        if target.startswith("/dashboard"):
            view_factory = routes.get("/dashboard")
        else:
            view_factory = routes.get(target)

        if view_factory is None:
            page.views.append(
                ft.View(
                    route=target,
                    controls=[
                        ft.Text(f"Route {target} not found", size=18),
                        ft.ElevatedButton("Back to login", on_click=lambda e: page.go("/")),
                    ],
                )
            )
        else:
            page.views.append(view_factory(page))
        page.update()

    return _handler