import os.path as osp

import json

import flet as ft

from core import websocket


SETTING_FILE_PATH = osp.join(osp.abspath('.'), 'settings.json')

class PanelSettings(ft.Container):

    def __init__(self):
        super().__init__()

        # 0: disconnected
        # 1: connecting
        # 2: connected
        self.connect_state = 0

        # 0: no auth (or disconnected)
        # 1: authenticating
        # 2: user
        # 3: emoji moderator
        # 4: moderator
        # 5: admin
        self.auth_state = 0

        self.enable_tooltip = True

        def check_addr(e):
            self.check_addr()
        
        def toggle_tooltip(e):
            self.save()
            self.enable_tooltip = self.switch_tooltip.value

        self.addr = ft.TextField(
            label='Emoji Moderation Serverのアドレス',
            label_style=ft.TextStyle(size=13),
            hint_text='192.168.x.x:yyyyy',
            on_change=check_addr,
        )

        self.mi_token = ft.TextField(
            label='Misskeyトークン',
            password=True,
            can_reveal_password=True,
        )

        self.switch_tooltip = ft.Switch(
            label='ツールチップ表示',
            value=True,
            splash_radius=0,
            on_change=toggle_tooltip,
        )

        self.button_connect = ft.FilledButton(
            content=ft.Text(
                value='接続',
                style=ft.TextStyle(weight=ft.FontWeight.BOLD),
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(3)
            ),
            on_click=self.connect,
            disabled=True,
        )
        self.status_connection = ft.TextSpan(
            text='切断',
            style=ft.TextStyle(
                color='#ff4040',
                weight=ft.FontWeight.BOLD,
            ),
        )

        self.button_auth = ft.FilledButton(
            content=ft.Text(
                value='認証',
                style=ft.TextStyle(weight=ft.FontWeight.BOLD),
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(3)
            ),
            on_click=self.auth,
            disabled=True,
        )
        self.status_perm = ft.TextSpan(
            text='',
            style=ft.TextStyle(
                color='#ff4040',
                weight=ft.FontWeight.BOLD,
            ),
        )
        self.status_auth = ft.Text(
            value='先にサーバーに接続してください',
            color='#ff4040',
            style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
            ),
            spans=[self.status_perm],
        )


        self.expand = True
        self.margin = 15
        self.alignment = ft.alignment.top_left

        self.content = ft.Column(
            controls=[
                ft.Text(
                    value='設定',
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=10),
                ft.Text(
                    value='サーバー接続',
                    size=20,
                    color='#8c929f',
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=5),
                ft.Row(
                    controls=[
                        self.addr,
                        ft.Tooltip(
                            message='''\
このツール用のサーバーが稼働しているアドレスを入力してください。
ポート番号を省略した場合デフォルトの3005番が使用されます。\
''',
                            content=ft.Icon(
                                name=ft.icons.HELP_ROUNDED,
                                color='#c3c7cf',
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    controls=[
                        self.button_connect,
                        ft.Text(
                            value='接続状態: ',
                            spans=[self.status_connection],
                        ),
                    ],
                ),
                ft.Container(height=10),
                ft.Row(
                    controls=[
                        self.mi_token,
                        ft.Tooltip(
                            message='''\
このツールは絵文字モデレーター以上でなければ使用することができません。
あなたが誰であるかを確認するためにトークンが必要になります。
設定画面からトークンを生成して貼り付けてください。ここで必要な権限は「アカウントの情報を見る」のみです。\
''',
                            content=ft.Icon(
                                name=ft.icons.HELP_ROUNDED,
                                color='#c3c7cf',
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    controls=[
                        self.button_auth,
                        self.status_auth,
                    ],
                ),
                ft.Divider(
                    height=5,
                ),
                ft.Text(
                    value='クライアント設定',
                    size=20,
                    color='#8c929f',
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=5),
                ft.Row(
                    controls=[
                        self.switch_tooltip,
                        ft.Tooltip(
                            message='''\
「絵文字一覧」画面で、項目のテキストなどが表示しきれない場合にツールチップを表示するようにするかどうかです。
OFFにすると動作が軽くなりますが、長い文字列に遭遇した場合全文を読むことができない為、非推奨です。
''',
                            content=ft.Icon(
                                name=ft.icons.HELP_ROUNDED,
                                color='#c3c7cf',
                            ),
                        ),
                    ],
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
        )

    def did_mount(self):
        self.load()
        self.check_addr()
        async def connect():
            if self.is_valid_addrport():
                await self.connect(None)
                if self.connect_state == 2:
                    self.auth(None)
        self.page.run_task(connect)

    def save(self):
        addr = self.addr.value
        token = self.mi_token.value
        tt = self.switch_tooltip.value
        data = {
            'addr': addr,
            'token': token,
            'tooltip': tt,
        }
        with open(SETTING_FILE_PATH, 'wt') as fs:
            json.dump(data, fs, indent=2, separators=(',', ': '))
    
    def load(self):
        addr = ''
        token = ''
        tt = True
        if osp.isfile(SETTING_FILE_PATH):
            with open(SETTING_FILE_PATH, 'rt') as fs:
                data = json.load(fs)
                if 'addr' in data:
                    addr = data['addr']
                if 'token' in data:
                    token = data['token']
                if 'tooltip' in data:
                    tt = data['tooltip']
        self.addr.value = addr
        self.mi_token.value = token
        self.switch_tooltip.value = tt
        self.enable_tooltip = tt
        self.addr.update()
        self.mi_token.update()
        self.switch_tooltip.update()

    def check_addr(self):
        if self.is_valid_addrport():
            self.addr.error_text = None
            self.button_connect.disabled = False
        else:
            self.addr.error_text = '正しいアドレスを入力してください。'
            self.button_connect.disabled = True
        self.addr.update()
        self.button_connect.update()

    async def connect(self, e):
        self.save()
        if self.connect_state == 0:
            await websocket.connect(self.addr.value, self.page)
        elif self.connect_state == 2:
            await websocket.disconnect(self.page)

    def auth(self, e):
        self.save()
        token = self.mi_token.value
        websocket.auth(token, self.page)

    def is_valid_addrport(self):
        addrp = self.addr.value

        z = addrp.split(':')

        if len(z) == 0 or len(z) > 2:
            return False
        
        if len(z) == 2:
            a, p = z
        else:
            a, p = z[0], '3005'
        
        try:
            port = int(p)
        except ValueError:
            return False

        if port < 1 or port > 65535:
            return False

        if a != 'localhost':
            w = a.split('.')
            if len(w) != 4:
                return False
            
            try:
                words = [int(i) for i in w]
            except ValueError:
                return False
            
            for word in words:
                if word < 0 or word > 255:
                    return False
            
        return True
    
    def set_connect_state(self, state: int):
        self.connect_state = state
        if self.connect_state == 0 or self.connect_state == 1:
            self.auth_state = 0
        match state:
            case 0:
                self.addr.disabled = False

                self.button_connect.content.value = '接続'
                self.status_connection.text = '切断'
                self.status_connection.style.color = '#ff4040'

                self.button_auth.disabled = True
                self.status_auth.value = '先にサーバーに接続してください'
                self.status_auth.color = '#ff4040'
                self.status_auth.style.weight = ft.FontWeight.BOLD
                self.status_perm.text = ''
                self.status_perm.style.color = '#ff4040'
            case 1:
                self.addr.disabled = True

                self.button_connect.content.value = '接続'
                self.status_connection.text = '接続中'
                self.status_connection.style.color = '#ffff40'

                self.button_auth.disabled = True
                self.status_auth.value = '先にサーバーに接続してください'
                self.status_auth.color = '#ff4040'
                self.status_auth.style.weight = ft.FontWeight.BOLD
                self.status_perm.text = ''
                self.status_perm.style.color = '#ff4040'
            case 2:
                self.addr.disabled = True

                self.button_connect.content.value = '切断'
                self.status_connection.text = '接続済'
                self.status_connection.style.color = '#40ff40'

                if self.auth_state == 0:
                    self.button_auth.disabled = False
                    self.status_auth.value = '認証状態: '
                    self.status_auth.color = '#e1e2e8'
                    self.status_auth.style.weight = ft.FontWeight.NORMAL
                    self.status_perm.text = '未認証'
                    self.status_perm.style.color = '#ff4040'
        self.update()
    
    def set_auth_state(self, state: int):
        if self.connect_state != 2:
            return
        match state:
            case 0:
                self.mi_token.disabled = False
                self.button_auth.disabled = False
                self.status_perm.text = '未認証'
                self.status_perm.style.color = '#ff4040'
            case 1:
                self.mi_token.disabled = True
                self.button_auth.disabled = True
                self.status_perm.text = '認証中'
                self.status_perm.style.color = '#ffff40'
            case 2:
                self.mi_token.disabled = False
                self.button_auth.disabled = False
                self.status_perm.text = '認証済 (権限レベル: 一般ユーザー)'
                self.status_perm.style.color = '#ffa040'
            case 3:
                self.mi_token.disabled = False
                self.button_auth.disabled = False
                self.status_perm.text = '認証済 (権限レベル: 絵文字モデレーター)'
                self.status_perm.style.color = '#40ff40'
            case 4:
                self.mi_token.disabled = False
                self.button_auth.disabled = False
                self.status_perm.text = '認証済 (権限レベル: モデレーター)'
                self.status_perm.style.color = '#40ff40'
            case 5:
                self.mi_token.disabled = False
                self.button_auth.disabled = False
                self.status_perm.text = '認証済 (権限レベル: 管理者)'
                self.status_perm.style.color = '#40ff40'
        self.update()

