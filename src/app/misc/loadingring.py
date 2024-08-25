import flet as ft

class LoadingRing(ft.Container):

    def __init__(self):
        super().__init__()

        self.counter = 0


        self.bgcolor='#40000000'

        self.margin = 5

        self.width = 0
        self.height = 40
        self.border_radius = 20

        self.offset = ft.Offset(1.0, 0.0)
        self.animate_offset = ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT_QUAD)
        self.animate_size = ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT_QUAD)

        self.text = ft.Text(
            value='',
            color='#c3c7cf',
            text_align=ft.TextAlign.CENTER,
            style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        )

        self.content = ft.Row(
            controls=[
                ft.Container(
                    content=ft.ProgressRing(
                        color='#c3c7cf',
                        stroke_cap=ft.StrokeCap.ROUND,
                        stroke_align=-5.0,
                        stroke_width=3,
                        value=None,
                    ),
                    width=40,
                    height=40,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=self.text,
                    width=20,
                    height=40,
                    alignment=ft.alignment.center,
                    offset=ft.Offset(-0.25, 0.0),
                ),
            ],
            alignment=ft.alignment.center_left,
            spacing=0,
        )


    def hide(self, enforce=False):
        if not enforce:
            self.counter -= 1
            if self.counter >= 1:
                self.width = 60 if self.counter > 1 else 40
                self.text.value = str(self.counter) if self.counter > 1 else ''
                self.text.update()
            if self.counter == 0:
                self.width = 0
                self.offset = ft.Offset(1.0, 0.0)
                self.update()
            if self.counter < 0:
                self.counter = 0
        else:
            self.counter = 0
            self.text.value = ''
            self.width = 0
            self.offset = ft.Offset(1.0, 0.0)
            self.update()

    def show(self):
        self.counter += 1
        self.width = 60 if self.counter > 1 else 40
        if self.counter > 1:
            self.text.value = str(self.counter)
            self.text.update()
        self.offset = ft.Offset(0.0, 0.0)
        self.update()

