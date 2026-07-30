import flet as ft, time

def main(page: ft.Page):
    page.title = "Native smoke"
    page.bgcolor = "#F3F5F8"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.theme = ft.Theme(color_scheme_seed="#0D9488", font_family="Segoe UI")
    page.add(ft.Text("font ok " + time.strftime("%H:%M:%S")))
    print("READY_FONT", flush=True)

ft.run(main, view=ft.AppView.FLET_APP, port=13051)
