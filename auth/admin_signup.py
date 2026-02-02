from pathlib import Path
import flet as ft
from ui.signup_ui import signup_card

# import admin auth helpers
from core.admin_manager import admin_signup as _admin_signup


def admin_signup_view(page: ft.Page) -> ft.View:
    """
    Return an ft.View for the admin signup page.
    Navigation uses page.go("/") to return to login.
    """
    MAROON = "#7B0C0C"

    # visible status widget (replaces SnackBar feedback)
    status_text = ft.Text("", size=13, weight=ft.FontWeight.BOLD, color="#B00020")

    def on_create_account(e, username_field, password_field, confirm_password_field):
        import csv
        from pathlib import Path

        username_raw = username_field.value or ""
        password_raw = password_field.value or ""
        confirm_raw = confirm_password_field.value or ""

        # Trim and protect against spaces-only values
        username = username_raw.strip()
        password = password_raw.strip()
        confirm = confirm_raw.strip()

        # Basic validation
        if not username or not password or not confirm:
            status_text.value = "All fields are required"
            status_text.color = "#B00020"
            page.update()
            return

        if password != confirm:
            status_text.value = "Passwords do not match"
            status_text.color = "#B00020"
            page.update()
            return

        admin_csv = Path(__file__).resolve().parent.parent / "database" / "admin.csv"

        # Read existing accounts and handle DB errors
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

        # Duplicate username check (case-insensitive)
        for r in rows:
            if (r.get("username") or "").strip().lower() == username.lower():
                status_text.value = "Username already registered"
                status_text.color = "#B00020"
                page.update()
                return

        # Append new admin record
        try:
            max_id = 0
            for r in rows:
                try:
                    max_id = max(max_id, int(r.get("id", 0)))
                except Exception:
                    pass
            new_id = max_id + 1
            with admin_csv.open("a", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow([new_id, username, password])
        except Exception:
            status_text.value = "Database error. Please try again."
            status_text.color = "#B00020"
            page.update()
            return

        # Success: notify and clear fields
        status_text.value = "Account created successfully"
        status_text.color = "#2E7D32"
        username_field.value = ""
        password_field.value = ""
        confirm_password_field.value = ""
        page.update()

    def on_login_redirect(e):
        status_text.value = ""
        page.update()
        page.go("/")

    card = signup_card(page, on_create_account=on_create_account, on_login_redirect=on_login_redirect)

    return ft.View(
        route="/signup",
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


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    ft.app(target=admin_signup_view, view=ft.WEB_BROWSER, assets_dir=str(project_root / "assets"))
