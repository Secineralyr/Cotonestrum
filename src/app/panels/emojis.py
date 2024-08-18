import asyncio
import flet as ft

from core import registry
from core import websocket

from app.utils.util import SizeAwareControl


class PanelEmojis(ft.Row):

    def __init__(self):
        super().__init__()

        self.selected: set[EmojiItem] = set()
        self.count_emojis = 0

        self.list_emoji = EmojiList(self)
        self.bulk = EmojiBulkChanger(self)

        self.expand = True
        self.scroll = ft.ScrollMode.ALWAYS

        self.controls = [
            ft.Container(
                width=1839,
                content=ft.Column(
                    expand=True,
                    alignment=ft.alignment.top_left,
                    spacing=0,
                    controls=[
                        EmojiHeader(),
                        ft.Divider(height=1),
                        self.list_emoji,
                        ft.Divider(height=1),
                        self.bulk,
                    ]
                ),
            ),
        ]

    def update_selected(self):
        self.bulk.update_selected()
    
    def all_deselect(self):
        for e in self.selected:
            e.checkbox.value = False
        self.list_emoji.update()
        self.selected.clear()

    def reload_reasons(self):
        self.list_emoji.reload_dropdown()
        self.bulk.reload_dropdown()


class EmojiHeader(ft.Container):
    def __init__(self):
        super().__init__()

        self.height = 50
        self.content = ft.Row(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    width=50,
                    alignment=ft.alignment.center,
                    content=ft.Text(''),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=50,
                    alignment=ft.alignment.center,
                    content=ft.Text('画像'),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=170,
                    alignment=ft.alignment.center,
                    content=ft.Text('名前'),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=140,
                    alignment=ft.alignment.center,
                    content=ft.Text('カテゴリー'),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=220,
                    alignment=ft.alignment.center,
                    content=ft.Text('タグ'),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=50,
                    alignment=ft.alignment.center,
                    content=ft.Text('自作\nフラグ', text_align=ft.TextAlign.CENTER),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=320,
                    alignment=ft.alignment.center,
                    content=ft.Text('ライセンス表記'),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=140,
                    alignment=ft.alignment.center,
                    content=ft.Text('所有者'),
                ),
                ft.VerticalDivider(width=2, thickness=2),
                ft.Container(
                    width=190,
                    alignment=ft.alignment.center,
                    content=ft.Text('危険度'),
                ),
                ft.Container(
                    width=200,
                    alignment=ft.alignment.center,
                    content=ft.Text('理由区分'),
                ),
                ft.Container(
                    width=300,
                    alignment=ft.alignment.center,
                    content=ft.Text('備考'),
                ),
            ]
        )


class EmojiList(ft.ListView):
    def __init__(self, main: PanelEmojis):
        super().__init__()

        self.main = main

        self.emojis: dict[str, EmojiItem] = {}

        self.expand = True

        self.controls = []
    
    def update_emoji(self, eid: str):
        emoji_data = registry.get_emoji(eid)
        if emoji_data is None:
            print(f"Emoji '{eid}' couldn't found in registry.")
            return

        eid = emoji_data.id
        name = emoji_data.name
        category = emoji_data.category
        tags = emoji_data.tags
        url = emoji_data.url
        sm = emoji_data.is_self_made
        license = emoji_data.license
        owner = emoji_data.owner_id
        risk_id = emoji_data.risk_id
        if owner is not None:
            owner = f'<{owner}>'
        
        if eid in self.emojis:
            e: EmojiItem = self.emojis[eid]
            e.update_name(name)
            e.update_category(category)
            e.update_tags(tags)
            e.update_url(url)
            e.update_self_made(sm)
            e.update_license(license)
            e.update_username(owner)
            if e.risk_id != risk_id:
                e.change_risk_id(risk_id)
        else:
            e = EmojiItem(self.main, name, category, tags, url, sm, license, owner, risk_id)
            
            self.emojis[eid] = e

            self.controls.append(e)
            self.update()
            self.main.count_emojis += 1
    
    def delete_emoji(self, eid: str):
        if eid in self.emojis:
            e = self.emojis[eid]
            if e.checkbox.value:
                e.toggle_selected(None)
            
            self.controls.remove(e)
            self.update()
            self.main.count_emojis -= 1

    def reload_dropdown(self):
        for e in self.emojis.values():
            e.reload_dropdown()

class EmojiItem(ft.Container):
    def __init__(self, main: PanelEmojis, name: str, category: str, tags: list[str], url: str, is_self_made: bool, license: str, username: str | None, risk_id: str):
        super().__init__()

        self.main = main

        self.username_resolved = False

        self.name = name
        self.category = category
        self.tags = tags
        self.emoji_url = url
        self.license = license
        if username is not None:
            self.username = username
        else:
            self.username_resolved = True
            self.username = '<Unknown>'
        self.risk_id = risk_id
        self.is_self_made = is_self_made

        def checker_need_tooltip(threshold_width):
            def check_need_tooltip(e: ft.canvas.CanvasResizeEvent):
                canvas = e.control
                if isinstance(canvas.content, ft.Tooltip):
                    tooltip = canvas.content
                    if threshold_width > e.width or tooltip.message == '' or tooltip.message is None:
                        content = tooltip.content
                        canvas.content = content
                        canvas.update()
            return check_need_tooltip

        self.checkbox = ft.Checkbox(
            label='',
            value=False,
            on_change=self.toggle_selected,
        )
        self.emoji_image = ft.Image(
            src=self.emoji_url,
            width=46,
            height=46,
            fit=ft.ImageFit.CONTAIN,
            error_content=ft.Icon(ft.icons.BROKEN_IMAGE, color='#303030'),
        )
        self.emoji_name = SizeAwareControl(
            on_resize=checker_need_tooltip(150),
            content=ft.Tooltip(
                content=ft.Text(self.name, no_wrap=True),
                message=self.name,
                wait_duration=500,
            )
        )
        self.emoji_category = SizeAwareControl(
            on_resize=checker_need_tooltip(120),
            content=ft.Tooltip(
                content=ft.Text(self.category, no_wrap=True),
                message=self.category,
                wait_duration=500,
            )
        )
        self.emoji_tags = SizeAwareControl(
            on_resize=checker_need_tooltip(200),
            content=ft.Tooltip(
                content=ft.Row(
                    spacing=5,
                    tight=True,
                    controls=[
                        ft.Container(
                            padding=5,
                            bgcolor=ft.colors.INDIGO,
                            alignment=ft.alignment.center,
                            border_radius=ft.border_radius.all(3),
                            content=ft.Text(value=tag, size=10),
                        )
                        for tag in self.tags
                    ]
                ),
                message=' '.join(self.tags),
                wait_duration=500,
            )
        )
        self.emoji_self_made = ft.Icon(
            name=ft.icons.CHECK_ROUNDED if self.is_self_made else ft.icons.CLOSE_ROUNDED,
            color='#d0d0d0' if self.is_self_made else '#303030',
        )
        self.emoji_license = SizeAwareControl(
            on_resize=checker_need_tooltip(300),
            content=ft.Tooltip(
                content=ft.Text(self.license, no_wrap=True),
                message=self.license,
                wait_duration=500,
            )
        )
        self.emoji_username = SizeAwareControl(
            on_resize=checker_need_tooltip(120),
            content=ft.Tooltip(
                content=ft.Text(
                    value=self.username,
                    no_wrap=True,
                    style=ft.TextStyle(
                        italic=self.username == '<Unknown>',
                        color='#404040' if self.username == '<Unknown>' else None
                    ),
                ),
                message=self.username,
                wait_duration=500,
            )
        )

        def change_risk_level(e):
            level = None
            match self.risk_level.value:
                case 'risk_0':
                    level = 0
                case 'risk_1':
                    level = 1
                case 'risk_2':
                    level = 2
                case 'risk_3':
                    level = 3
                case _:
                    level = None
            self.change_risk_level(level)

        def change_reason(e):
            rsid = self.reason.content.value
            if self.reason.content.value == 'none':
                rsid = None
            self.reason.update()
            self.change_reason(rsid)

        self._remark = ''

        def focus_remark(e):
            self._remark = self.remark.content.value

        def change_remark(e):
            if self._remark != self.remark.content.value:
                self._remark = self.remark.content.value
                text = self.remark.content.value
                self.change_remark(text)

        self.risk_level = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    ft.Radio(value='risk_0', fill_color='#5bae5b', toggleable=True),
                    ft.Radio(value='risk_1', fill_color='#c1d36e', toggleable=True),
                    ft.Radio(value='risk_2', fill_color='#cdad4b', toggleable=True),
                    ft.Radio(value='risk_3', fill_color='#cc4444', toggleable=True),
                ],
            ),
            on_change=change_risk_level,
            disabled=True,
        )
        self.reason = ft.Container(
            content=ft.Dropdown(
                options=[
                    ft.dropdown.Option(key='none', text=' '),
                ],
                expand=True,
                border_color='transparent',
                filled=True,
                fill_color='#10ffffff',
                content_padding=ft.padding.symmetric(horizontal=10),
                on_change=change_reason,
            ),
            expand=True,
            padding=4,
            disabled=True,
        )
        self.remark = ft.Container(
            content=ft.TextField(
                expand=True,
                border_color='transparent',
                filled=True,
                fill_color='#10ffffff',
                content_padding=ft.padding.symmetric(horizontal=10),
                on_focus=focus_remark,
                on_blur=change_remark,
                on_submit=change_remark,
            ),
            expand=True,
            padding=4,
            disabled=True,
        )

        self.height = 50
        self.content = ft.Row(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    width=50,
                    alignment=ft.alignment.center,
                    content=self.checkbox,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=50,
                    alignment=ft.alignment.center,
                    content=self.emoji_image,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=150,
                    margin=10,
                    alignment=ft.alignment.center_left,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=self.emoji_name,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=120,
                    margin=10,
                    alignment=ft.alignment.center_left,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=self.emoji_category,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=200,
                    margin=10,
                    alignment=ft.alignment.center_left,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=self.emoji_tags,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=50,
                    alignment=ft.alignment.center,
                    content=self.emoji_self_made,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=300,
                    margin=10,
                    alignment=ft.alignment.center_left,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=self.emoji_license,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=120,
                    margin=10,
                    alignment=ft.alignment.center_left,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=self.emoji_username,
                ),
                ft.VerticalDivider(width=2, thickness=2),
                ft.Container(
                    width=190,
                    alignment=ft.alignment.center,
                    content=self.risk_level,
                ),
                ft.Container(
                    width=200,
                    alignment=ft.alignment.center_left,
                    content=self.reason,
                ),
                ft.Container(
                    width=300,
                    alignment=ft.alignment.center_left,
                    content=self.remark,
                ),
            ]
        )
    
    def did_mount(self):
        self.page.run_task(self.get_username)
        self.page.run_task(self.get_risk)

    async def get_username(self):
        while not self.username_resolved:
            user = registry.get_user(self.username[1:-1])
            if user is not None:
                username = user.username
                self.update_username(username)
                self.username_resolved = True
                break
            await asyncio.sleep(1)

    async def get_risk(self):
        while True:
            risk = registry.get_risk(self.risk_id)
            if risk is not None:
                risk_level = risk.level
                reason = risk.reason_genre
                remark = risk.remark
                self.update_risk(risk_level, reason, remark)
                break
            await asyncio.sleep(1)

    def toggle_selected(self, e):
        checked = self.checkbox.value
        if checked:
            self.main.selected.add(self)
        else:
            self.main.selected.discard(self)
        self.main.update_selected()


    def update_name(self, name):
        self.name = name
        self.emoji_name.content = ft.Tooltip(
            content=ft.Text(self.name, no_wrap=True),
            message=self.name,
            wait_duration=500,
        )
        self.emoji_name.update()

    def update_category(self, category):
        self.category = category
        self.emoji_category.content = ft.Tooltip(
            content=ft.Text(self.category, no_wrap=True),
            message=self.category,
            wait_duration=500,
        )
        self.emoji_category.update()

    def update_tags(self, tags):
        self.tags = tags
        self.emoji_tags.content = ft.Tooltip(
            content=ft.Row(
                spacing=5,
                tight=True,
                controls=[
                    ft.Container(
                        padding=5,
                        bgcolor=ft.colors.INDIGO,
                        alignment=ft.alignment.center,
                        border_radius=ft.border_radius.all(3),
                        content=ft.Text(value=tag, size=10),
                    )
                    for tag in self.tags
                ]
            ),
            message=' '.join(self.tags),
            wait_duration=500,
        )
        self.emoji_tags.update()
    
    def update_url(self, url):
        self.url = url
        self.emoji_image.src = url
        self.emoji_image.update()
    
    def update_self_made(self, is_self_made):
        self.is_self_made = is_self_made
        self.emoji_self_made.name = ft.icons.CHECK_ROUNDED if self.is_self_made else ft.icons.CLOSE_ROUNDED
        self.emoji_self_made.color = '#d0d0d0' if self.is_self_made else '#303030'
        self.emoji_self_made.update()
    
    def update_license(self, license):
        self.license = license
        self.emoji_license.content = ft.Tooltip(
            content=ft.Text(self.license, no_wrap=True),
            message=self.license,
            wait_duration=500,
        )
        self.emoji_license.update()

    def update_username(self, username):
        if username.startswith('<') and username.endswith('>'):
            if self.username_resolved:
                self.page.run_task(self.get_username)
            self.username_resolved = False
        else:
            self.username_resolved = True
        
        self.username = username
        self.emoji_username.content = ft.Tooltip(
            content=ft.Text(
                value=self.username,
                no_wrap=True,
                style=ft.TextStyle(
                    italic=self.username == '<Unknown>',
                    color='#404040' if self.username == '<Unknown>' else None
                ),
            ),
            message=self.username,
            wait_duration=500,
        )
        self.emoji_username.update()

    def change_risk_id(self, risk_id):
        if self.risk_id != risk_id:
            self.risk_level.disabled = True
            self.reason.disabled = True
            self.remark.disabled = True
            self.risk_id = risk_id
            self.page.run_task(self.get_risk)
        self.update()

    def update_risk(self, level, reason, remark):
        self.update_risk_level(level, False)
        self.update_reason(reason, False)
        self.update_remark(remark, False)
        if self.checkbox.value:
            self.main.bulk.update_values()
        self.update()

    def update_risk_level(self, level, _update=True):
        self.risk_level.disabled = False
        match level:
            case None:
                self.risk_level.value = None
            case 0:
                self.risk_level.value = 'risk_0'
            case 1:
                self.risk_level.value = 'risk_1'
            case 2:
                self.risk_level.value = 'risk_2'
            case 3:
                self.risk_level.value = 'risk_3'
        if _update:
            self.risk_level.update()
            if self.checkbox.value:
                self.main.bulk.update_values()

    def update_reason(self, rsid, _update=True):
        self.reason.disabled = False
        self.reason.content.value = rsid
        if rsid is not None:
            self.reason.content.hint_text = f'<{rsid}>'
        else:
            self.reason.content.hint_text = ''
        if _update:
            self.reason.update()
            if self.checkbox.value:
                self.main.bulk.update_values()

    def update_remark(self, text, _update=True):
        self.remark.disabled = False
        self.remark.content.value = text
        if _update:
            self.remark.update()
            if self.checkbox.value:
                self.main.bulk.update_values()

    def reload_dropdown(self):
        self.reason.content.options = [ft.dropdown.Option(key='none', text=' ')]
        for rsid in registry.reasons:
            text = registry.reasons[rsid].text
            self.reason.content.options.append(ft.dropdown.Option(key=rsid, text=text))
        self.reason.update()

    def change_risk_level(self, level, _update=True):
        self.update_risk_level(level, _update)
        websocket.change_risk_level(self.risk_id, level, self.page)

    def change_reason(self, rsid, _update=True):
        self.update_reason(rsid, _update)
        websocket.change_reason(self.risk_id, rsid, self.page)

    def change_remark(self, text, _update=True):
        self.update_remark(text, _update)
        websocket.change_remark(self.risk_id, text, self.page)



class EmojiBulkChanger(ft.Container):
    def __init__(self, main: PanelEmojis):
        super().__init__()

        self.main = main

        def all_deselect(e):
            self.disabled = True

            self.select_counter.value = '== 0 emojis selected. =='
            self.checkbox.value = False
            self.risk_level.value = None
            self.reason.content.value = None
            self.remark.content.value = None

            self.update()

            self.main.all_deselect()
        
        self.checkbox = ft.Checkbox(
            label='',
            value=False,
            tristate=True,
            on_change=all_deselect,
        )

        self.select_counter = ft.Text(
            value='== 0 emojis selected. ==',
            style=ft.TextStyle(italic=True),
        )

        def change_risk_level(e):
            match self.risk_level.value:
                case 'risk_0':
                    level = 0
                case 'risk_1':
                    level = 1
                case 'risk_2':
                    level = 2
                case 'risk_3':
                    level = 3
                case _:
                    level = None
            for i in self.main.selected:
                i.change_risk_level(level, False)
            self.main.update()
            self.update_values()

        def change_reason(e):
            rsid = self.reason.content.value
            if self.reason.content.value == 'none':
                rsid = None
            for i in self.main.selected:
                i.change_reason(rsid)
            self.reason.update()
            self.update_values()

        self._remark = ''

        def focus_remark(e):
            self._remark = self.remark.content.value

        def change_remark(e):
            if self._remark != self.remark.content.value:
                self._remark = self.remark.content.value
                text = self.remark.content.value
                for i in self.main.selected:
                    i.change_remark(text, False)
                self.main.update()
                self.update_values()

        self.risk_level = ft.RadioGroup(
            content=ft.Row(
                expand=True,
                controls=[
                    ft.Radio(value='risk_0', toggleable=True, fill_color={
                        ft.ControlState.DISABLED: '#8b8b8b',
                        ft.ControlState.DEFAULT: '#5bae5b',
                    }),
                    ft.Radio(value='risk_1', toggleable=True, fill_color={
                        ft.ControlState.DISABLED: '#c2c2c2',
                        ft.ControlState.DEFAULT: '#c1d36e',
                    }),
                    ft.Radio(value='risk_2', toggleable=True, fill_color={
                        ft.ControlState.DISABLED: '#ababab',
                        ft.ControlState.DEFAULT: '#cdad4b',
                    }),
                    ft.Radio(value='risk_3', fill_color={
                        ft.ControlState.DISABLED: '#6c6c6c',
                        ft.ControlState.DEFAULT: '#cc4444',
                    }),
                ],
            ),
            on_change=change_risk_level,
        )
        self.reason = ft.Container(
            content=ft.Dropdown(
                options=[ft.dropdown.Option(key='none', text=' ')],
                expand=True,
                border_color='transparent',
                filled=True,
                fill_color='#10ffffff',
                content_padding=ft.padding.symmetric(horizontal=10),
                on_change=change_reason,
            ),
            expand=True,
            padding=4,
        )
        self.remark = ft.Container(
            content=ft.TextField(
                expand=True,
                border_color='transparent',
                filled=True,
                fill_color='#10ffffff',
                content_padding=ft.padding.symmetric(horizontal=10),
                on_focus=focus_remark,
                on_blur=change_remark,
                on_submit=change_remark,
            ),
            expand=True,
            padding=4,
        )

        self.half_risk_0 = ft.Icon(name=ft.icons.REMOVE_CIRCLE_OUTLINE_ROUNDED, color='#005bae5b', size=20)
        self.half_risk_1 = ft.Icon(name=ft.icons.REMOVE_CIRCLE_OUTLINE_ROUNDED, color='#00c1d36e', size=20)
        self.half_risk_2 = ft.Icon(name=ft.icons.REMOVE_CIRCLE_OUTLINE_ROUNDED, color='#00cdad4b', size=20)
        self.half_risk_3 = ft.Icon(name=ft.icons.REMOVE_CIRCLE_OUTLINE_ROUNDED, color='#00cc4444', size=20)

        self.disabled = True
        self.height = 50

        self.content = ft.Row(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    width=50,
                    alignment=ft.alignment.center,
                    content=self.checkbox,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=1076,
                    margin=10,
                    alignment=ft.alignment.center_left,
                    content=self.select_counter,
                ),
                ft.VerticalDivider(width=2, thickness=2),
                ft.Stack(
                    width=190,
                    controls=[
                        ft.Container(
                            width=190,
                            alignment=ft.alignment.center,
                            content=ft.Row(
                                spacing=0,
                                controls=[
                                    ft.Row(width=10),
                                    self.half_risk_0,
                                    ft.Row(width=30),
                                    self.half_risk_1,
                                    ft.Row(width=30),
                                    self.half_risk_2,
                                    ft.Row(width=30),
                                    self.half_risk_3,
                                ]
                            )
                        ),
                        ft.Container(
                            width=190,
                            alignment=ft.alignment.center,
                            content=self.risk_level,
                        ),
                    ]
                ),
                ft.Container(
                    width=200,
                    alignment=ft.alignment.center_left,
                    content=self.reason,
                ),
                ft.Container(
                    width=300,
                    alignment=ft.alignment.center_left,
                    content=self.remark,
                ),
            ]
        )

    def update_selected(self):
        nsel = len(self.main.selected)

        self.select_counter.value = f'== {nsel} emojis selected. =='
        if nsel == 0:
            self.disabled = True
            self.checkbox.value = False
        else:
            self.disabled = False
            if nsel == self.main.count_emojis:
                self.checkbox.value = True
            else:
                self.checkbox.value = None
        self.update_values()

    def update_values(self):
        nsel = len(self.main.selected)
        if nsel == 0:
            self.risk_level.value = None
            self.reason.content.value = None
            self.reason.content.hint_text = ''
            self.remark.content.value = None
            self.half_risk_0.color = '#005bae5b'
            self.half_risk_1.color = '#00c1d36e'
            self.half_risk_2.color = '#00cdad4b'
            self.half_risk_3.color = '#00cc4444'
        elif nsel == 1:
            e = list(self.main.selected)[0]
            common_risk_level = e.risk_level.value
            common_reason = e.reason.content.value
            common_remark = e.remark.content.value
            if common_reason == '': common_reason = None
            if common_remark == '': common_remark = None
            
            self.risk_level.value = common_risk_level
            self.half_risk_0.color = '#005bae5b'
            self.half_risk_1.color = '#00c1d36e'
            self.half_risk_2.color = '#00cdad4b'
            self.half_risk_3.color = '#00cc4444'
            self.reason.content.value = common_reason
            if common_reason is not None:
                self.reason.content.hint_text = f'<{common_reason}>'
            else:
                self.reason.content.hint_text = ''
            self.remark.content.value = common_remark
        else:
            is_common_risk_level = True
            is_common_reason = True
            is_common_remark = True

            contains_risk = [False, False, False, False]
            common_risk_level = list(self.main.selected)[0].risk_level.value
            common_reason = list(self.main.selected)[0].reason.content.value
            common_remark = list(self.main.selected)[0].remark.content.value
            if common_reason == '': common_reason = None
            if common_remark == '': common_remark = None
            
            match common_risk_level:
                case 'risk_0':
                    contains_risk[0] = True
                case 'risk_1':
                    contains_risk[1] = True
                case 'risk_2':
                    contains_risk[2] = True
                case 'risk_3':
                    contains_risk[3] = True
            
            for e in list(self.main.selected)[1:]:
                risk_level = e.risk_level.value
                reason = e.reason.content.value
                remark = e.remark.content.value
                if reason == '': reason = None
                if remark == '': remark = None

                is_common_risk_level = is_common_risk_level and common_risk_level == risk_level
                is_common_reason = is_common_reason and common_reason == reason
                is_common_remark = is_common_remark and common_remark == remark

                match risk_level:
                    case 'risk_0':
                        contains_risk[0] = True
                    case 'risk_1':
                        contains_risk[1] = True
                    case 'risk_2':
                        contains_risk[2] = True
                    case 'risk_3':
                        contains_risk[3] = True
            
            if is_common_risk_level:
                self.risk_level.value = common_risk_level
                self.half_risk_0.color = '#005bae5b'
                self.half_risk_1.color = '#00c1d36e'
                self.half_risk_2.color = '#00cdad4b'
                self.half_risk_3.color = '#00cc4444'
            else:
                self.risk_level.value = None
                self.half_risk_0.color = '#5bae5b' if contains_risk[0] else '#005bae5b'
                self.half_risk_1.color = '#c1d36e' if contains_risk[1] else '#00c1d36e'
                self.half_risk_2.color = '#cdad4b' if contains_risk[2] else '#00cdad4b'
                self.half_risk_3.color = '#cc4444' if contains_risk[3] else '#00cc4444'
            if is_common_reason:
                self.reason.content.value = common_reason
                if common_reason is not None:
                    self.reason.content.hint_text = f'<{common_reason}>'
                else:
                    self.reason.content.hint_text = ''
            else:
                self.reason.content.value = '<Mixed>'
                self.reason.content.hint_text = '<Mixed>'
            if is_common_remark:
                self.remark.content.value = common_remark
            else:
                self.remark.content.value = '<Mixed>'
        self.update()


    def reload_dropdown(self):
        self.reason.content.options = [ft.dropdown.Option(key='none', text=' ')]
        for rsid in registry.reasons:
            text = registry.reasons[rsid].text
            self.reason.content.options.append(ft.dropdown.Option(key=rsid, text=text))
        self.reason.update()

