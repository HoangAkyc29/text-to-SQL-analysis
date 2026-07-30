import flet as ft
from app import theme
from app.ui.shell import build_shell

def main(page: ft.Page):
    theme.page_defaults(page)
    page.add(build_shell(page))
    print("READY_13050", flush=True)

ft.run(main, view=ft.AppView.FLET_APP, port=13050)
