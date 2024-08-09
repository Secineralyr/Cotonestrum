import flet as ft

from app.sidebar import Sidebar, SidebarArea
from core.views import Views


class Root(ft.Container):

    __currentView = Views.EMOJIS

    @property
    def currentView(self) -> Views:
        return self.__currentView
    
    @currentView.setter
    def currentView(self, value: Views):
        self.__currentView = value

    def __init__(self):
        super().__init__()

        self.expand = True

        self.sidebar_area = SidebarArea()
        self.sidebar = Sidebar(self.sidebar_area)

        self.main_panel = ft.Container(content=ft.Text('Main Panel'), expand=True)

        self.content = ft.Stack(
            controls=[
                ft.Row(
                    [
                        self.sidebar_area,
                        ft.VerticalDivider(width=1),
                        self.main_panel,
                    ],
                ),
                self.sidebar,
            ],
            expand=True
        )
    
