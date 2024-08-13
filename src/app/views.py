import enum
from typing import Union, Optional

import flet as ft


class Views(enum.Enum):
    EMOJIS = enum.auto()
    USERS = enum.auto()
    SETTINGS = enum.auto()
    LOGS = enum.auto()


class SidebarButtonInfo(object):
    __EMOJIS = (ft.icons.EMOJI_EMOTIONS_OUTLINED, ft.icons.EMOJI_EMOTIONS, '絵文字一覧')
    __USERS = (ft.icons.PERSON_OUTLINED, ft.icons.PERSON, 'ユーザー情報')
    __SETTINGS = (ft.icons.SETTINGS_OUTLINED, ft.icons.SETTINGS, '設定')
    __LOGS = (ft.icons.TASK_OUTLINED, ft.icons.TASK, 'ログ/タスク')

    @classmethod
    def get_info(cls, view: Views) -> tuple:
        match view:
            case Views.EMOJIS:
                return cls.__EMOJIS
            case Views.USERS:
                return cls.__USERS
            case Views.SETTINGS:
                return cls.__SETTINGS
            case Views.LOGS:
                return cls.__LOGS

    @classmethod
    def _get_single_info(cls, view: Views, index: int) -> Union[Optional[str], str]:
        return cls.getInfo(view)[index]
    
    @classmethod
    def get_unselected_icon(cls, view: Views) -> Optional[str]:
        return cls._get_single_info(view, 0)

    @classmethod
    def get_selected_icon(cls, view: Views) -> Optional[str]:
        return cls._get_single_info(view, 1)

    @classmethod
    def get_text(cls, view: Views) -> str:
        return cls._get_single_info(view, 2)
