import flet as ft

from core import websocket

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


        def check_addr(e):
            if self.is_valid_addrport():
                self.addr.error_text = None
                self.button_connect.disabled = False
            else:
                self.addr.error_text = '正しいアドレスを入力してください。'
                self.button_connect.disabled = True
            self.page.update()

        async def connect(e):
            if self.connect_state == 0:
                await websocket.connect(self.addr.value, self)
            elif self.connect_state == 2:
                await websocket.disconnect(self)

        async def auth(e):
            token = self.mi_token.value
            await websocket.auth(token, self)

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

        self.button_connect = ft.FilledButton(
            content=ft.Text(
                value='接続',
                style=ft.TextStyle(weight=ft.FontWeight.BOLD),
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(3)
            ),
            on_click=connect,
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
            on_click=auth,
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
            ],
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
        )
    
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
        self.page.update()
    
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
        self.page.update()

