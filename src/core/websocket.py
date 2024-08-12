import traceback

import json

import asyncio
import websockets
import websockets.exceptions

from core import wsmsg

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
                else:
                    if 'error' in data:
                        data['error'](body)
            match op:
                case 'user_update':
                    pass
                case 'emoji_update':
                    pass
                case 'emoji_delete':
                    pass
                case 'risk_update':
                    pass
                case 'reason_update':
                    pass
                case 'denied':
                    pass
                case 'misskey_api_error':
                    pass
                case 'misskey_unknown_error':
                    pass
                case 'error':
                    pass
                case 'internal_error':
                    pass
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
    msg = op.build()
    pending[op.reqid] = {'msg': msg, 'callback': callback_auth, 'error': error_auth}
    await ws.send(msg)

