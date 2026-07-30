import flet as ft, time

def main(page: ft.Page):
    page.title = "Data Access - Supermarket"
    page.bgcolor = "#F3F5F8"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window.min_width = 1100
    page.window.min_height = 720
    page.theme = ft.Theme(
        color_scheme_seed="#0D9488",
        font_family="Segoe UI",
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
    page.add(ft.Text("full defaults " + time.strftime("%H:%M:%S")))
    print("READY_FULL", flush=True)

ft.run(main, view=ft.AppView.FLET_APP, port=13051)
