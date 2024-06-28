from typing import Optional

import flet as ft

from data.views import Views, SidebarButtonInfo



class Constants(object):
    __WIDTH_COLLAPSED: int = 60
    __WIDTH_EXTENDED: int  = 200

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


    def toggleExtended(self, extend: bool):
        if extend:
            self.width = CONST_SIDEBAR.WIDTH_EXTENDED
        else:
            self.width = CONST_SIDEBAR.WIDTH_COLLAPSED
        self.update()

class Sidebar(ft.Column):

    def __init__(self, sidebar_area: SidebarArea):
        super().__init__()

        self.extended = False
        self.sidebar_area = sidebar_area
        ft.FloatingActionButton
        self.toggle_button = SidebarToggleButton(self)
        self.buttons: list[SidebarButton] = [
            SidebarButton.createSidebarButton(Views.EMOJIS, self, selected=True),
            SidebarButton.createSidebarButton(Views.USERS, self),
            SidebarButton.createSidebarButton(Views.SETTINGS, self),
        ]

        self.width = CONST_SIDEBAR.WIDTH_EXTENDED

        self.controls = [self.toggle_button]
        self.controls.extend(self.buttons)

    def toggleExtended(self, e):
        self.extended = not self.extended
        extend = self.extended

        if extend:
            self.toggle_button.icon = ft.icons.CLOSE_ROUNDED
        else:
            self.toggle_button.icon = ft.icons.MENU_ROUNDED
        
        for button in self.buttons:
            button.toggleExtended(extend)
        
        self.sidebar_area.toggleExtended(extend)
        self.update()
    



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

        self.target = target
        self.sidebar = sidebar
        self._selected = selected

        self.selected_icon = selected_icon
        self.unselected_icon = unselected_icon

        self._icon = self.selected_icon if self._selected else self.unselected_icon
        self._text = text

        self.height = CONST_SIDEBAR.BUTTON_HEIGHT
        self.width = CONST_SIDEBAR.WIDTH_COLLAPSED
        self.border_radius = 10
        self.alignment = ft.alignment.center_left
        self.clip_behavior = ft.ClipBehavior.ANTI_ALIAS

        self.ink = True

        self.on_click = self.changeView

        self.icon_content = ft.Icon(self.icon)
        self.text_content = ft.Text(self.text, size=18)
        self.text_container = ft.Container(
            width=0,
            alignment=ft.alignment.center_right,
            padding=ft.padding.only(right=30),
            content=self.text_content,
            animate_size=ft.Animation(300, ft.AnimationCurve.EASE_OUT_CUBIC),
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
    def createSidebarButton(cls, view: Views, sidebar: Sidebar, selected: bool = False):
        info = SidebarButtonInfo.getInfo(view)
        return cls(view, sidebar, *info, selected)
    
    @property
    def icon(self) -> Optional[str]:
        return self._icon
    
    @icon.setter
    def icon(self, value: Optional[str]):
        if self._icon != value:
            self._icon = value
            self.icon_content.name = value
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

    def toggleExtended(self, extend: bool):
        if extend:
            self.width = CONST_SIDEBAR.WIDTH_EXTENDED
            self.text_container.width = CONST_SIDEBAR.WIDTH_EXTENDED - CONST_SIDEBAR.WIDTH_COLLAPSED
        else:
            self.width = CONST_SIDEBAR.WIDTH_COLLAPSED
            self.text_container.width = 0
        self.update()

    def changeView(self, e):
        self.page.data['rootInstance'].currentView = self.target
        for button in self.sidebar.buttons:
            button.selected = button.target == self.target
        self.page.update()


class SidebarToggleButton(ft.FloatingActionButton):
    def __init__(self, sidebar: Sidebar, **kwargs):
        super().__init__(**kwargs)

        self.sidebar = sidebar

        self.height = CONST_SIDEBAR.TOGGLE_BUTTON_HEIGHT
        self.width = CONST_SIDEBAR.WIDTH_COLLAPSED
        self.icon = ft.icons.MENU_ROUNDED

        self.on_click = self.sidebar.toggleExtended










