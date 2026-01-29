import flet as ft

def main(page: ft.Page):
    page.title = "Login Page"
    page.window_width = 600
    page.window_height = 600
    page.padding = 0
    page.bgcolor = "#F2F2F2"

    # COLORS (HEX = stable)
    MAROON = "#7B0C0C"
    LIGHT_PINK = "#E6CFCF"
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    PURPLE = "#B000FF"

    # INPUTS
    username = ft.TextField(
        hint_text="username",
        bgcolor=LIGHT_PINK,
        border_radius=10,
        border_color="transparent",
        content_padding=12,
        width=260,
    )

    password = ft.TextField(
        hint_text="password",
        password=True,
        can_reveal_password=True,
        bgcolor=LIGHT_PINK,
        border_radius=10,
        border_color="transparent",
        content_padding=12,
        width=260,
    )

    # LOGIN CARD
    login_card = ft.Container(
        width=360,
        padding=30,
        height=530,
        bgcolor=WHITE,
        border_radius=10,
        shadow=ft.BoxShadow(
            blur_radius=20,
            color="#00000020",
            offset=ft.Offset(0, 6),
        ),
        content=ft.Column(
            [
                ft.Image(
                    src="assets/stc.png",  # <-- CHANGE THIS
                    width=100,
                    height=100,
                ),

                ft.Text(
                    "Sign in",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=BLACK,
                ),

                ft.Container(height=10),

                username,
                ft.Container(height=10),
                password,

                ft.Container(
                    ft.Text(
                        "forgot password?",
                        size=12,
                        color=PURPLE,
                    ),
                    alignment=ft.alignment.center_right,
                    width=260,
                ),

                ft.Container(height=15),

                ft.ElevatedButton(
                    text="Log in",
                    width=160,
                    height=42,
                    bgcolor=MAROON,
                    color=WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=20)
                    ),
                ),

                ft.Container(height=15),

                ft.Text(
                    "Don't have an account?",
                    size=12,
                    color=BLACK,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # PAGE LAYOUT
    page.add(
        ft.Column(
            [
                ft.Container(height=40, bgcolor=MAROON),  # TOP BAR

                ft.Container(
                    content=login_card,
                    alignment=ft.alignment.center,
                    expand=True,
                ),
            ],
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
