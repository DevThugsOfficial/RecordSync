from pathlib import Path
import flet as ft
from ui.login_ui import login_card

# import admin auth helpers
from core.admin_manager import admin_login as _admin_login


def admin_login_view(page: ft.Page) -> ft.View:
    """
    Return an ft.View for the admin login page.
    Navigation uses page.go("/signup") and page.go("/dashboard").
    """
    MAROON = "#7B0C0C"

    # visible status widget (replaces SnackBar feedback)
    status_text = ft.Text("", size=13, weight=ft.FontWeight.BOLD, color="#B00020")

    def on_forgot(e):
        page.dialog = ft.AlertDialog(
            title=ft.Text("Forgot Password", font_family="Port Lligat Slab"),
            content=ft.Text("Redirect to forgot password page here.", font_family="Port Lligat Slab"),
            actions=[ft.TextButton("Close", on_click=lambda ev: (setattr(page.dialog, "open", False), page.update()))],
        )
        page.dialog.open = True
        page.update()

    def on_signup(e):
        # clear any previous message and navigate
        status_text.value = ""
        page.update()
        page.go("/signup")

    def on_login(e, username_field, password_field):
        import csv
        from pathlib import Path

        username = (username_field.value or "").strip()
        password = (password_field.value or "").strip()

        # Field validation (visible messages)
        if not username:
            status_text.value = "Username is required"
            status_text.color = "#B00020"
            page.update()
            return
        if not password:
            status_text.value = "Password is required"
            status_text.color = "#B00020"
            page.update()
            return

        admin_csv = Path(__file__).resolve().parent.parent / "database" / "admin.csv"

        # Ensure file exists (header) and read safely
        try:
            admin_csv.parent.mkdir(parents=True, exist_ok=True)
            if not admin_csv.exists():
                with admin_csv.open("w", newline="", encoding="utf-8") as fh:
                    fh.write("id,username,password\n")
            with admin_csv.open(newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                rows = [r for r in reader]
        except Exception:
            status_text.value = "Database error. Please try again."
            status_text.color = "#B00020"
            page.update()
            return

        # Account existence check (case-insensitive)
        user_row = None
        for r in rows:
            if (r.get("username") or "").strip().lower() == username.lower():
                user_row = r
                break

        if user_row is None:
            status_text.value = "Account not registered"
            status_text.color = "#B00020"
            page.update()
            return

        # Password check
        stored_password = (user_row.get("password") or "")
        if stored_password != password:
            status_text.value = "Incorrect password"
            status_text.color = "#B00020"
            page.update()
            return

        # Success -> clear message and navigate
        status_text.value = ""
        page.update()
        page.go("/dashboard")

    # build login card using reusable UI function
    card = login_card(page, on_signup=on_signup, on_forgot=on_forgot, on_login=on_login)

    return ft.View(
        route="/",
        controls=[
            ft.Column(
                [
                    ft.Container(content=card, alignment=ft.alignment.center, expand=True),
                    ft.Container(height=8),
                    ft.Container(content=status_text, alignment=ft.alignment.center),
                ],
                expand=True,
            )
        ],
    )


# allow running this file directly for quick manual testing
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    ft.app(target=admin_login_view, view=ft.WEB_BROWSER, assets_dir=str(project_root / "assets"))