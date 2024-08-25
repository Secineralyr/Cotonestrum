from typing import Optional

import flet as ft

from app.views import Views, SidebarButtonInfo



class Constants(object):
    __WIDTH_COLLAPSED: int = 60
    __WIDTH_EXTENDED: int  = 220

    __TOGGLE_BUTTON_HEIGHT = 60
    __BUTTON_HEIGHT = 50

    @property
    def WIDTH_COLLAPSED(self) -> int:
        return self.__WIDTH_COLLAPSED

    @property
    def WIDTH_EXTENDED(self) -> int:
        return self.__WIDTH_EXTENDED
    
    @property
    def TOGGLE_BUTTON_HEIGHT(self) -> int:
        return self.__TOGGLE_BUTTON_HEIGHT

    @property
    def BUTTON_HEIGHT(self) -> int:
        return self.__BUTTON_HEIGHT

CONST_SIDEBAR = Constants()


class SidebarArea(ft.Column):

    def __init__(self):
        super().__init__()

        self.width = CONST_SIDEBAR.WIDTH_COLLAPSED
        self.animate_size = ft.Animation(300, ft.AnimationCurve.EASE_OUT_CUBIC)

        self.controls = []


    def toggle_extended(self, extend: bool):
        if extend:
            self.width = CONST_SIDEBAR.WIDTH_EXTENDED
        else:
            self.width = CONST_SIDEBAR.WIDTH_COLLAPSED
        self.update()

class Sidebar(ft.Container):

    def __init__(self, sidebar_area: SidebarArea):
        super().__init__()

        self.extended = False
        self.sidebar_area = sidebar_area

        self.toggle_button = SidebarToggleButton(self)
        self.buttons: list[SidebarButton] = [
            SidebarButton.create_sidebar_button(Views.DASHBOARD, self, True),
            SidebarButton.create_sidebar_button(Views.EMOJIS, self),
            SidebarButton.create_sidebar_button(Views.USERS, self),
            SidebarButton.create_sidebar_button(Views.REASONS, self),
        ]
        self.button_logs = SidebarButtonWithBadge.create_sidebar_button(Views.LOGS, self)
        self.buttons_bottom: list[SidebarButton] = [
            self.button_logs,
            SidebarButton.create_sidebar_button(Views.SETTINGS, self),
        ]

        self.content = ft.Column(
            controls = [
                ft.Container(
                    content=ft.Column(
                        controls=[self.toggle_button, *self.buttons],
                    ),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=self.buttons_bottom,
                    ),
                ),
            ],
            width=CONST_SIDEBAR.WIDTH_COLLAPSED,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def toggle_extended(self, e):
        self.extended = not self.extended
        extend = self.extended

        if extend:
            self.content.width = CONST_SIDEBAR.WIDTH_EXTENDED
            self.toggle_button.icon = ft.icons.CLOSE_ROUNDED
        else:
            self.content.width = CONST_SIDEBAR.WIDTH_COLLAPSED
            self.toggle_button.icon = ft.icons.MENU_ROUNDED
        
        for button in [*self.buttons, *self.buttons_bottom]:
            button.toggle_extended(extend)
        
        self.sidebar_area.toggle_extended(extend)
        self.update()
    
    def lock_buttons(self):
        for button in [*self.buttons, *self.buttons_bottom]:
            button.locked = True
            button.update()

    def unlock_buttons(self):
        for button in [*self.buttons, *self.buttons_bottom]:
            button.locked = False
            button.update()


class SidebarButton(ft.Container):

    def __init__(
        self,
        target: Views,
        sidebar: Sidebar,
        unselected_icon: Optional[str] = None,
        selected_icon: Optional[str] = None,
        text: str = '',
        selected: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)

        self._locked = False

        self.target = target
        self.sidebar = sidebar
        self._selected = selected

        self.selected_icon = selected_icon
        self.unselected_icon = unselected_icon

        self._icon = self.selected_icon if self._selected else self.unselected_icon
        self._text = text

        def change_view(e):
            if not self.locked:
                self.page.data['root'].navigate(self.target)
                for button in [*self.sidebar.buttons, *self.sidebar.buttons_bottom]:
                    button.selected = button.target == self.target
                    button.update()

        self.height = CONST_SIDEBAR.BUTTON_HEIGHT
        self.width = CONST_SIDEBAR.WIDTH_COLLAPSED
        self.border_radius = 10
        self.alignment = ft.alignment.center_left
        self.clip_behavior = ft.ClipBehavior.ANTI_ALIAS

        self.ink = True

        self.on_click = change_view

        self.icon_content = ft.Container(ft.Icon(self.icon))
        self.text_content = ft.Text(self.text, size=18)
        self.text_container = ft.Container(
            width=0,
            alignment=ft.alignment.center_right,
            padding=ft.padding.only(right=30),
            content=self.text_content,
            animate_size=ft.Animation(300, ft.AnimationCurve.EASE_OUT_CUBIC),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )

        self.content = ft.Row(
            height=CONST_SIDEBAR.BUTTON_HEIGHT,
            controls=[
                ft.Container(
                    width=CONST_SIDEBAR.WIDTH_COLLAPSED,
                    alignment=ft.alignment.center,
                    content=self.icon_content,
                ),
                self.text_container,
            ],
        )
    
    @classmethod
    def create_sidebar_button(cls, view: Views, sidebar: Sidebar, selected: bool = False):
        info = SidebarButtonInfo.get_info(view)
        return cls(view, sidebar, *info, selected)
    
    @property
    def locked(self) -> bool:
        return self._locked
    
    @locked.setter
    def locked(self, value: bool):
        if self._locked != value:
            self._locked = value
            if value:
                self.icon_content.content.color = '#808080'
            else:
                self.icon_content.content.color = '#a0cafd'
            self.icon_content.update()

    @property
    def icon(self) -> Optional[str]:
        return self._icon
    
    @icon.setter
    def icon(self, value: Optional[str]):
        if self._icon != value:
            self._icon = value
            self.icon_content.content.name = value
            self.icon_content.update()

    @property
    def text(self) -> Optional[str]:
        return self._text
    
    @text.setter
    def text(self, value: Optional[str]):
        if self._text != value:
            self._text = value
            self.text_content.value = value
            self.text_content.update()
    
    @property
    def selected(self) -> bool:
        return self._selected
    
    @selected.setter
    def selected(self, value: bool):
        if self._selected != value:
            self._selected = value
            self.icon = self.selected_icon if self._selected else self.unselected_icon

    def toggle_extended(self, extend: bool):
        if extend:
            self.width = CONST_SIDEBAR.WIDTH_EXTENDED
            self.text_container.width = CONST_SIDEBAR.WIDTH_EXTENDED - CONST_SIDEBAR.WIDTH_COLLAPSED
        else:
            self.width = CONST_SIDEBAR.WIDTH_COLLAPSED
            self.text_container.width = 0
        self.update()


class SidebarButtonWithBadge(SidebarButton):

    def __init__(
        self,
        target: Views,
        sidebar: Sidebar,
        unselected_icon: Optional[str] = None,
        selected_icon: Optional[str] = None,
        text: str = '',
        selected: bool = False,
        **kwargs
    ):
        super().__init__(target, sidebar, unselected_icon, selected_icon, text, selected, **kwargs)

        self.badge_value = 0

        self.icon_content.content = ft.Badge(
            content=ft.Icon(self.icon),
            offset=ft.Offset(0, 10),
            label_visible=False,
        )

    @property
    def locked(self) -> bool:
        return self._locked
    
    @locked.setter
    def locked(self, value: bool):
        if self._locked != value:
            self._locked = value
            if value:
                self.icon_content.content.content.color = '#808080'
            else:
                self.icon_content.content.content.color = '#a0cafd'
            self.icon_content.update()

    @property
    def icon(self) -> Optional[str]:
        return self._icon
    
    @icon.setter
    def icon(self, value: Optional[str]):
        if self._icon != value:
            self._icon = value
            self.icon_content.content.content.name = value
            self.icon_content.update()
    
    def _show_badge_value(self):
        value = self.badge_value
        self.icon_content.content.label_visible = value > 0
        if value <= 0:
            text = '0'
        elif value <= 99:
            text = str(value)
        else:
            text = '99+'
        self.icon_content.content.text = text
        self.icon_content.update()

    def set_badge_value(self, value: int):
        self.badge_value = value if value >= 0 else 0
        self._show_badge_value()
    
    def get_badge_value(self):
        return self.badge_value
    
    def reset_badge_value(self):
        if self.badge_value != 0:
            self.badge_value = 0
            self._show_badge_value()

    def increment_badge_value(self):
        self.badge_value += 1
        if self.badge_value <= 100:
            self._show_badge_value()


class SidebarToggleButton(ft.FloatingActionButton):
    def __init__(self, sidebar: Sidebar, **kwargs):
        super().__init__(**kwargs)

        self.sidebar = sidebar

        self.height = CONST_SIDEBAR.TOGGLE_BUTTON_HEIGHT
        self.width = CONST_SIDEBAR.WIDTH_COLLAPSED
        self.icon = ft.icons.MENU_ROUNDED

        self.on_click = self.sidebar.toggle_extended
