import traceback

import json

import asyncio
import websockets
import websockets.exceptions

from app.panels.dashboard import PanelDashboard
from core import wsmsg
from core import registry
from app.views import Views

ws = None
task = None
pending = {}

async def connect(server_host, page):
    global ws, task
    if ws is not None:
        return
    page.data['settings'].set_connect_state(1)
    if ':' not in server_host:
        server_host += ':3005'
    try:
        uri = f'ws://{server_host}/'
        ws = await websockets.connect(uri, max_size=None)
    except (OSError, TimeoutError, websockets.exceptions.InvalidURI, websockets.exceptions.InvalidHandshake):
        traceback.print_exc()
        print('websocket connection could not opened')
        page.data['settings'].set_connect_state(0)
    else:
        task = page.run_task(reception, ws, page)
        print('websocket connection opened')
        page.data['settings'].set_connect_state(2)

async def disconnect(page):
    global ws, task
    if ws is None:
        return
    await ws.close()
    task.cancel()
    print('websocket connection closed')
    ws = None
    page.data['settings'].set_connect_state(0)

def create_send_task(op, page, callback = None, error_callback = None):
    msg = op.build()
    operation = {'msg': msg}
    if callback is not None:
        operation['callback'] = callback
    if error_callback is not None:
        operation['error'] = error_callback
    pending[op.reqid] = operation
    page.run_task(ws.send, msg)

async def reception(ws, page):
    from app.panels.emojis import PanelEmojis
    from app.panels.logs import PanelLogs
    panel_emojis: PanelEmojis = page.data['emojis']
    panel_logs: PanelLogs = page.data['logs']
    while True:
        try:
            data = json.loads(await ws.recv())
            op = data['op']
            reqid = data['reqid'] if 'reqid' in data else None
            body = data['body']
            if reqid in pending:
                operation = pending.pop(reqid)
                if op == 'ok':
                    log_subject = '操作は完了しました'
                    log_text = f"操作: {body['op']}"
                    is_error = False
                    if 'callback' in operation:
                        ret = operation['callback'](body, page)
                        if ret is not None:
                            log_subject, log_text = ret
                elif op == 'denied':
                    log_subject = '操作が拒否されました'
                    log_text = f"操作: {body['op']}\n追記: {body['message']}\n必要な権限が不足している可能性があります。"
                    is_error = True
                    if 'error' in operation:
                        ret = operation['error'](body, data['op'], page)
                        if ret is not None:
                            log_subject, log_text = ret
                elif op == 'internal_error':
                    log_subject = '内部エラーが発生しました'
                    log_text = f"操作: {body['op']}\n追記: {body['message']}\nこれはサーバー側の問題です。直らない場合報告してください。"
                    is_error = True
                    if 'error' in operation:
                        ret = operation['error'](body, data['op'], page)
                        if ret is not None:
                            log_subject, log_text = ret
                else:
                    log_subject = 'エラーが発生しました'
                    log_text = f"操作: {body['op']}\n追記: {body['message']}"
                    is_error = True
                    if 'error' in operation:
                        ret = operation['error'](body, data['op'], page)
                        if ret is not None:
                            log_subject, log_text = ret
                panel_logs.write_log(log_subject, log_text, data, is_error)
            elif reqid is None:
                match op:
                    case 'user_update':
                        registry.put_user(body['id'], body['misskey_id'], body['username'])

                        if page.data['root'].current_view == Views.DASHBOARD:
                            page.data['dashboard'].reload_users()

                        log_subject = 'ユーザーのデータを取得しました'
                        log_text = ''
                        is_error = False
                    case 'users_update':
                        for i in body:
                            registry.put_user(i['id'], i['misskey_id'], i['username'])

                        if page.data['root'].current_view == Views.DASHBOARD:
                            page.data['dashboard'].reload_users()

                        log_subject = '複数のユーザーのデータを取得しました'
                        log_text = ''
                        is_error = False
                    case 'emoji_update':
                        registry.put_emoji(body['id'], body['misskey_id'], body['name'], body['category'], body['tags'], body['url'], body['is_self_made'], body['license'], body['owner_id'], body['risk_id'], body['created_at'], body['updated_at'])
                        panel_emojis.add_emoji(body['id'])

                        if page.data['root'].current_view == Views.DASHBOARD:
                            page.data['dashboard'].reload_all()

                        log_subject = '絵文字のデータを取得しました'
                        log_text = ''
                        is_error = False
                    case 'emojis_update':
                        for i in body:
                            registry.put_emoji(i['id'], i['misskey_id'], i['name'], i['category'], i['tags'], i['url'], i['is_self_made'], i['license'], i['owner_id'], i['risk_id'], i['created_at'], i['updated_at'])
                        panel_emojis.add_emojis([i['id'] for i in body])

                        if page.data['root'].current_view == Views.DASHBOARD:
                            page.data['dashboard'].reload_all()

                        log_subject = '絵文字のデータを取得しました'
                        log_text = ''
                        is_error = False
                    case 'emoji_delete':
                        registry.pop_emoji(body['id'])
                        panel_emojis.remove_emoji(body['id'])

                        if page.data['root'].current_view == Views.DASHBOARD:
                            page.data['dashboard'].reload_all()

                        log_subject = '絵文字のデータが削除されました'
                        log_text = ''
                        is_error = False
                    case 'emojis_delete':
                        for i in body['ids']:
                            registry.pop_emoji(i)
                        panel_emojis.remove_emojis([i for i in body['ids']])

                        if page.data['root'].current_view == Views.DASHBOARD:
                            page.data['dashboard'].reload_all()

                        log_subject = '絵文字のデータが削除されました'
                        log_text = ''
                        is_error = False
                    case 'risk_update':
                        rid = body['id']
                        rr = False
                        if rid in registry.risks:
                            rr = True
                        registry.put_risk(rid, body['checked'], body['level'], body['reason_genre'], body['remark'], body['created_at'], body['updated_at'])
                        if rr:
                            page.data['emojis'].list_emoji.reload_risk(rid)

                        if page.data['root'].current_view == Views.DASHBOARD:
                            page.data['dashboard'].reload_risks()

                        log_subject = 'リスクのデータを取得しました'
                        log_text = ''
                        is_error = False
                    case 'risks_update':
                        for i in body:
                            registry.put_risk(i['id'], i['checked'], i['level'], i['reason_genre'], i['remark'], i['created_at'], i['updated_at'])

                        if page.data['root'].current_view == Views.DASHBOARD:
                            page.data['dashboard'].reload_risks()

                        log_subject = 'リスクのデータを取得しました'
                        log_text = ''
                        is_error = False
                    case 'reason_update':
                        registry.put_reason(body['id'], body['text'], body['created_at'], body['updated_at'])
                        page.data['reasons'].update_reason(body['id'], body['text'])
                        page.data['emojis'].reload_reasons()

                        if page.data['root'].current_view == Views.DASHBOARD:
                            page.data['dashboard'].reload_reasons()

                        log_subject = '理由区分のデータを取得しました'
                        log_text = ''
                        is_error = False
                    case 'reasons_update':
                        for i in body:
                            registry.put_reason(i['id'], i['text'], i['created_at'], i['updated_at'])
                            page.data['reasons'].update_reason(i['id'], i['text'])
                        page.data['emojis'].reload_reasons()

                        if page.data['root'].current_view == Views.DASHBOARD:
                            page.data['dashboard'].reload_reasons()

                        log_subject = '理由区分のデータを取得しました'
                        log_text = ''
                        is_error = False
                    case 'reason_delete':
                        registry.pop_reason(body['id'])
                        page.data['reasons'].remove_reason(body['id'])
                        page.data['emojis'].reload_reasons()

                        if page.data['root'].current_view == Views.DASHBOARD:
                            page.data['dashboard'].reload_reasons()

                        log_subject = '理由区分のデータが削除されました'
                        log_text = ''
                        is_error = False
                    case 'reasons_delete':
                        for i in body['ids']:
                            registry.pop_reason(i)
                            page.data['reasons'].remove_reason(i)
                        page.data['emojis'].reload_reasons()

                        if page.data['root'].current_view == Views.DASHBOARD:
                            page.data['dashboard'].reload_reasons()

                        log_subject = '理由区分のデータが削除されました'
                        log_text = ''
                        is_error = False
                    case 'misskey_api_error':
                        log_subject = 'サーバー側の処理でエラーが発生しました'
                        log_text = 'これはサーバー側のプログラムのバグか設定ミスが原因である可能性が極めて高いです。報告してください。'
                        is_error = True
                    case 'misskey_unknown_error':
                        log_subject = 'サーバー側の処理でエラーが発生しました'
                        log_text = 'これはサーバー側のプログラムのバグか設定ミスが原因である可能性が極めて高いです。報告してください。'
                        is_error = True
                    case 'error':
                        log_subject = 'サーバー側の処理でエラーが発生しました'
                        log_text = 'これはサーバー側のプログラムのバグか設定ミスが原因である可能性が極めて高いです。報告してください。'
                        is_error = True
                    case 'internal_error':
                        log_subject = 'サーバー側の処理で内部エラーが発生しました'
                        log_text = 'これはサーバー側のプログラムのバグか設定ミスが原因である可能性が極めて高いです。報告してください。'
                        is_error = True
                    case _:
                        log_subject = f'<{op}>'
                        log_text = ''
                page.data['logs'].write_log(log_subject, log_text, data, is_error)
        except asyncio.exceptions.CancelledError:
            break
        except websockets.ConnectionClosed:
            break
        except Exception:
            traceback.print_exc()


def auth(token, page):
    global ws
    if ws is None:
        return
    page.data['settings'].set_auth_state(1)

    def callback_auth(body, page):
        permitted = False
        bashboard: PanelDashboard = page.data['dashboard']

        permissions = [
            ("You logged in as 'User'.", 2, False),
            ("You logged in as 'Emoji moderator'.", 3, True),
            ("You logged in as 'Moderator'.", 4, True),
            ("You logged in as 'Administrator'.", 5, True),
        ]
        msg = body['message']
        for p in permissions:
            if msg.startswith(p[0]):
                page.data['settings'].set_auth_state(p[1])
                permitted = p[2]
                username = msg[len(f'{p[0]} (Username: '):-1]
                break
        if permitted:
            bashboard.main_frame.welcome_text.update_to_authed_text(username)
            create_send_task(wsmsg.FetchAllEmojis(), page)
            create_send_task(wsmsg.FetchAllUsers(), page)
            create_send_task(wsmsg.FetchAllRisks(), page)
            create_send_task(wsmsg.FetchAllReasons(), page)

    def error_auth(body, err, page):
        page.data['settings'].set_auth_state(0)

    op = wsmsg.Auth(token)
    create_send_task(op, page, callback_auth, error_auth)


def change_risk_level(rid, level, page):
    global ws
    if ws is None:
        return
    op = wsmsg.SetRiskProp(rid, level=level)
    create_send_task(op, page)

def change_reason(rid, rsid, page):
    global ws
    if ws is None:
        return
    if rsid == '':
        rsid = None
    op = wsmsg.SetRiskProp(rid, rsid=rsid)
    create_send_task(op, page)

def change_remark(rid, text, page):
    global ws
    if ws is None:
        return
    op = wsmsg.SetRiskProp(rid, remark=text)
    create_send_task(op, page)

def change_status(rid, status, page):
    global ws
    if ws is None:
        return
    op = wsmsg.SetRiskProp(rid, checked=status)
    create_send_task(op, page)


def create_reason(text, page):
    global ws
    if ws is None:
        return
    op = wsmsg.CreateReason(text)
    create_send_task(op, page)

def delete_reason(rsid, page):
    global ws
    if ws is None:
        return
    op = wsmsg.DeleteReason(rsid)
    create_send_task(op, page)

def change_reason_text(rsid, text, page):
    global ws
    if ws is None:
        return
    op = wsmsg.SetReasonText(rsid, text)
    create_send_task(op, page)
