from typing import Union

import flet as ft

# ほしいのは以下の通り
# ようこそメッセージ
# 現在の登録絵文字数、精査完了数、危険度別数
# 各危険度の円グラフ
# ユーザー別登録数の円グラフ
# 理由区分別絵文字数の取得


class PanelDashboard(ft.Container):
    """パディング用ダッシュボードフレーム"""

    def __init__(self):
        super().__init__(
            padding=ft.padding.all(20),
            expand=True,
        )
        self._main_frame = DashboardMainFrame()
        self.content = self._main_frame

    @property
    def main_frame(self):
        """ダッシュボードのメインフレーム"""
        return self._main_frame


class DashboardMainFrame(ft.Column):
    """ダッシュボードのメインパネル"""

    def __init__(self):
        super().__init__(
            spacing=10,
            expand=True,
        )

        # テスト用 実装されたら消す
        labels = ['いらない', '気になる', 'どうでもいい', 'めっちゃほしい']
        values: list[Union[int, float]] = [370, 300, 150, 50]
        values.reverse()
        colors = ['#00B06B', '#1971FF', '#F6AA00', '#FF4B00']

        self._welcome_text = WelcomeText()
        self._emoji_status = EmojiStatus()
        self._risk_pie_chart = PieChartComponent('危険度別絵文字数グラフ', labels, values, colors, False, False)
        self._user_pie_chart = PieChartComponent('ユーザー別絵文字数グラフ', [*labels, 'ああああ'], [*values, 3], colors)
        self._reason_pie_chart = PieChartComponent('理由区分別絵文字数グラフ', labels, values, [*colors, '#f0f0f0'])

        self.controls = [
            self._welcome_text,
            ft.Divider(color='#ffffff'),
            ft.Row(
                controls=[
                    self._emoji_status,
                    StatusFrame(self._risk_pie_chart),
                ],
                expand=1,
            ),
            ft.Row(
                controls=[
                    StatusFrame(self._user_pie_chart),
                    StatusFrame(self._reason_pie_chart),
                ],
                expand=1,
            ),
        ]

    @property
    def welcome_text(self):
        """メッセージテキストコンポーネント"""
        return self._welcome_text

    @property
    def emoji_status(self):
        """絵文字の数値系情報群"""
        return self._emoji_status

    @property
    def risk_pie_chart(self):
        """危険度チャート"""
        return self._risk_pie_chart

    @property
    def user_pie_chart(self):
        """ユーザー絵文字数チャート"""
        return self._user_pie_chart

    @property
    def reason_pie_chart(self):
        """理由区分チャート"""
        return self._reason_pie_chart


class WelcomeText(ft.Text):
    """上部に表示されるメッセージ"""

    def __init__(self):
        super().__init__(
            theme_style=ft.TextThemeStyle.TITLE_LARGE,
            weight=ft.FontWeight.BOLD
        )

        # お疲れ様です、～さん。
        # 下記はログインしていない状態
        self.value = 'ようこそCotonestrumへ！'

    def update_to_authed_text(self, username: str = 'てすと'): # デフォルトは後で消す
        """認証されている際にテキストを変更します"""
        self.value = f'おつかれさまです、{username}さん。'
        self.update()


class StatusFrame(ft.Container):
    """ステータスのフレーム"""

    def __init__(self, content: Union[ft.Control, None] = None):
        super().__init__(
            content,
            bgcolor=ft.colors.ON_SECONDARY,
            expand=1,
            padding=20,
            alignment=ft.alignment.center,
            border_radius=10,
            col={ 'lg': 6 }
        )


class CounterInfoCard(ft.Container):
    """状態などを表すカード
    NOTE: CardよりContainerのほうがいいのでそうしている"""

    _count_value = 0

    def __init__(self, icon: str, icon_container_color: str, label: str, value: int):
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
            value='{:,}'.format(value),
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

    def _format_value(self, value: int):
        return '{:,}'.format(value)

    def change_count(self, count: int):
        self._counter_component.value = self._format_value(count)
        self._counter_component.update()

class EmojiStatus(StatusFrame):
    """絵文字ステータスメインコンテナ"""

    def __init__(self):
        super().__init__()
        self.alignment = ft.alignment.top_left

        self._emoji_count = CounterInfoCard(ft.icons.ADD_REACTION, '#00B06B', '絵文字総数', 16777216)
        self._check_count = CounterInfoCard(ft.icons.CHECKLIST_ROUNDED, '#1971FF', '精査数', 16777216)
        self._low_risk_count = CounterInfoCard(ft.icons.HEALTH_AND_SAFETY_ROUNDED, '#00B06B', '危険度: 低', 16777216)
        self._medium_risk_count = CounterInfoCard(ft.icons.WARNING_ROUNDED, '#F6AA00', '危険度: 中', 16777216)
        self._high_risk_count = CounterInfoCard(ft.icons.DO_NOT_DISTURB_ROUNDED, '#FF4B00', '危険度: 高', 16777216)
        self._danger_risk_count = CounterInfoCard(ft.icons.DANGEROUS_ROUNDED, '#990099', '危険度: 重大', 16777216)
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self._emoji_count,
                        self._check_count,
                    ],
                ),
                ft.Divider(
                    color='#ffffff',
                ),
                ft.Row(
                    controls=[
                        self._low_risk_count,
                        self._medium_risk_count,
                    ],
                ),
                ft.Row(
                    controls=[
                        self._high_risk_count,
                        self._danger_risk_count,
                    ],
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    @property
    def emoji_count(self):
        """絵文字数"""
        return self._emoji_count

    @property
    def check_count(self):
        """精査数"""
        return self._check_count

    @property
    def low_risk_count(self):
        """低危険度"""
        return self._low_risk_count

    @property
    def medium_risk_count(self):
        """中危険度"""
        return self._medium_risk_count

    @property
    def high_risk_count(self):
        """高危険度"""
        return self._high_risk_count

    @property
    def danger_risk_count(self):
        """重大危険度"""
        return self._danger_risk_count


class PieChart(ft.PieChart):
    """円グラフ本体"""

    _SECTION_RADIUS = 100

    _before_hover_section_index = -1

    def __init__(self):
        super().__init__(
            expand=2,
            sections_space=0,
            center_space_radius=0,
            height=self._SECTION_RADIUS*2,
            start_degree_offset=-90,
        )

        def on_hover(e: ft.PieChartEvent):
            # iosの場合、Noneになる
            section_index = e.section_index if e.section_index is not None else -1

            # 他のホバーしているところから映った際にホバーしていたセクションのコンテナを非表示にする
            def before_badge_divisible():
                if self._before_hover_section_index != -1:
                    before_section = self.sections[self._before_hover_section_index]
                    if before_section.badge is not None:
                        before_section.badge.opacity = 0
                        before_section.badge.update()

            # どこにもホバーがされていないとき
            if section_index == -1:
                before_badge_divisible()
                self._before_hover_section_index = -1
                return
            elif self._before_hover_section_index == section_index:
                return

            section: ft.PieChartSection = self.sections[section_index]
            before_badge_divisible()
            self._before_hover_section_index = section_index
            if section.badge is not None:
                section.badge.opacity = 1
                section.badge.update()

        self.on_chart_event = on_hover

    def create_section(self, label: str, value: Union[int, float], color: str):
        return ft.PieChartSection(
            value,
            color=color,
            title=label,
            radius=self._SECTION_RADIUS,
            badge=ft.Container(
                content=ft.Text(
                    value=f'{label}: {value}'
                ),
                padding=ft.padding.all(10),
                border_radius=10,
                bgcolor=ft.colors.SECONDARY_CONTAINER,
                opacity=0,
                animate_opacity=100,
            ),
            badge_position=1.25,
        )

    def set_data(self, labels: list[str], values: list[Union[int, float]], colors: list[str]):
        self._labels = labels
        self._values = values
        self._colors = colors
        if not (len(self._labels) == len(self._values) == len(self._colors)):
            raise ValueError('プロットデータの要素数が一致しません')

        sections: list[ft.PieChartSection] = []
        for i in range(len(self._labels)):
            sections.append(
                self.create_section(
                    self._labels[i],
                    self._values[i],
                    self._colors[i],
                )
            )
        self.sections = sections


class PieChartComponent(ft.Row):
    """円グラフのメインコンポーネント"""

    def __init__(self, title: str, labels: list[str], values: list[Union[int, float]], colors: list[str], sortable: bool = True, has_other: bool = True):
        super().__init__(
            expand=True,
        )
        self._sortable = sortable
        self._has_other = has_other

        self._label_list = ft.ListView(
            expand=1,
            spacing=10,
            padding=ft.padding.symmetric(horizontal=20),
            auto_scroll=False,
        )

        self._pie_chart = PieChart()

        self._title = title
        self._title_label = ft.Text(
            size=18,
            weight=ft.FontWeight.BOLD,
            value=self._title,
        )

        self.controls = [
            ft.Column(
                controls=[
                    self._title_label,
                    self._label_list,
                ],
                expand=1,
                spacing=15,
            ),
            self._pie_chart,
        ]

        self._set_data(labels, values, colors)

    def _check_list(self):
        """データが正しいかを確認"""
        if (
            self._has_other
            and len(self._labels) != len(self._values)
            and len(self._colors) < 1
        ) or (
            not self._has_other
            and not (len(self._labels) == len(self._values) == len(self._colors))
        ):
            raise ValueError('プロットデータの要素数が一致しません')

    def _sort_data(self):
        if not self._sortable:
            return

        before_sorted_data = [
            (self._labels[i], self._values[i], self._colors[i] if not self._has_other else None)
            for i in range(len(self._labels))
        ]
        sorted_data = sorted(
            before_sorted_data,
            key=lambda x: x[1],
            reverse=True,
        )
        self._labels = [x[0] for x in sorted_data]
        self._values = [x[1] for x in sorted_data]
        if not self._has_other:
            self._colors = [x[2] for x in sorted_data]

    def _processing_list(self):
        """リストの加工を行います"""

        # その他ありのリストではカラーリストが基準となってデータが変動する
        # つまり、カラーリストに6個の色があるならば
        # データの上位5個のデータが採用され、他のデータはすべて「その他」としてグルーピングされる
        if not self._has_other:
            return

        cutting_count = len(self._colors) - 1
        # データが一致しているならその他カラーを削除する
        if cutting_count == len(self._labels):
            self._colors = self._colors[:cutting_count]
            return

        integration_value = sum(self._values[cutting_count:])
        self._labels = [*self._labels[:cutting_count], 'その他']
        self._values = [*self._values[:cutting_count], integration_value]

    def _make_data_list(self, labels: list[str], values: list[Union[int, float]]) -> list['GraphLabelItem']:
        """データからラベルリストを生成します"""
        label_list = []
        for i in range(len(labels)):
            label_list.append(
                GraphLabelItem(
                    self._colors[min(len(self._colors) - 1, i)], f'{labels[i]} {values[i]}'
                )
            )
        return label_list

    def _set_data(self, labels: list[str], values: list[Union[int, float]], colors: list[str]):
        """円グラフ総合入れ替え処理"""
        self._labels = labels
        self._values = values
        self._colors = colors
        self._check_list()

        self._sort_data()
        label_text_data = self._labels
        label_value_data = self._values
        self._processing_list()

        self._pie_chart.set_data(
            self._labels,
            self._values,
            self._colors,
        )

        label_list = self._make_data_list(label_text_data, label_value_data)
        self._label_list.controls = label_list

    def update_chart(self, labels: list[str], values: list[Union[int, float]], colors: list[str]):
        """チャートを更新します"""
        self._set_data(labels, values, colors)
        self.update()


class GraphLabelItem(ft.Row):
    """円グラフのラベル"""

    def __init__(self, color: str, label: str):
        super().__init__(
            expand=True,
            spacing=10,
        )

        self._color = color
        self._color_container = ft.Container(
            bgcolor=self._color,
            width=10,
            height=10,
        )

        self._label = label
        self._label_text = ft.Text(
            value=self._label,
            expand=True,
        )

        self.controls = [
            self._color_container,
            self._label_text,
        ]
