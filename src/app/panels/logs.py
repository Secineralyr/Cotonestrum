import flet as ft


class PanelLogs(ft.Container):

    def __init__(self):
        super().__init__()

        self.expand = True

        self.content = ft.TextField(
            value='log',
            expand=True
        )
    
