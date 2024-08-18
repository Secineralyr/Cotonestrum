import json

import flet as ft


class PanelLogs(ft.Container):

    def __init__(self):
        super().__init__()

        self.log_view = ft.ListView(
            expand=True,
            first_item_prototype=True,
            spacing=10,
        )

        def navigate_to_bottom(e):
            self.log_view.scroll_to(offset=-1, duration=1000)

        self.button_navigate_to_bottom = ft.FloatingActionButton(
            icon=ft.icons.KEYBOARD_DOUBLE_ARROW_DOWN_ROUNDED,
            on_click=navigate_to_bottom, 
        )

        self.expand = True
        self.margin = 15

        self.content=ft.Column(
            controls=[
                ft.Text(
                    value='ログ/タスク',
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(
                    content=ft.Stack(
                        controls=[
                            self.log_view,
                            ft.Container(
                                content=self.button_navigate_to_bottom,
                            ),
                        ],
                        alignment=ft.alignment.bottom_right,
                    ),
                    expand=True,
                ),
            ],
        )

    def write_log(self, subject: str, text: str, data: dict = None, error: bool = False):
        if not error:
            # More items will take too long to processing.
            # I want to figure out some way to not need to do this.
            return
        if text == '':
            inner = []
        else:
            inner = [
                ft.Row(
                    controls=[
                        ft.Text(
                            value=text,
                        ),
                    ],
                ),
                ft.Row(height=3),
            ]
        
        inner.extend(
            [
                ft.Text(
                    value='RAW DATA',
                    color='#808080',
                    font_family='M PLUS 1 Code',
                    size=10,
                    style=ft.TextStyle(
                        weight=ft.FontWeight.W_900,
                    ),
                    scale=ft.transform.Scale(scale_x=1, scale_y=0.8),
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            value=json.dumps(data, ensure_ascii=False, indent=2, separators=(',', ': ')),
                            color='#a0a0a0',
                            font_family='M PLUS 1 Code',
                        ),
                    ],
                ),
            ]
        )

        item = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    value=subject,
                                    no_wrap=True,
                                ),
                                width=800,
                                expand=1,
                                padding=ft.padding.symmetric(horizontal=5),
                                alignment=ft.alignment.center_left,
                                bgcolor='#20d0e0f0',
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=inner,
                                    expand=True,
                                    spacing=0,
                                    scroll=ft.ScrollMode.AUTO,
                                ),
                                width=800,
                                expand=7,
                                padding=ft.padding.only(left=5),
                                alignment=ft.alignment.top_left,
                                bgcolor='#18d0e0f0',
                            ),
                        ],
                        expand=True,
                        spacing=0,
                    ),
                    border=ft.border.all(2, '#80d0e0f0'),
                    border_radius=5,
                ),
            ],
            height=200,
        )
        key = str(len(self.log_view.controls))
        item.key = key
        self.log_view.controls.append(item)
        if error:
            self.page.data['sidebar'].button_logs.increment_badge_value()
        self.log_view.update()

