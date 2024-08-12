import flet as ft

from app.sidebar import Sidebar, SidebarArea
from app.panels.emojis import PanelEmojis
from app.panels.users import PanelUsers
from app.panels.settings import PanelSettings

from app.views import Views


class Root(ft.Container):

    __currentView = None

    @property
    def currentView(self) -> Views:
        return self.__currentView
    
    def navigate(self, value: Views):
        self.__currentView = value
        match value:
            case Views.EMOJIS:
                self.main_panel.content = self.panel_emojis
            case Views.USERS:
                self.main_panel.content = self.panel_users
            case Views.SETTINGS:
                self.main_panel.content = self.panel_settings

    def __init__(self):
        super().__init__()

        self.expand = True

        self.sidebar_area = SidebarArea()
        self.sidebar = Sidebar(self.sidebar_area)

        self.panel_emojis = PanelEmojis()
        self.panel_users = PanelUsers()
        self.panel_settings = PanelSettings()

        self.main_panel = ft.Container(content=ft.Text('Main Panel'), expand=True)

        self.content = ft.Stack(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=self.sidebar_area,
                            margin=10,
                        ),
                        ft.VerticalDivider(width=1),
                        self.main_panel,
                    ],
                    spacing=0,
                ),
                ft.Container(
                    content=self.sidebar,
                    margin=10,
                ),
            ],
            expand=True
        )

