import abc
import uuid

import json

class IWSMessage(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def _build_json(self) -> dict:
        raise NotImplementedError()
    
    def build(self) -> str:
        return json.dumps(self._build_json())

class IWSOperation(IWSMessage):
    def __init__(self, op) -> None:
        self.op = op
        self.reqid = str(uuid.uuid4())


class Auth(IWSOperation):
    def __init__(self, token) -> None:
        super().__init__('auth')
        self.token = token

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {
                    'token': self.token
                }
            }

class FetchEmoji(IWSOperation):
    def __init__(self, eid) -> None:
        super().__init__('fetch_emoji')
        self.id = eid

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {
                    'id': self.id
                }
            }

class FetchAllEmojis(IWSOperation):
    def __init__(self) -> None:
        super().__init__('fetch_all_emojis')

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {}
            }

class FetchUser(IWSOperation):
    def __init__(self, uid) -> None:
        super().__init__('fetch_user')
        self.id = uid

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {
                    'id': self.id
                }
            }

class FetchAllUsers(IWSOperation):
    def __init__(self) -> None:
        super().__init__('fetch_all_users')

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {}
            }

class FetchRisk(IWSOperation):
    def __init__(self, rid) -> None:
        super().__init__('fetch_risk')
        self.id = rid

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {
                    'id': self.id
                }
            }

class FetchAllRisks(IWSOperation):
    def __init__(self) -> None:
        super().__init__('fetch_all_risks')

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {}
            }

class FetchReason(IWSOperation):
    def __init__(self, rsid) -> None:
        super().__init__('fetch_reason')
        self.id = rsid

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {
                    'id': self.id
                }
            }

class FetchAllReasons(IWSOperation):
    def __init__(self) -> None:
        super().__init__('fetch_all_reasons')

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {}
            }


class SetRiskProp(IWSOperation):
    def __init__(self, rid, checked=-1, level=-1, rsid=None, remark=None) -> None:
        super().__init__('set_risk_prop')
        self.id = rid
        props = {}
        if checked in [0, 1]:
            props['checked'] = checked
        if level in [None, 0, 1, 2, 3]:
            props['level'] = level
        if rsid is not None:
            props['reason_id'] = rsid
        if remark is not None:
            props['remark'] = remark
        self.props = props

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {
                    'id': self.id,
                    'props': self.props
                }
            }

class CreateReason(IWSOperation):
    def __init__(self, text) -> None:
        super().__init__('create_reason')
        self.text = text

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {
                    'text': self.text
                }
            }

class DeleteReason(IWSOperation):
    def __init__(self, rsid) -> None:
        super().__init__('delete_reason')
        self.id = rsid

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {
                    'id': self.id
                }
            }

class SetReasonText(IWSOperation):
    def __init__(self, rsid, text) -> None:
        super().__init__('set_reason_text')
        self.id = rsid
        self.text = text

    def _build_json(self) -> dict:
        return \
            {
                'op': self.op,
                'reqid': self.reqid,
                'body': {
                    'id': self.id,
                    'text': self.text
                }
            }

