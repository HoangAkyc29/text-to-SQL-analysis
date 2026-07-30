import flet as ft
import time

def main(page: ft.Page):
    page.title = "Data Access - Supermarket"
    page.bgcolor = "#F3F5F8"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    # skip window min sizes
    page.theme = ft.Theme(color_scheme_seed="#0D9488", font_family="Segoe UI")
    page.add(ft.Text("theme ok " + time.strftime("%H:%M:%S")))
    print("READY_T1", flush=True)

ft.run(main, view=ft.AppView.FLET_APP, port=13050)
