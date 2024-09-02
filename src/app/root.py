from typing import Optional
import flet as ft

from app.panels.dashboard import PanelDashboard
from app.sidebar import Sidebar, SidebarArea
from app.panels.emojis import PanelEmojis
from app.panels.users import PanelUsers
from app.panels.reasons import PanelReasons
from app.panels.settings import PanelSettings
from app.panels.logs import PanelLogs

from app.utils.control import IOSAlignment
from app.views import Views
from app.misc.loadingring import LoadingRing


class Root(ft.Container):

    __current_view = None

    def get_panel(self, value: Views) -> Optional[Views]:
        match value:
            case Views.EMOJIS:
                return self.panel_emojis
            case Views.USERS:
                return self.panel_users
            case Views.REASONS:
                return self.panel_reasons
            case Views.SETTINGS:
                return self.panel_settings
            case Views.LOGS:
                return self.panel_logs
            case Views.DASHBOARD:
                return self.panel_dashboard
        return None

    @property
    def current_view(self) -> Views:
        return self.__current_view

    def navigate(self, value: Views):
        bvalue = self.__current_view
        self.__current_view = value
        if bvalue != value:
            target = self.get_panel(value)
            before = self.get_panel(bvalue)

            if value == Views.DASHBOARD:
                self.panel_dashboard.reload_all()
            if value == Views.EMOJIS:
                self.panel_emojis.load_next()
            if value == Views.LOGS:
                self.sidebar.button_logs.reset_badge_value()
                self.panel_logs.log_view.scroll_to(offset=-1, duration=0)

            if bvalue == Views.EMOJIS:
                self.panel_emojis.unload_all()

            if before is not None:
                before.visible = False
                before.update()
            if target is not None:
                target.visible = True
                target.update()

    def __init__(self):
        super().__init__()

        self.expand = True

        self.sidebar_area = SidebarArea()
        self.sidebar = Sidebar(self.sidebar_area)

        self.panel_dashboard = PanelDashboard()
        self.panel_emojis = PanelEmojis()
        self.panel_users = PanelUsers()
        self.panel_reasons = PanelReasons()
        self.panel_settings = PanelSettings()
        self.panel_logs = PanelLogs()

        self.panels: list[ft.Control] = [
            self.panel_dashboard,
            self.panel_emojis,
            self.panel_users,
            self.panel_reasons,
            self.panel_settings,
            self.panel_logs,
        ]

        for p in self.panels:
            p.visible = False

        self.loading = LoadingRing()

        self.content = ft.Stack(
            controls=[
                ft.Stack(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=self.sidebar_area,
                                    margin=10,
                                ),
                                ft.VerticalDivider(width=1),
                                ft.Container(
                                    content=ft.Stack(
                                        controls=self.panels,
                                    ),
                                    expand=True,
                                ),
                            ],
                            spacing=0,
                        ),
                        ft.Container(
                            content=self.sidebar,
                            margin=10,
                        ),
                    ],
                    expand=True,
                ),
                IOSAlignment(
                    content=self.loading,
                    horizontal=ft.MainAxisAlignment.END,
                    vertical=ft.MainAxisAlignment.END,
                ),
            ],
            alignment=ft.alignment.bottom_right,
        )

        # 最後にダッシュボードに移動する
        # このときnavigateは使えないのでそういうふうにする
        self.__current_view = Views.DASHBOARD
        self.panel_dashboard.visible = True


    def did_mount(self):
        self.page.data['sidebar'] = self.sidebar

        self.page.data['dashboard'] = self.panel_dashboard
        self.page.data['emojis'] = self.panel_emojis
        self.page.data['users'] = self.panel_users
        self.page.data['reasons'] = self.panel_reasons
        self.page.data['settings'] = self.panel_settings
        self.page.data['logs'] = self.panel_logs

        self.page.data['loading'] = self.loading

        self.panel_dashboard.reload_all()
