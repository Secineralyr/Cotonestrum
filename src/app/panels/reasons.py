import flet as ft

from core import websocket

class PanelReasons(ft.Container):

    def __init__(self):
        super().__init__()

        self.expand = True
        self.margin = 15
        self.alignment = ft.alignment.top_left


        self.locked = True

        def toggle_lock(e):
            locked = not self.lock.value
            self.set_locked(locked)

        def create_reason(e):
            text = self.tf_adding.value
            if text != '':
                websocket.create_reason(text, self.page)

        self.lock = ft.Switch(
            label='',
            splash_radius=0,
            on_change=toggle_lock,
        )

        self.tf_adding = ft.TextField(
            label='追加したい理由区分',
            border_color='#a0cafd',
            border_width=2,
        )

        self.button_add = ft.FilledButton(
            content=ft.Text(
                value='追加',
                style=ft.TextStyle(weight=ft.FontWeight.BOLD),
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(3),
                padding=18,
            ),
            on_click=create_reason,
            disabled=True,
        )

        self.list_reason = ft.ListView(controls=[])

        self.main_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.tf_adding,
                            self.button_add,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Divider(
                        height=4,
                        thickness=2,
                    ),
                    self.list_reason,
                ],
            ),
            width=400,
            padding=10,
            border_radius=5,
            disabled=True,
        )

        self.content = ft.Column(
            controls=[
                ft.Text(
                    value='理由区分管理',
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    value='''\
理由区分とは「絵文字が危険な理由」の区分です。\
その区分をここで追加・編集・削除することができます。
既に絵文字に割り当てられている理由区分を編集・削除した場合、割り当て先全てに影響します。

なので間違って変更を加えると危険です。デフォルトでロックがかかっています。
編集したい場合は下のスイッチからロックを解除して編集してください。
''',
                ),
                ft.Row(
                    controls=[
                        ft.Icon(name=ft.icons.LOCK, color='#616367'),
                        self.lock,
                        ft.Icon(name=ft.icons.LOCK_OPEN),
                    ],
                ),
                self.main_container,
            ]
        )

    def set_locked(self, locked):
        self.locked = locked
        self.main_container.disabled = locked
        self.button_add.disabled = locked
        for item in self.list_reason.controls:
            item.button_delete.disabled = locked
        self.main_container.update()

    def add_reason(self, rsid, text):
        locked = self.locked

        item = ReasonItem(rsid, text, locked)

        self.list_reason.controls.append(item)
        self.list_reason.update()

    def update_reason(self, rsid, text):
        target: ReasonItem | None = None
        for item in self.list_reason.controls:
            if item.rsid == rsid:
                target = item
                break
        if target is not None:
            target.set_reason_text(text)
            target.update()
        else:
            self.add_reason(rsid, text)

    def remove_reason(self, rsid):
        target: ReasonItem | None = None
        for item in self.list_reason.controls:
            if item.rsid == rsid:
                target = item
                break
        if target is not None:
            self.list_reason.controls.remove(target)
            self.list_reason.update()


class ReasonItem(ft.Row):

    def __init__(self, rsid, text, locked):
        super().__init__()

        self.rsid = rsid
        self._text = text

        def focus_text(e):
            self._text = self.text.value

        def change_text(e):
            if self._text != self.text.value:
                self._text = self.text.value
                text = self.text.value
                websocket.change_reason_text(rsid, text, self.page)

        def delete(e):
            websocket.delete_reason(rsid, self.page)

        self.text = ft.TextField(
            value=text,
            border_color='#a0cafd',
            border_width=2,
            content_padding=ft.padding.symmetric(horizontal=10),
            on_focus=focus_text,
            on_blur=change_text,
            on_submit=change_text,
        )
        self.button_delete = ft.OutlinedButton(
            content=ft.Icon(name=ft.icons.DELETE_OUTLINED),
            style=ft.ButtonStyle(
                color='#ff8080',
                bgcolor='#20ff8080',
                shape=ft.RoundedRectangleBorder(3),
                padding=12,
            ),
            disabled=locked,
            on_click=delete,
        )

        self.controls = [
            self.text,
            self.button_delete,
        ]
        self.alignment = ft.MainAxisAlignment.CENTER
    
    def set_reason_text(self, text):
        self._text = text
        self.text.value = text
        self.page.update()

