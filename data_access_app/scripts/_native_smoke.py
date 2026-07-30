import flet as ft
import time

def main(page: ft.Page):
    page.title = "Native smoke"
    page.add(ft.Text("NATIVE OK " + time.strftime("%H:%M:%S"), size=28))
    print("MAIN_OK", flush=True)

ft.run(main, view=ft.AppView.FLET_APP, port=13051)
