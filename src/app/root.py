import flet as ft

from app.sidebar import Sidebar, SidebarArea
from app.panels.emojis import PanelEmojis
from app.panels.users import PanelUsers
from app.panels.settings import PanelSettings
from app.panels.logs import PanelLogs

from app.views import Views


class Root(ft.Container):

    __current_view = None

    @property
    def current_view(self) -> Views:
        return self.__current_view
    
    def navigate(self, value: Views):
        self.__current_view = value
        match value:
            case Views.EMOJIS:
                self.main_panel.content = self.panel_emojis
            case Views.USERS:
                self.main_panel.content = self.panel_users
            case Views.SETTINGS:
                self.main_panel.content = self.panel_settings
            case Views.LOGS:
                self.main_panel.content = self.panel_logs
                self.sidebar.button_logs.reset_badge_value()

    def __init__(self):
        super().__init__()

        self.expand = True

        self.sidebar_area = SidebarArea()
        self.sidebar = Sidebar(self.sidebar_area)

        self.panel_emojis = PanelEmojis()
        self.panel_users = PanelUsers()
        self.panel_settings = PanelSettings()
        self.panel_logs = PanelLogs()

        self.page.data['sidebar'] = self.sidebar

        self.page.data['emojis'] = self.panel_emojis
        self.page.data['users'] = self.panel_users
        self.page.data['settings'] = self.panel_settings
        self.page.data['logs'] = self.panel_logs

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
                        ft.Container(
                            content=self.main_panel,
                        ),
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

