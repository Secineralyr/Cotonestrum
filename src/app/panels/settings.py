import flet as ft


class PanelSettings(ft.Container):

    def __init__(self):
        super().__init__()

        self.expand = True

        self.content = ft.TextField(
            value='setting',
            expand=True
        )
    
