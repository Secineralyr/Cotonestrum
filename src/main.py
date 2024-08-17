import flet as ft

from app.root import Root

async def main(page: ft.Page):

    def window_event_handler(e):
        if e.data == 'close':
            page.window.destroy()

    page.title = 'misskey.dream Emoji Moderation Tool'

    page.window.min_width = 1280
    page.window.min_height = 720
    page.window.width = 1280
    page.window.height = 720

    page.fonts = {
        'IBM Plex Sans JP': 'https://github.com/google/fonts/raw/main/ofl/ibmplexsansjp/IBMPlexSansJP-Regular.ttf',
        'M PLUS 1 Code': 'https://github.com/google/fonts/raw/main/ofl/mplus1code/MPLUS1Code%5Bwght%5D.ttf',
    }
    
    page.theme = ft.Theme(font_family='IBM Plex Sans JP')

    page.theme_mode = 'DARK'

    page.window.prevent_close = True
    page.window.on_event = window_event_handler

    page.data = {}
    
    root = Root()

    page.data['root'] = root

    page.padding = 0

    page.add(root)
    page.update()

if __name__ == '__main__':
    ft.app(target=main, view=ft.AppView.FLET_APP)

