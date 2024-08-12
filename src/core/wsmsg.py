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
