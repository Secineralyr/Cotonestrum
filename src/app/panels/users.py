import flet as ft


class PanelUsers(ft.Container):

    def __init__(self):
        super().__init__()

        self.expand = True

        self.content = ft.TextField(
            value='user',
            expand=True
        )
    
