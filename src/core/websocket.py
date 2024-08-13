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

async def connect(server_host, panel_settings):
    global ws, task
    if ws is not None:
        return
    panel_settings.set_connect_state(1)
    if ':'  not in server_host:
        server_host += ':3005'
    try:
        uri = f'ws://{server_host}/'
        ws = await websockets.connect(uri)
    except (OSError, TimeoutError, websockets.exceptions.InvalidURI, websockets.exceptions.InvalidHandshake):
        traceback.print_exc()
        print('websocket connection could not opened')
        panel_settings.set_connect_state(0)
    else:
        task = asyncio.create_task(reception(ws))
        print('websocket connection opened')
        panel_settings.set_connect_state(2)

async def disconnect(panel_settings):
    global ws, task
    if ws is None:
        return
    await ws.close()
    task.cancel()
    print('websocket connection closed')
    ws = None
    panel_settings.set_connect_state(0)

async def create_send_task(op, callback, error_callback):
    msg = op.build()
    pending[op.reqid] = {'msg': msg, 'callback': callback, 'error': error_callback}
    asyncio.create_task(ws.send(msg))

async def reception(ws):
    while True:
        try:
            data = json.loads(await ws.recv())
            op = data['op']
            reqid = data['reqid'] if 'reqid' in data else None
            body = data['body']
            if reqid in pending:
                data = pending.pop(reqid)
                if op == 'ok':
                    if 'callback' in data:
                        data['callback'](body)
                elif op == 'denied':
                    pass # todo
                else:
                    if 'error' in data:
                        data['error'](body)
            if reqid is None:
                match op:
                    case 'user_update':
                        registry.put_user(body['id'], body['misskey_id'], body['username'])
                    case 'emoji_update':
                        registry.put_emoji(body['id'], body['misskey_id'], body['name'], body['category'], body['tags'], body['url'], body['is_self_made'], body['license'], body['owner_id'], body['created_at'], body['updated_at'])
                    case 'emoji_delete':
                        registry.pop_emoji(body['id'])
                    case 'risk_update':
                        registry.put_risk(body['id'], body['checked'], body['level'], body['reason_genre'], body['remark'], body['created_at'], body['updated_at'])
                    case 'reason_update':
                        registry.put_reason(body['id'], body['text'], body['created_at'], body['updated_at'])
                    case 'misskey_api_error':
                        pass # todo
                    case 'misskey_unknown_error':
                        pass # todo
                    case 'error':
                        pass # todo
                    case 'internal_error':
                        pass # todo
        except asyncio.exceptions.CancelledError:
            break
        except websockets.ConnectionClosed:
            break
        except:
            traceback.print_exc()


async def auth(token, panel_settings):
    global ws
    if ws is None:
        return
    panel_settings.set_auth_state(1)

    def callback_auth(body):
        match body['message']:
            case "You logged in as 'User'.":
                panel_settings.set_auth_state(2)
            case "You logged in as 'Emoji moderator'.":
                panel_settings.set_auth_state(3)
            case "You logged in as 'Moderator'.":
                panel_settings.set_auth_state(4)
            case "You logged in as 'Administrator'.":
                panel_settings.set_auth_state(5)
    
    def error_auth(body):
        panel_settings.set_auth_state(0)

    op = wsmsg.Auth(token)
    await create_send_task(op, callback_auth, error_auth)




