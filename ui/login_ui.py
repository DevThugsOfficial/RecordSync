import flet as ft

# Light theme colors for login UI
BG_LIGHT = "#FAFAFA"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#121212"
MAROON = "#7B0C0C"

# Enhanced visibility colors
LIGHT_BORDER = "#D1D1D1"        # More visible border
INPUT_BORDER = "#E3E3E3"        # Subtle input outline
SHADOW_SOFT = "#00000026"       # Slightly stronger shadow
WHITE = "#FFFFFF"
BLUE = "#1976D2"

def login_card(page: ft.Page, *, on_signup, on_forgot, on_login) -> ft.Container:

    username = ft.TextField(
        hint_text="username",
        bgcolor=BG_LIGHT,
        border_radius=12,
        border_color=INPUT_BORDER,   # changed from transparent
        content_padding=12,
        width=260,
        text_style=ft.TextStyle(font_family="Port Lligat Slab", color=TEXT_DARK),
        hint_style=ft.TextStyle(font_family="Port Lligat Slab", color="#99000000"),
    )

    password = ft.TextField(
        hint_text="password",
        password=True,
        can_reveal_password=True,
        bgcolor=BG_LIGHT,
        border_radius=12,
        border_color=INPUT_BORDER,   # changed from transparent
        content_padding=12,
        width=260,
        text_style=ft.TextStyle(font_family="Port Lligat Slab", color=TEXT_DARK),
        hint_style=ft.TextStyle(font_family="Port Lligat Slab", color="#99000000"),
    )

    return ft.Container(
        width=360,
        padding=30,
        bgcolor=CARD_BG,

        # Card enhancement
        border_radius=16,   # smoother card rounding
        border=ft.border.all(1, LIGHT_BORDER),   # visible card stroke

        shadow=ft.BoxShadow(
            blur_radius=28,
            color=SHADOW_SOFT,
            offset=ft.Offset(0, 8),
        ),

        content=ft.Column(
            [
                ft.Image(src="stc.png", width=200, height=200),

                ft.Text(
                    "Sign in",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_DARK,
                    font_family="Port Lligat Slab"
                ),

                ft.Container(height=10),
                username,
                ft.Container(height=10),
                password,

                ft.Container(
                    ft.TextButton(
                        "forgot password?",
                        style=ft.ButtonStyle(
                            text_style=ft.TextStyle(
                                size=15,
                                font_family="Port Lligat Slab",
                                color=BLUE
                            )
                        ),
                        on_click=on_forgot
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
                    on_click=lambda e: on_login(e, username, password),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=22)
                    )
                ),

                ft.Container(height=15),

                ft.TextButton(
                    "Don't have an account?",
                    style=ft.ButtonStyle(
                        text_style=ft.TextStyle(
                            size=15,
                            font_family="Port Lligat Slab",
                            color=BLUE
                        )
                    ),
                    on_click=on_signup
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
    )
