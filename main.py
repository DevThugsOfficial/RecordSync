from pathlib import Path
import flet as ft
import router


def main(page: ft.Page):
    # global page defaults:
    page.title = "RecordSync"
    page.window_width = 900
    page.window_height = 700
    page.padding = 0
    page.bgcolor = "#F2F2F2"
    page.theme_mode = ft.ThemeMode.LIGHT

    # bind router (route_handler returns a handler bound to this page)
    page.on_route_change = router.route_handler(page)

    # navigate to the current route (will invoke the handler)
    page.go(page.route or "/")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    ft.app(target=main, view=ft.WEB_BROWSER, assets_dir=str(project_root / "assets"))