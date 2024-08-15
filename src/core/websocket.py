import traceback

import json

import asyncio
import websockets
import websockets.exceptions

from core import wsmsg
from core import registry

ws = None
task = None
pending = {}

async def connect(server_host, page):
    global ws, task
    if ws is not None:
        return
    page.data['settings'].set_connect_state(1)
    if ':'  not in server_host:
        server_host += ':3005'
    try:
        uri = f'ws://{server_host}/'
        ws = await websockets.connect(uri)
    except (OSError, TimeoutError, websockets.exceptions.InvalidURI, websockets.exceptions.InvalidHandshake):
        traceback.print_exc()
        print('websocket connection could not opened')
        page.data['settings'].set_connect_state(0)
    else:
        task = asyncio.create_task(reception(ws, page))
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

async def create_send_task(op, callback = None, error_callback = None):
    msg = op.build()
    operation = {'msg': msg}
    if callback is not None:
        operation['callback'] = callback
    if error_callback is not None:
        operation['error'] = error_callback
    pending[op.reqid] = operation
    asyncio.create_task(ws.send(msg))

async def reception(ws, page):
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
                elif op == 'internal_error':
                    log_subject = '内部エラーが発生しました'
                    log_text = f"操作: {body['op']}\n追記: {body['message']}\nこれはサーバー側の問題です。直らない場合報告してください。"
                    is_error = True
                else:
                    log_subject = 'エラーが発生しました'
                    log_text = f"操作: {body['op']}\n追記: {body['message']}"
                    is_error = True
                    if 'error' in operation:
                        ret = operation['error'](body, data['op'], page)
                        if ret is not None:
                            log_subject, log_text = ret
                page.data['logs'].write_log(log_subject, log_text, data, is_error)
            elif reqid is None:
                match op:
                    case 'user_update':
                        registry.put_user(body['id'], body['misskey_id'], body['username'])
                        log_subject = 'ユーザーのデータを取得しました'
                        log_text = ''
                        is_error = False
                    case 'emoji_update':
                        registry.put_emoji(body['id'], body['misskey_id'], body['name'], body['category'], body['tags'], body['url'], body['is_self_made'], body['license'], body['owner_id'], body['created_at'], body['updated_at'])
                        page.data['emojis'].list_emoji.update_emoji(body['id'])
                        log_subject = '絵文字のデータを取得しました'
                        log_text = ''
                        is_error = False
                    case 'emoji_delete':
                        registry.pop_emoji(body['id'])
                        page.data['emojis'].list_emoji.delete_emoji(body['id'])
                        log_subject = '絵文字のデータが削除されました'
                        log_text = ''
                        is_error = False
                    case 'risk_update':
                        registry.put_risk(body['id'], body['checked'], body['level'], body['reason_genre'], body['remark'], body['created_at'], body['updated_at'])
                        log_subject = 'リスクのデータを取得しました'
                        log_text = ''
                        is_error = False
                    case 'reason_update':
                        registry.put_reason(body['id'], body['text'], body['created_at'], body['updated_at'])
                        log_subject = '理由区分のデータを取得しました'
                        log_text = ''
                        is_error = False
                    case 'reason_delete':
                        registry.pop_reason(body['id'])
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
        except:
            traceback.print_exc()


async def auth(token, page):
    global ws
    if ws is None:
        return
    page.data['settings'].set_auth_state(1)

    def callback_auth(body, page):
        match body['message']:
            case "You logged in as 'User'.":
                page.data['settings'].set_auth_state(2)
            case "You logged in as 'Emoji moderator'.":
                page.data['settings'].set_auth_state(3)
            case "You logged in as 'Moderator'.":
                page.data['settings'].set_auth_state(4)
            case "You logged in as 'Administrator'.":
                page.data['settings'].set_auth_state(5)
    
    def error_auth(body, err, page):
        page.data['settings'].set_auth_state(0)

    op = wsmsg.Auth(token)
    await create_send_task(op, callback_auth, error_auth)




