import flet as ft


class PanelUsers(ft.Container):

    def __init__(self):
        super().__init__()

        self.expand = True
        self.margin = 15
        self.alignment = ft.alignment.top_left

        self.content = ft.Column(
            controls=[
                ft.Text(
                    value='ユーザー',
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    value='未実装',
                ),
            ]
        )

