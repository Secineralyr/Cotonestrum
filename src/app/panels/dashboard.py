import flet as ft
from flet.plotly_chart import PlotlyChart

# ほしいのは以下の通り
# ようこそメッセージ
# 現在の登録絵文字数、精査完了数、危険度別数
# 各危険度の円グラフ
# ユーザー別登録数の円グラフ


class PanelDashboard(ft.Container):
    """パディング用ダッシュボードフレーム"""

    def __init__(self):
        super().__init__(
            padding=ft.padding.all(20),
            content=DashboardMainFrame(),
            expand=True,
        )


class DashboardMainFrame(ft.Column):
    """ダッシュボードのメインパネル"""

    def __init__(self):
        super().__init__(
            spacing=10
        )

        self.controls = [
            WelcomeText(),
            ft.Divider(color='#ffffff'),
            ft.ResponsiveRow(
                controls=[
                    EmojiStatus(),
                    StatusFrame(WelcomeText()),
                    StatusFrame(WelcomeText()),
                    StatusFrame(WelcomeText()),
                ],
            ),
        ]


class WelcomeText(ft.Text):
    """上部に表示されるメッセージ"""

    def __init__(self):
        super().__init__(
            theme_style=ft.TextThemeStyle.TITLE_LARGE,
            weight=ft.FontWeight.BOLD
        )

        self.value = 'ようこそあああああああああああああああああああああああああああ！！！！！！'


class StatusFrame(ft.Container):
    """ステータスのフレーム"""

    def __init__(self, content: ft.Control):
        super().__init__(
            content,
            bgcolor=ft.colors.ON_SECONDARY,
            expand=True,
            padding=20,
            alignment=ft.alignment.center,
            border_radius=10,
            col={ 'lg': 6 }
        )


class CounterInfoCard(ft.Container):
    """状態などを表すカード
    NOTE: CardよりContainerのほうがいいのでそうしている"""


    _count_value = 0


    def __init__(self, icon: str, icon_container_color: str, label: str):
        super().__init__(
            bgcolor=ft.colors.SECONDARY_CONTAINER,
            expand=True,
            padding=10,
            alignment=ft.alignment.center_left,
            border_radius=5,
        )

        self._icon = icon
        self._icon_component = ft.Icon(
            name=self._icon,
            color='#ffffff',
            size=20,
        )

        self._icon_container_color = icon_container_color
        self._icon_container = ft.Container(
            content=self._icon_component,
            bgcolor=self._icon_container_color,
            padding=15,
            alignment=ft.alignment.center,
            border_radius=10,
        )

        self._label = label
        self._label_text = ft.Text(
            size=18,
            weight=ft.FontWeight.BOLD,
            value=self._label,
        )

        self._counter_component = ft.Text(
            size=16,
            value='1,000',
            text_align=ft.TextAlign.RIGHT,
        )

        self._info_column = ft.Column(
            expand=True,
            controls=[
                self._label_text,
                self._counter_component,
            ],
            spacing=0
        )

        self._card_row = ft.Row(
            expand=True,
            controls=[
                self._icon_container,
                self._info_column,
            ],
        )

        self.content = self._card_row


class EmojiStatus(StatusFrame):

    def __init__(self):
        super().__init__(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            CounterInfoCard(ft.icons.ADD_REACTION, '#8000B06B', '絵文字の数'),
                            CounterInfoCard(ft.icons.WARNING, '#80F6AA00', '危険数'),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            CounterInfoCard(ft.icons.ADD_REACTION, '#00B06B', '絵文字の数'),
                            CounterInfoCard(ft.icons.WARNING, '#F6AA00', '危険数'),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            CounterInfoCard(ft.icons.ADD_REACTION, '#00B06B', '絵文字の数'),
                            CounterInfoCard(ft.icons.WARNING, '#F6AA00', '危険数'),
                        ]
                    )
                ]
            )
        )


class PieChartComponent(PlotlyChart):

    def __init__(self):

        super().__init__()

