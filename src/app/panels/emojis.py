import re
import csv
import traceback
import asyncio

import flet as ft

from app.panels.logs import PanelLogs
from app.utils.data import KeyboardBehaviorData
from core import registry
from core import websocket
from core.filtering import EmojiFilter
from core.filtering import SelectionIsSelfMade, SelectionRiskLevel, SelectionReasonGenre, SelectionCheckStatus

from app.utils.control import SizeAwareControl
from app.utils.control import IOSAlignment
from app.utils import func
from app.resources.texts import TEXT_FIELDS
from app.misc.loadingring import LoadingRing
from app.sidebar import Sidebar

TEXTS = TEXT_FIELDS.EMOJIS

class PanelEmojis(ft.Row):

    def __init__(self):
        super().__init__()

        self._locks = 0

        self.all_emojis = {} # Use dict with value=None because python doesn't has ordered set.

        self.filter = EmojiFilter.no_filter()
        self.filtered_emojis = {}

        self.selected: set[EmojiItem] = set()
        self.multiselect_origin: EmojiItem | None = None

        self.count_emojis = 0

        self.header = EmojiHeader(self)
        self.list_emoji = EmojiList(self)
        self.bulk = EmojiBulkChanger(self)

        self.expand = True
        self.scroll = ft.ScrollMode.ALWAYS

        self.loading = False

        self.controls = [
            ft.Container(
                width=1839,
                content=ft.Column(
                    expand=True,
                    alignment=ft.alignment.top_left,
                    spacing=0,
                    controls=[
                        self.header,
                        ft.Divider(height=1),
                        self.list_emoji,
                        ft.Divider(height=1),
                        self.bulk,
                    ]
                ),
            ),
        ]

    def add_emoji(self, eid: str):
        self.all_emojis[eid] = None
        if self.filter.filter(eid):
            self.filtered_emojis[eid] = None
            if eid in self.list_emoji.emojis:
                self.list_emoji.update_emoji(eid)

    def remove_emoji(self, eid: str):
        if eid in self.all_emojis:
            self.list_emoji.delete_emoji(eid)
            del self.all_emojis[eid]
            if eid in self.filtered_emojis:
                del self.filtered_emojis[eid]

    def add_emojis(self, eids: list[str]):
        need_update = []
        for eid in eids:
            self.all_emojis[eid] = None
            if self.filter.filter(eid):
                self.filtered_emojis[eid] = None
                if eid in self.list_emoji.emojis:
                    need_update.append(eid)
        self.list_emoji.update_emojis(need_update)

    def remove_emojis(self, eids: list[str]):
        eeids = []
        for eid in eids:
            if eid in self.all_emojis:
                eeids.append(eid)
        self.list_emoji.delete_emojis(eeids)
        for eid in eeids:
            del self.all_emojis[eid]
            if eid in self.filtered_emojis:
                del self.filtered_emojis[eid]

    def lock(self):
        lr: LoadingRing = self.page.data['loading']
        sidebar: Sidebar = self.page.data['sidebar']
        sidebar.lock_buttons()
        lr.show()
        self._locks += 1

    def unlock(self):
        lr: LoadingRing = self.page.data['loading']
        sidebar: Sidebar = self.page.data['sidebar']
        lr.hide()
        self._locks -= 1
        if self._locks == 0:
            sidebar.unlock_buttons()

    def unload_all(self):
        self.bulk.all_deselect(None)
        self.list_emoji.delete_all_emojis()
        self.list_emoji.update()

    def load_next(self, count=50):
        if self.loading: return
        self.loading = True
        self.lock()
        if len(self.list_emoji.controls) > 0:
            if isinstance(self.list_emoji.controls[-1], MoreLoad):
                del self.list_emoji.controls[-1]
        eids = [eid for eid in self.filtered_emojis if eid not in self.list_emoji.emojis.keys()]
        if len(eids) > count:
            eids = eids[:count]
        self.list_emoji.update_emojis(eids, False)
        self.list_emoji.controls.append(MoreLoad(self))
        self.list_emoji.update()
        self.unlock()
        self.loading = False

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

    def open_filtering_menu(self):
        self.page.show_dialog(FilteringDialog(self))

    def update_filter(self, filter: EmojiFilter):
        self.filter = filter
        self.header.set_filtering_status(filter.get_filter_status())
        eids = list(self.all_emojis.keys())
        self.filtered_emojis = {eid: None for eid in filter.filter_all(eids)}
        self.unload_all()
        self.load_next()

    def write_csv(self, eids, filename) -> int | None:
        panel_logs: PanelLogs = self.page.data['logs']
        try:
            with open(filename, 'wt', encoding='utf-8', newline='') as fs:
                writer = csv.writer(fs)
                writer.writerow(['ID', '絵文字名', 'カテゴリー', 'タグ', 'URL', '自作フラグ', 'ライセンス表記', '所有者', '危険度', '理由区分', '備考', '状態'])
                for eid in eids:
                    emoji_data = registry.get_emoji(eid)

                    misskey_id = emoji_data.misskey_id
                    name = emoji_data.name
                    category = emoji_data.category
                    tags = emoji_data.tags
                    url = emoji_data.url
                    if emoji_data.is_self_made:
                        is_self_made = 'はい'
                    else:
                        is_self_made = 'いいえ'
                    license = emoji_data.license

                    owner_data = registry.get_user(emoji_data.owner_id)
                    risk_data = registry.get_risk(emoji_data.risk_id)

                    if owner_data is not None:
                        username = owner_data.username
                    else:
                        username = '<不明>'

                    if risk_data is not None:
                        match risk_data.level:
                            case None:
                                level = '<未設定>'
                            case 0:
                                level = '低'
                            case 1:
                                level = '中'
                            case 2:
                                level = '高'
                            case 3:
                                level = '重大'
                            case _:
                                level = '<不明>'

                        reason_data = registry.get_reason(risk_data.reason_genre)
                        if reason_data is not None:
                            reason_text = reason_data.text
                        else:
                            # unreachable if work correctly
                            reason_text = '<不明>'

                        remark = risk_data.remark

                        match risk_data.checked:
                            case 0:
                                checked = '要チェック'
                            case 1:
                                checked = 'チェック済'
                            case 2:
                                checked = '要再チェック(絵文字更新済)'
                            case _:  # unreachable if work correctly
                                checked = '<不明>'
                    else:
                        # unreachable if work correctly
                        level = '<不明>'
                        reason_text = '<不明>'
                        remark = '<不明>'
                        checked = '<不明>'

                    writer.writerow([misskey_id, name, category, tags, url, is_self_made, license, username, level, reason_text, remark, checked])
            succeed = True
        except Exception:
            panel_logs.write_log("white_csv process exception", traceback.format_exc(), None, True)
            traceback.print_exc()
            succeed = False
        return succeed

    def export_csv(self):
        if self.loading: return
        self.loading = True
        self.lock()

        eids = [eid for eid in self.filtered_emojis]
        if len(eids) > 0:
            if self.write_csv(eids, 'out_emojis.csv'):
                ret = len(eids)
            else:
                ret = None
        else:
            ret = 0

        self.unlock()
        self.loading = False

        return ret

    def export_selected_csv(self):
        if self.loading: return
        self.loading = True
        self.lock()

        eids = [eid for eid, emoji in self.list_emoji.emojis.items() if emoji.checkbox.value]
        if len(eids) > 0:
            if self.write_csv(eids, 'out_emojis.csv'):
                ret = len(eids)
            else:
                ret = None
        else:
            ret = 0

        self.unlock()
        self.loading = False

        return ret


class EmojiHeader(ft.Container):
    def __init__(self, main: PanelEmojis):
        super().__init__()

        self.main = main

        self.filter_enabled = False

        def open_actions_menu(e):
            self.page.show_dialog(ActionsDialog(main, self.filter_enabled))

        self.actions = ft.Container(
            content=ft.Icon(
                name=ft.icons.MENU_ROUNDED,
                color='#c0c0c0',
            ),
            expand=True,
            border_radius=4,
            alignment=ft.alignment.center,
            margin=4,
            ink=True,
            on_click=open_actions_menu,
            disabled=False,
        )

        self.height = 50
        self.content = ft.Row(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    width=50,
                    alignment=ft.alignment.center,
                    content=self.actions,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=50,
                    alignment=ft.alignment.center,
                    content=ft.Text(TEXTS.IMAGE),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=160,
                    alignment=ft.alignment.center,
                    content=ft.Text(TEXTS.NAME),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=140,
                    alignment=ft.alignment.center,
                    content=ft.Text(TEXTS.CATEGORY),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=220,
                    alignment=ft.alignment.center,
                    content=ft.Text(TEXTS.TAG),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=50,
                    alignment=ft.alignment.center,
                    content=ft.Text(TEXTS.SELFMADE, text_align=ft.TextAlign.CENTER),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=240,
                    alignment=ft.alignment.center,
                    content=ft.Text(TEXTS.LICENSE),
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    width=140,
                    alignment=ft.alignment.center,
                    content=ft.Text(TEXTS.OWNER),
                ),
                ft.VerticalDivider(width=2, thickness=2),
                ft.Container(
                    width=190,
                    alignment=ft.alignment.center,
                    content=ft.Text(TEXTS.RISK_LEVEL),
                ),
                ft.Container(
                    width=240,
                    alignment=ft.alignment.center,
                    content=ft.Text(TEXTS.REASON_GENRE),
                ),
                ft.Container(
                    width=300,
                    alignment=ft.alignment.center,
                    content=ft.Text(TEXTS.REMARK),
                ),
                ft.Container(
                    width=40,
                    alignment=ft.alignment.center,
                    content=ft.Text(TEXTS.CHECK_STATUS),
                ),
                ft.Container(width=10),
            ]
        )

    def set_filtering_status(self, enable: bool):
        self.filter_enabled = enable
        self.actions.content.color = '#40ff40' if self.filter_enabled else '#c0c0c0'
        self.actions.content.update()

class EmojiList(ft.ListView):
    def __init__(self, main: PanelEmojis):
        super().__init__()

        self.main = main

        self.emojis: dict[str, EmojiItem] = {}

        self.expand = True

        self.item_extent = 50

        self.controls = []

    def update_emoji(self, eid: str, _update=True):
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
            if _update:
                self.update()
            self.main.count_emojis += 1

    def update_emojis(self, eids: list[str], _update=True):
        for eid in eids:
            self.update_emoji(eid, False)
        if _update:
            self.update()

    def delete_emoji(self, eid: str, _update=True):
        if eid in self.emojis:
            e = self.emojis[eid]
            if e.checkbox.value:
                e.toggle_selected(None)
            if e == self.main.multiselect_origin:
                self.main.multiselect_origin = None

            self.controls.remove(e)
            if _update:
                self.update()
            del self.emojis[eid]
            self.main.count_emojis -= 1

    def delete_emojis(self, eids: list[str]):
        for eid in eids:
            self.delete_emoji(eid, False)
        self.update()

    def delete_all_emojis(self):
        for eid in list(self.emojis.keys()):
            self.delete_emoji(eid, False)
        self.update()

    def reload_risk(self, rid: str):
        for e in self.emojis.values():
            if e.risk_id == rid:
                risk = registry.get_risk(rid)
                level = risk.level
                reason = risk.reason_genre
                remark = risk.remark
                status = risk.checked
                e.update_risk(level, reason, remark, status)

    def reload_dropdown(self):
        for e in self.emojis.values():
            e.reload_dropdown()

class EmojiItem(ft.Container):
    def __init__(self, main: PanelEmojis, name: str, category: str, tags: list[str], url: str, is_self_made: bool, license: str, username: str | None, risk_id: str):
        super().__init__()

        self.main = main

        self.username_resolved = False
        self.dropdown_keys = []

        self.name = name
        self.category = category
        self.tags = tags
        self.emoji_url = url
        self.license = license
        if username is not None:
            self.username = username
        else:
            self.username_resolved = True
            self.username = TEXTS.USERNAME_UNRESOLVED
        self.risk_id = risk_id
        self.is_self_made = is_self_made

        # 上書き用urlが存在するなら絵文字の画像urlを上書きする
        override_image_url = main.page.data['settings'].override_image_url
        if override_image_url is not None:
            override_emoji_url: str = override_image_url.value
            if override_emoji_url is not None and len(override_emoji_url.strip()) > 0:
                self.emoji_url = re.sub(r'(https?://)[a-zA-Z0-9\-\.:]+(/.*)$', r'\g<1>' + override_emoji_url + r'\g<2>', self.emoji_url)

        self.status_value = 0

        self.checkbox = ft.Checkbox(
            label='',
            value=False,
            on_change=self.toggle_selected,
        )
        def show_image(e):
            self.page.show_dialog(
                ft.AlertDialog(
                    title=ft.Text(TEXTS.IMAGE_DIALOG_TITLE),
                    title_padding=10,
                    content=ft.Image(
                        src=self.emoji_url,
                        error_content=ft.Icon(ft.icons.BROKEN_IMAGE, color='#303030'),
                    )
                )
            )
        self.emoji_image = ft.Container(
            content=ft.Image(
                src=self.emoji_url,
                width=46,
                height=46,
                fit=ft.ImageFit.CONTAIN,
                error_content=ft.Icon(ft.icons.BROKEN_IMAGE, color='#303030'),
            ),
            on_click=show_image,
        )
        self.emoji_name = ft.Container(
            content=SizeAwareControl(
                on_resize=self.create_checker_need_tooltip(140, self.name),
                content=ft.Container(ft.Text(self.name, no_wrap=True),),
            ),
            expand=True,
        )
        def hover_name(e):
            self.copy_icon.opacity = 1. if e.data == 'true' else 0.
            self.copy_icon.update()
        self.copy_icon = ft.Container(
            ft.Icon(
                name=ft.icons.COPY,
                size=18,
            ),
            opacity=0.,
            animate_opacity=300,
        )
        self.emoji_name_container = ft.Container(
            ft.Stack(
                controls=[
                    IOSAlignment(
                        content=self.copy_icon,
                        horizontal=ft.MainAxisAlignment.END,
                        vertical=ft.MainAxisAlignment.CENTER,
                    ),
                    IOSAlignment(
                        content=self.emoji_name,
                        horizontal=ft.MainAxisAlignment.START,
                        vertical=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.alignment.center_left,
            ),
            expand=True,
            padding=5,
            margin=5,
            border_radius=3,
            ink=True,
            on_click=self.create_copier(self.name),
            on_hover=hover_name,
        )
        self.emoji_category = ft.Container(
            content=SizeAwareControl(
                on_resize=self.create_checker_need_tooltip(120, self.category),
                content=ft.Container(ft.Text(self.category, no_wrap=True)),
            ),
            expand=True,
        )
        self.emoji_tags = ft.Container(
            content=SizeAwareControl(
                on_resize=self.create_checker_need_tooltip(200, ' '.join(self.tags)),
                content=ft.Container(ft.Row(
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
                )),
            ),
            expand=True,
        )
        self.emoji_self_made = ft.Icon(
            name=ft.icons.CHECK_ROUNDED if self.is_self_made else ft.icons.CLOSE_ROUNDED,
            color='#d0d0d0' if self.is_self_made else '#303030',
        )
        spans = []
        for is_url, text in func.detect_url(self.license):
            if is_url:
                span = ft.TextSpan(
                    text=text,
                    style=ft.TextStyle(
                        decoration=ft.TextDecoration.UNDERLINE,
                    ),
                    on_click=lambda e: self.page.launch_url(url=text),  # noqa: B023
                )
            else:
                span = ft.TextSpan(text=text)
            spans.append(span)
        self.emoji_license = ft.Container(
            content=SizeAwareControl(
                on_resize=self.create_checker_need_tooltip(220, self.license),
                content=ft.Container(
                    content=ft.Text(
                        value='',
                        spans=spans,
                        no_wrap=True,
                    )
                ),
            ),
            expand=True,
        )
        self.emoji_username = ft.Container(
            content=SizeAwareControl(
                on_resize=self.create_checker_need_tooltip(120, self.username),
                content=ft.Container(ft.Text(
                    value=self.username,
                    no_wrap=True,
                    style=ft.TextStyle(
                        italic=self.username == '<Unknown>',
                        color='#404040' if self.username == '<Unknown>' else None
                    ),
                )),
            ),
            expand=True,
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
            self.change_reason(rsid)

        self._remark = ''

        def focus_remark(e):
            self._remark = self.remark.content.value

        def change_remark(e):
            if self._remark != self.remark.content.value:
                self._remark = self.remark.content.value
                text = self.remark.content.value
                self.change_remark(text)

        def change_status(e):
            match self.status_value:
                case 0:
                    self.change_status(1)
                case 1:
                    self.change_status(0)
                case 2:
                    self.change_status(1)

        self.risk_level = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Radio(value='risk_0', fill_color='#5bae5b', toggleable=True),
                        width=40,
                    ),
                    ft.Container(
                        ft.Radio(value='risk_1', fill_color='#c1d36e', toggleable=True),
                        width=40,
                    ),
                    ft.Container(
                        ft.Radio(value='risk_2', fill_color='#cdad4b', toggleable=True),
                        width=40,
                    ),
                    ft.Container(
                        ft.Radio(value='risk_3', fill_color='#cc4444', toggleable=True),
                        width=40,
                    ),
                ],
                spacing=10,
            ),
            on_change=change_risk_level,
            disabled=True,
        )
        self.reason = ft.Container(
            content=ft.Dropdown(
                options=[
                    ft.dropdown.Option(key='none', text=' '),
                ],
                value='none',
                expand=True,
                border_color='transparent',
                filled=True,
                fill_color='#10ffffff',
                text_size=14,
                content_padding=ft.padding.symmetric(horizontal=10),
                on_change=change_reason,
            ),
            alignment=ft.alignment.center_left,
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
        self.status = ft.Container(
            content=ft.Icon(
                name=ft.icons.ERROR_ROUNDED,
                color='#cdad4b',
            ),
            tooltip=ft.Tooltip(
                message=TEXTS.NEED_CHECK,
                wait_duration=1000,
            ),
            expand=True,
            border_radius=4,
            alignment=ft.alignment.center,
            margin=4,
            ink=True,
            on_click=change_status,
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
                    width=160,
                    alignment=ft.alignment.center_left,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=self.emoji_name_container,
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
                    width=220,
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
                    width=240,
                    alignment=ft.alignment.center_left,
                    content=self.reason,
                ),
                ft.Container(
                    width=300,
                    alignment=ft.alignment.center_left,
                    content=self.remark,
                ),
                ft.Container(
                    width=40,
                    alignment=ft.alignment.center_left,
                    content=self.status,
                ),
                ft.Container(width=10),
            ]
        )

    def did_mount(self):
        self.reload_dropdown()
        self.page.run_task(self.get_username)
        self.page.run_task(self.get_risk)

    def create_copier(self, text: str):
        def copy_emoji_name(e):
            self.page.set_clipboard(text)
            if self.copy_icon.opacity == 0.:
                self.copy_icon.opacity = 1.
                self.copy_icon.update()
                async def icon_off():
                    await asyncio.sleep(0.3)
                    self.copy_icon.opacity = 0.
                    self.copy_icon.update()
                self.page.run_task(icon_off)
        return copy_emoji_name


    def create_checker_need_tooltip(self, threshold_width, message):
        def check_need_tooltip(e: ft.canvas.CanvasResizeEvent):
            if not self.page.data['settings'].enable_tooltip: return
            if message not in ['', None]:
                canvas = e.control.content
                content = canvas.content
                if content.tooltip is None:
                    if threshold_width <= e.width:
                        content.tooltip = ft.Tooltip(
                            message=message,
                            wait_duration=500,
                        )
                        content.update()
        return check_need_tooltip


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
                status = risk.checked
                self.update_risk(risk_level, reason, remark, status)
                break
            await asyncio.sleep(1)

    def toggle_selected(self, e: ft.ControlEvent):
        checked = self.checkbox.value if self.checkbox.value is not None else False

        keyboard_behavior: KeyboardBehaviorData = self.page.data['keyboard_behavior']

        if not keyboard_behavior.shift or self.main.multiselect_origin is None:
            # shiftが押されていない or 選択の開始位置がない場合(絵文字削除に起因) -> 単純な一項目のトグル
            if checked:
                self.main.selected.add(self)
            else:
                self.main.selected.discard(self)
            self.main.multiselect_origin = self
        else:
            if not keyboard_behavior.ctrl:
                # shiftが押されていてctrlは押されていない場合 -> 排他的な範囲選択
                self._toggle_selected_multiple_exclusive()
            else:
                # shiftが押されていてctrlも押されている場合 -> 範囲選択
                self._toggle_selected_multiple()
        self.main.update_selected()

    def _toggle_selected_multiple_exclusive(self):
        """排他的な複数選択の処理 (範囲外の項目は選択解除)"""

        # そのEmojiItemがListの何番目に属しているかわからないので調べる
        # 全てのEmojiItemがEmojiListにあることが前提
        emojis = list(self.main.list_emoji.emojis.values())
        current_item_index = emojis.index(self)
        origin_item_index = emojis.index(self.main.multiselect_origin)

        start_index = min(current_item_index, origin_item_index)
        end_index = max(current_item_index, origin_item_index)

        for index, emoji in enumerate(emojis):
            if index >= start_index and index <= end_index:
                target = True
            else:
                target = False
            if emoji.checkbox.value != target or emoji == self:
                emoji.checkbox.value = target
                emoji.checkbox.update()
                if target:
                    self.main.selected.add(emoji)
                else:
                    self.main.selected.discard(emoji)

    def _toggle_selected_multiple(self):
        """複数選択の処理 (範囲外の項目は選択維持)"""

        emojis = list(self.main.list_emoji.emojis.values())
        current_item_index = emojis.index(self)
        origin_item_index = emojis.index(self.main.multiselect_origin)

        start_index = min(current_item_index, origin_item_index)
        end_index = max(current_item_index, origin_item_index)

        for index, emoji in enumerate(emojis):
            if index >= start_index and index <= end_index:
                target = True
            else:
                continue
            if emoji.checkbox.value != target or emoji == self:
                emoji.checkbox.value = target
                emoji.checkbox.update()
                if target:
                    self.main.selected.add(emoji)
                else:
                    self.main.selected.discard(emoji)

    def update_name(self, name):
        self.name = name
        self.emoji_name.content = SizeAwareControl(
            on_resize=self.create_checker_need_tooltip(140, self.name),
            content=ft.Container(ft.Text(self.name, no_wrap=True),)
        )
        self.emoji_name.update()

    def update_category(self, category):
        self.category = category
        self.emoji_category.content = SizeAwareControl(
            on_resize=self.create_checker_need_tooltip(120, self.category),
            content=ft.Container(ft.Text(self.category, no_wrap=True)),
        )
        self.emoji_category.update()

    def update_tags(self, tags):
        self.tags = tags
        self.emoji_tags.content = SizeAwareControl(
            on_resize=self.create_checker_need_tooltip(200, ' '.join(self.tags)),
            content=ft.Container(ft.Row(
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
            )),
        )
        self.emoji_tags.update()

    def update_url(self, url):
        self.url = url
        self.emoji_image.content.src = url
        self.emoji_image.content.update()

    def update_self_made(self, is_self_made):
        self.is_self_made = is_self_made
        self.emoji_self_made.name = ft.icons.CHECK_ROUNDED if self.is_self_made else ft.icons.CLOSE_ROUNDED
        self.emoji_self_made.color = '#d0d0d0' if self.is_self_made else '#303030'
        self.emoji_self_made.update()

    def update_license(self, license):
        self.license = license
        spans = []
        for is_url, text in func.detect_url(self.license):
            if is_url:
                span = ft.TextSpan(
                    text=text,
                    style=ft.TextStyle(
                        decoration=ft.TextDecoration.UNDERLINE,
                    ),
                    on_click=lambda e: self.page.launch_url(url=text),  # noqa: B023
                )
            else:
                span = ft.TextSpan(text=text)
            spans.append(span)
        self.emoji_license.content = SizeAwareControl(
            on_resize=self.create_checker_need_tooltip(220, self.license),
            content=ft.Container(
                content=ft.Text(
                    value='',
                    spans=spans,
                    no_wrap=True,
                )
            ),
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
        self.emoji_username.content = SizeAwareControl(
            on_resize=self.create_checker_need_tooltip(120, self.username),
            content=ft.Container(ft.Text(
                value=self.username,
                no_wrap=True,
                style=ft.TextStyle(
                    italic=self.username == '<Unknown>',
                    color='#404040' if self.username == '<Unknown>' else None
                ),
            )),
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

    def update_risk(self, level, reason, remark, status):
        self.update_risk_level(level, False)
        self.update_reason(reason, False)
        self.update_remark(remark, False)
        self.update_status(status, False)
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
            if rsid in self.dropdown_keys:
                self.reason.content.hint_text = ''
            else:
                self.reason.content.hint_text = '<{rsid}>'
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

    def update_status(self, status, _update=True):
        self.status.disabled = False
        self.status_value = status
        match status:
            case 0:
                self.status.content.name = ft.icons.ERROR
                self.status.content.color = '#cdad4b'
                self.status.tooltip.message = TEXTS.NEED_CHECK
            case 1:
                self.status.content.name = ft.icons.CHECK
                self.status.content.color = '#5bae5b'
                self.status.tooltip.message = TEXTS.CHECKED
            case 2:
                self.status.content.name = ft.icons.ERROR_OUTLINE
                self.status.content.color = '#c1d36e'
                self.status.tooltip.message = TEXTS.NEED_RECHECK
        if _update:
            self.status.update()
            if self.checkbox.value:
                self.main.bulk.update_values()

    def reload_dropdown(self):
        dropdown_keys = []
        self.reason.content.options = [ft.dropdown.Option(key='none', text=' ')]
        for rsid in registry.reasons:
            text = registry.reasons[rsid].text
            self.reason.content.options.append(ft.dropdown.Option(key=rsid, text=text))
            dropdown_keys.append(rsid)
        self.dropdown_keys = dropdown_keys
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

    def change_status(self, status, _update=True):
        self.update_status(status, _update)
        websocket.change_status(self.risk_id, status, self.page)

class MoreLoad(ft.Container):
    def __init__(self, main: PanelEmojis):
        super().__init__()

        self.main = main

        self.ink = True

        def on_click(e):
            self.load()

        self.on_click = on_click

        self.height = 50
        self.expand = True

        self.content = ft.Row(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Text(
                        value=TEXTS.LOAD_MORE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ),
            ],
        )

    def load(self):
        self.main.load_next()


class EmojiBulkChanger(ft.Container):
    def __init__(self, main: PanelEmojis):
        super().__init__()

        self.main = main

        self.dropdown_keys = []

        # -2: none (no emoji selected)
        # -1: bar (mixed)
        # 0 - 2: same EmojiItem
        self._status_value = -2

        self.checkbox = ft.Checkbox(
            label='',
            value=False,
            tristate=True,
            on_change=self.all_deselect,
        )

        self.select_counter = ft.Text(
            value='== 0 emojis selected. ==',
            style=ft.TextStyle(italic=True),
        )

        def change_risk_level(e):
            self.main.lock()
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
            self.main.unlock()

        def change_reason(e):
            self.main.lock()
            rsid = self.reason.content.value
            if self.reason.content.value == 'none':
                rsid = None
            for i in self.main.selected:
                i.change_reason(rsid)
            self.reason.update()
            self.update_values()
            self.main.unlock()

        self._remark = ''

        def focus_remark(e):
            self._remark = self.remark.content.value

        def change_remark(e):
            self.main.lock()
            if self._remark != self.remark.content.value:
                self._remark = self.remark.content.value
                text = self.remark.content.value
                for i in self.main.selected:
                    i.change_remark(text, False)
                self.main.update()
                self.update_values()
            self.main.unlock()

        def change_status(e):
            self.main.lock()
            match self._status_value:
                case -1:
                    status = 1
                case 0:
                    status = 1
                case 1:
                    status = 0
                case 2:
                    status = 1
            self._update_status(status)
            for i in self.main.selected:
                i.change_status(status, False)
            self.main.update()
            self.update_values()
            self.main.unlock()

        self.risk_level = ft.RadioGroup(
            content=ft.Row(
                expand=True,
                controls=[
                    ft.Container(
                        ft.Radio(value='risk_0', toggleable=True, fill_color={
                            ft.ControlState.DISABLED: '#8b8b8b',
                            ft.ControlState.DEFAULT: '#5bae5b',
                        }),
                        width=40,
                    ),
                    ft.Container(
                        ft.Radio(value='risk_1', toggleable=True, fill_color={
                            ft.ControlState.DISABLED: '#c2c2c2',
                            ft.ControlState.DEFAULT: '#c1d36e',
                        }),
                        width=40,
                    ),
                    ft.Container(
                        ft.Radio(value='risk_2', toggleable=True, fill_color={
                            ft.ControlState.DISABLED: '#ababab',
                            ft.ControlState.DEFAULT: '#cdad4b',
                        }),
                        width=40,
                    ),
                    ft.Container(
                        ft.Radio(value='risk_3', fill_color={
                            ft.ControlState.DISABLED: '#6c6c6c',
                            ft.ControlState.DEFAULT: '#cc4444',
                        }),
                        width=40
                    ),
                ],
                spacing=10,
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
                text_size=14,
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
        self.status = ft.Container(
            content=ft.Icon(
                name=ft.icons.REMOVE,
                color='#00000000',
            ),
            tooltip=ft.Tooltip(
                message='<未選択>',
                wait_duration=1000,
            ),
            expand=True,
            border_radius=4,
            alignment=ft.alignment.center,
            margin=4,
            ink=True,
            on_click=change_status,
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
                    width=986,
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
                    width=240,
                    alignment=ft.alignment.center_left,
                    content=self.reason,
                ),
                ft.Container(
                    width=300,
                    alignment=ft.alignment.center_left,
                    content=self.remark,
                ),
                ft.Container(
                    width=40,
                    alignment=ft.alignment.center_left,
                    content=self.status,
                ),
                ft.Container(width=10),
            ]
        )

    def all_deselect(self, e):
        self.disabled = True

        self.main.lock()

        self.select_counter.value = '== 0 emojis selected. =='
        self.checkbox.value = False
        self.risk_level.value = None
        self.reason.content.value = None
        self.reason.content.hint_text = ''
        self.remark.content.value = None
        self.half_risk_0.color = '#005bae5b'
        self.half_risk_1.color = '#00c1d36e'
        self.half_risk_2.color = '#00cdad4b'
        self.half_risk_3.color = '#00cc4444'
        self._update_status(-2)

        self.update()

        self.main.all_deselect()

        self.main.unlock()

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
            self._update_status(-2)
        elif nsel == 1:
            e = list(self.main.selected)[0]
            common_risk_level = e.risk_level.value
            common_reason = e.reason.content.value
            common_remark = e.remark.content.value
            common_status = e.status_value
            if common_reason == '': common_reason = None
            if common_remark == '': common_remark = None

            self.risk_level.value = common_risk_level
            self.half_risk_0.color = '#005bae5b'
            self.half_risk_1.color = '#00c1d36e'
            self.half_risk_2.color = '#00cdad4b'
            self.half_risk_3.color = '#00cc4444'
            self.reason.content.value = common_reason
            if common_reason is not None:
                if common_reason in self.dropdown_keys:
                    self.reason.content.hint_text = ''
                else:
                    self.reason.content.hint_text = f'<{common_reason}>'
            else:
                self.reason.content.hint_text = ''
            self.remark.content.value = common_remark
            self._update_status(common_status)
        else:
            is_common_risk_level = True
            is_common_reason = True
            is_common_remark = True
            is_common_status = True

            contains_risk = [False, False, False, False]
            common_risk_level = list(self.main.selected)[0].risk_level.value
            common_reason = list(self.main.selected)[0].reason.content.value
            common_remark = list(self.main.selected)[0].remark.content.value
            common_status = list(self.main.selected)[0].status_value
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
                status = e.status_value
                if reason == '': reason = None
                if remark == '': remark = None

                is_common_risk_level = is_common_risk_level and common_risk_level == risk_level
                is_common_reason = is_common_reason and common_reason == reason
                is_common_remark = is_common_remark and common_remark == remark
                is_common_status = is_common_status and common_status == status

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
                    if common_reason in self.dropdown_keys:
                        self.reason.content.hint_text = ''
                    else:
                        self.reason.content.hint_text = f'<{common_reason}>'
                else:
                    self.reason.content.hint_text = ''
            else:
                self.reason.content.value = TEXTS.MISC_MIXED
                self.reason.content.hint_text = TEXTS.MISC_MIXED
            if is_common_remark:
                self.remark.content.value = common_remark
            else:
                self.remark.content.value = TEXTS.MISC_MIXED
            if is_common_status:
                self._update_status(common_status)
            else:
                self._update_status(-1)
        self.update()

    def _update_status(self, status):
        self._status_value = status
        match status:
            case -2:
                self.status.content.name = ft.icons.REMOVE
                self.status.content.color = '#00000000'
                self.status.tooltip = TEXTS.MISC_NO_SELECTED
            case -1:
                self.status.content.name = ft.icons.REMOVE
                self.status.content.color = '#606060'
                self.status.tooltip = TEXTS.MISC_MIXED
            case 0:
                self.status.content.name = ft.icons.ERROR
                self.status.content.color = '#cdad4b'
                self.status.tooltip = TEXTS.NEED_CHECK
            case 1:
                self.status.content.name = ft.icons.CHECK
                self.status.content.color = '#5bae5b'
                self.status.tooltip = TEXTS.CHECKED
            case 2:
                self.status.content.name = ft.icons.ERROR_OUTLINE
                self.status.content.color = '#c1d36e'
                self.status.tooltip = TEXTS.NEED_RECHECK

    def reload_dropdown(self):
        dropdown_keys = []
        self.reason.content.options = [ft.dropdown.Option(key='none', text=' ')]
        for rsid in registry.reasons:
            text = registry.reasons[rsid].text
            self.reason.content.options.append(ft.dropdown.Option(key=rsid, text=text))
            dropdown_keys.append(rsid)
        self.dropdown_keys = dropdown_keys
        self.reason.update()

class ActionsDialog(ft.AlertDialog):
    def __init__(self, main: PanelEmojis, filter_enabled: bool):
        super().__init__()

        self.main = main

        def open_filtering_menu(e):
            self.main.open_filtering_menu()

        def export_csv(e):
            ret = self.main.export_csv()
            if ret is not None:
                if ret > 0:
                    msg = f'{ret}個の絵文字データを出力しました\n出力先: out_emojis.csv'
                else:
                    msg = '対象の絵文字が無い為、書き出しを中断しました'
            else:
                msg = 'エラーが発生しました\nもう一度試しても直らない場合はバグの可能性があるので報告してください'
            self.page.show_dialog(
                ft.AlertDialog(
                    content=ft.Container(
                        content=ft.Text(msg),
                        margin=ft.Margin(10, 20, 10, 0),
                    ),
                    actions=[
                        ft.OutlinedButton(
                            content=ft.Text(
                                value='OK',
                                style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                            ),
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(width=2),
                                shape=ft.RoundedRectangleBorder(3)
                            ),
                            on_click=lambda e: self.page.close_dialog(),
                        ),
                    ],
                )
            )

        def export_selected_csv(e):
            ret = self.main.export_selected_csv()
            if ret is not None:
                if ret > 0:
                    msg = f'{ret}個の絵文字データを出力しました\n出力先: out_emojis.csv'
                else:
                    msg = '対象の絵文字が無い為、書き出しを中断しました'
            else:
                msg = 'エラーが発生しました\nもう一度試しても直らない場合はバグの可能性があるので報告してください'
            self.page.show_dialog(
                ft.AlertDialog(
                    content=ft.Container(
                        content=ft.Text(msg),
                        margin=ft.Margin(10, 20, 10, 0),
                    ),
                    actions=[
                        ft.OutlinedButton(
                            content=ft.Text(
                                value='OK',
                                style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                            ),
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(width=2),
                                shape=ft.RoundedRectangleBorder(3)
                            ),
                            on_click=lambda e: self.page.close_dialog(),
                        ),
                    ],
                )
            )

        self.filtering = ft.Container(
            content=ft.Icon(
                name=ft.icons.FILTER_LIST_ROUNDED,
                color='#40ff40' if filter_enabled else '#606060',
            ),
            width=50,
            height=50,
        )

        self.filtering_container = ft.Container(
            ft.Column(
                controls=[
                    self.filtering,
                    ft.Text('フィルター機能', text_align=ft.TextAlign.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            width=150,
            height=150,
            border_radius=8,
            alignment=ft.alignment.center,
            margin=4,
            ink=True,
            on_click=open_filtering_menu,
            disabled=False,
        )
        self.export_selected_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            name=ft.icons.IOS_SHARE_OUTLINED,
                            color='#c0c0c0',
                        ),
                        width=50,
                        height=50,
                    ),
                    ft.Text('選択中の項目を\nCSVファイルに出力', text_align=ft.TextAlign.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            width=150,
            height=150,
            border_radius=8,
            alignment=ft.alignment.center,
            margin=4,
            ink=True,
            on_click=export_selected_csv,
            disabled=False,
        )
        self.export_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            name=ft.icons.IOS_SHARE_OUTLINED,
                            color='#c0c0c0',
                        ),
                        width=50,
                        height=50,
                    ),
                    ft.Text('フィルターに合致する\n全ての項目を\nCSVファイルに出力', text_align=ft.TextAlign.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            width=150,
            height=150,
            border_radius=8,
            alignment=ft.alignment.center,
            margin=4,
            ink=True,
            on_click=export_csv,
            disabled=False,
        )

        self.content = ft.Container(
            content=ft.Row(
                controls=[
                    self.filtering_container,
                    self.export_selected_container,
                    self.export_container,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            margin=ft.Margin(10, 20, 10, 0)
        )

        self.actions = [
            ft.OutlinedButton(
                content=ft.Text(
                    value='閉じる',
                    style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                ),
                style=ft.ButtonStyle(
                    side=ft.BorderSide(width=2),
                    shape=ft.RoundedRectangleBorder(3)
                ),
                on_click=lambda e: self.page.close_dialog(),
            ),
        ]

class FilteringDialog(ft.AlertDialog):
    def __init__(self, main: PanelEmojis):
        super().__init__()

        self.main = main

        self.title = ft.Text(TEXTS.FILTERING.DIALOG_TITLE)
        self.title_padding = 10

        def cancel_filtering(e):
            self.page.close_dialog()

        def ok_filtering(e):
            filter: EmojiFilter = self.content.build_filter()
            self.main.update_filter(filter)
            self.page.close_dialog()

        self.content = FilteringDialogContent(self.main.filter)

        self.actions = [
            ft.OutlinedButton(
                content=ft.Text(
                    value=TEXTS.FILTERING.BUTTON_CANCEL,
                    style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                ),
                style=ft.ButtonStyle(
                    side=ft.BorderSide(width=2),
                    shape=ft.RoundedRectangleBorder(3),
                ),
                on_click=cancel_filtering,
            ),
            ft.FilledButton(
                content=ft.Text(
                    value=TEXTS.FILTERING.BUTTON_OK,
                    style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                ),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(3)
                ),
                on_click=ok_filtering,
            ),
        ]

class FilteringDialogContent(ft.Column):
    def __init__(self, filter: EmojiFilter):
        super().__init__()

        self.scroll = ft.ScrollMode.ALWAYS

        reason_genre_checkboxes = [
            ReasonGenreCheckbox(
                None,
                label=TEXTS.FILTERING.MISC_NONSET,
                value=filter.reason_genre.mapping[None] if None in filter.reason_genre.mapping else False,
            ),
        ]
        for rsid in registry.reasons:
            reason = registry.get_reason(rsid)
            reason_genre_checkboxes.append(
                ReasonGenreCheckbox(
                    rsid,
                    label=reason.text,
                    value=filter.reason_genre.mapping[rsid] if rsid in filter.reason_genre.mapping else False,
                ),
            )

        def toggle_main_switch(e):
            self.main_container.disabled = not self.main_switch.value
            self.main_container.update()

        self.main_switch = ft.Switch(
            label=TEXTS.FILTERING.MAIN,
            splash_radius=0,
            value=filter.enabled,
            on_change=toggle_main_switch,
        )

        self.name = ft.TextField(value=filter.name)
        self.category = EmptyOrTextField(filter.category, filter.empty_category)
        self.tags = EmptyOrTextField(filter.tags, filter.empty_tags)
        self.is_self_made = ft.Column(
            controls=[
                ft.Checkbox(label=TEXTS.FILTERING.SELFMADE_YES, value=filter.is_self_made.yes),
                ft.Checkbox(label=TEXTS.FILTERING.SELFMADE_NO, value=filter.is_self_made.no),
            ],
            spacing=0,
        )
        self.licence = EmptyOrTextField(filter.licence, filter.empty_licence)
        self.username = EmptyOrTextField(filter.username, filter.empty_username)
        self.risk_level = ft.Column(
            controls=[
                ft.Checkbox(label=TEXTS.FILTERING.MISC_NONSET, value=filter.risk_level.notset),
                ft.Checkbox(label=TEXTS.FILTERING.RISK_LEVEL_LOW, value=filter.risk_level.low),
                ft.Checkbox(label=TEXTS.FILTERING.RISK_LEVEL_MEDIUM, value=filter.risk_level.medium),
                ft.Checkbox(label=TEXTS.FILTERING.RISK_LEVEL_HIGH, value=filter.risk_level.high),
                ft.Checkbox(label=TEXTS.FILTERING.RISK_LEVEL_DANGER, value=filter.risk_level.danger),
            ],
            spacing=0,
        )
        self.reason_genre = ft.Column(
            controls=reason_genre_checkboxes,
            spacing=0,
        )
        self.remark = EmptyOrTextField(filter.remark, filter.empty_remark)
        self.status = ft.Column(
            controls=[
                ft.Checkbox(label=TEXTS.FILTERING.NEED_CHECK, value=filter.status.need_check),
                ft.Checkbox(label=TEXTS.FILTERING.NEED_RECHECK, value=filter.status.need_recheck),
                ft.Checkbox(label=TEXTS.FILTERING.CHECKED, value=filter.status.checked),
            ],
            spacing=0,
        )

        self.name_container = ControlWithSwitch(
            content=self.name,
            label=TEXTS.FILTERING.NAME,
            enable=filter.enabled_name,
        )
        self.category_container = ControlWithSwitch(
            content=self.category,
            label=TEXTS.FILTERING.CATEGORY,
            enable=filter.enabled_category,
        )
        self.tags_container = ControlWithSwitch(
            content=self.tags,
            label=TEXTS.FILTERING.TAG,
            enable=filter.enabled_tags,
        )
        self.is_self_made_container = ControlWithSwitch(
            content=self.is_self_made,
            label=TEXTS.FILTERING.SELFMADE,
            enable=filter.enabled_is_self_made,
        )
        self.licence_container = ControlWithSwitch(
            content=self.licence,
            label=TEXTS.FILTERING.LICENSE,
            enable=filter.enabled_licence,
        )
        self.username_container = ControlWithSwitch(
            content=self.username,
            label=TEXTS.FILTERING.OWNER,
            enable=filter.enabled_username,
        )
        self.risk_level_container = ControlWithSwitch(
            content=self.risk_level,
            label=TEXTS.FILTERING.RISK_LEVEL,
            enable=filter.enabled_risk_level,
        )
        self.reason_genre_container = ControlWithSwitch(
            content=self.reason_genre,
            label=TEXTS.FILTERING.REASON_GENRE,
            enable=filter.enabled_reason_genre,
        )
        self.remark_container = ControlWithSwitch(
            content=self.remark,
            label=TEXTS.FILTERING.REMARK,
            enable=filter.enabled_remark,
        )
        self.status_container = ControlWithSwitch(
            content=self.status,
            label=TEXTS.FILTERING.CHECK_STATUS,
            enable=filter.enabled_status,
        )

        self.main_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                self.name_container,
                                self.category_container,
                                self.tags_container,
                                self.is_self_made_container,
                                self.licence_container,
                                self.username_container,
                                self.risk_level_container,
                                self.reason_genre_container,
                                self.remark_container,
                                self.status_container,
                            ],
                        ),
                    ),
                ],
                scroll=ft.ScrollMode.HIDDEN,
            ),
            width=600,
            padding=10,
            border_radius=3,
            disabled=not filter.enabled,
        )

        self.controls = [
            self.main_switch,
            self.main_container,
        ]

    def build_filter(self) -> EmojiFilter:

        self_made_no = self.is_self_made.controls[1].value
        self_made_yes = self.is_self_made.controls[0].value

        risk_level_notset = self.risk_level.controls[0].value
        risk_level_low = self.risk_level.controls[1].value
        risk_level_medium = self.risk_level.controls[2].value
        risk_level_high = self.risk_level.controls[3].value
        risk_level_danger = self.risk_level.controls[4].value

        status_need_check = self.status.controls[0].value
        status_checked = self.status.controls[2].value
        status_need_recheck = self.status.controls[1].value

        reason_genre_items = {}
        for cb in self.reason_genre.controls:
            reason_genre_items[cb.rsid] = cb.value

        enabled = self.main_switch.value

        enabled_name = self.name_container.get_enabled()
        enabled_category = self.category_container.get_enabled()
        enabled_tags = self.tags_container.get_enabled()
        enabled_is_self_made = self.is_self_made_container.get_enabled()
        enabled_licence = self.licence_container.get_enabled()
        enabled_username = self.username_container.get_enabled()
        enabled_risk_level = self.risk_level_container.get_enabled()
        enabled_reason_genre = self.reason_genre_container.get_enabled()
        enabled_remark = self.remark_container.get_enabled()
        enabled_status = self.status_container.get_enabled()

        name = self.name.value
        category = self.category.get_text()
        tags = self.tags.get_text()
        is_self_made = SelectionIsSelfMade(self_made_no, self_made_yes)
        licence = self.licence.get_text()
        username = self.username.get_text()
        risk_level = SelectionRiskLevel(risk_level_notset, risk_level_low, risk_level_medium, risk_level_high, risk_level_danger)
        reason_genre = SelectionReasonGenre(reason_genre_items)
        remark = self.remark.get_text()
        status = SelectionCheckStatus(status_need_check, status_checked, status_need_recheck)

        empty_category = self.category.get_empty()
        empty_tags = self.tags.get_empty()
        empty_licence = self.licence.get_empty()
        empty_username = self.username.get_empty()
        empty_remark = self.remark.get_empty()

        return EmojiFilter(enabled, enabled_name, enabled_category, enabled_tags, enabled_is_self_made, enabled_licence, enabled_username, enabled_risk_level, enabled_reason_genre, enabled_remark, enabled_status, name, category, tags, is_self_made, licence, username, risk_level, reason_genre, remark, status, empty_category, empty_tags, empty_licence, empty_username, empty_remark)

class ControlWithSwitch(ft.Container):
    def __init__(self, content: ft.Control, label: str, enable: bool = True):
        super().__init__()

        def toggle(e):
            self.main_content.disabled = not self.switch.value
            self.main_content.update()

        self.main_content = content
        self.switch = ft.Switch(
            label=label,
            splash_radius=0,
            value=enable,
            on_change=toggle,
        )
        self.main_content.disabled = not enable

        self.content = ft.Column(
            controls=[
                self.switch,
                self.main_content,
            ],
        )

    def get_enabled(self) -> bool:
        return self.switch.value

class EmptyOrTextField(ft.Row):
    def __init__(self, text: str, empty: bool):
        super().__init__()

        def toggle_empty(e):
            self.set_empty(self.cb.value)

        self.tf = ft.TextField(
            value=text,
            disabled=empty,
        )
        self.cb = ft.Checkbox(
            label='空の項目のみを検索',
            value=empty,
            on_change=toggle_empty,
        )

        self.controls = [
            self.tf,
            self.cb,
        ]

    def get_text(self):
        return self.tf.value

    def get_empty(self):
        return self.cb.value

    def set_text(self, text: str):
        self.tf.value = text
        self.tf.update()

    def set_empty(self, empty: bool):
        self.tf.disabled = empty
        self.cb.value = empty
        self.update()

class ReasonGenreCheckbox(ft.Checkbox):
    def __init__(self, rsid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rsid = rsid

