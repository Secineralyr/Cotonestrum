import enum
from typing import Union, Optional

import flet as ft


class Views(enum.Enum):
    DASHBOARD = enum.auto()
    EMOJIS = enum.auto()
    DELETED = enum.auto()
    USERS = enum.auto()
    REASONS = enum.auto()
    LOGS = enum.auto()
    SETTINGS = enum.auto()


class SidebarButtonInfo(object):
    __DASHBOARD = (ft.icons.HOME_OUTLINED, ft.icons.HOME_ROUNDED, 'ダッシュボード')
    __EMOJIS = (ft.icons.EMOJI_EMOTIONS_OUTLINED, ft.icons.EMOJI_EMOTIONS, '絵文字一覧')
    __DELETED = (ft.icons.DELETE_OUTLINE, ft.icons.DELETE, '削除済み絵文字')
    __USERS = (ft.icons.PERSON_OUTLINED, ft.icons.PERSON, 'ユーザー情報')
    __REASONS = (ft.icons.BALLOT_OUTLINED, ft.icons.BALLOT, '理由区分管理')
    __LOGS = (ft.icons.TASK_OUTLINED, ft.icons.TASK, 'ログ/タスク')
    __SETTINGS = (ft.icons.SETTINGS_OUTLINED, ft.icons.SETTINGS, '設定')

    @classmethod
    def get_info(cls, view: Views) -> tuple:
        match view:
            case Views.DASHBOARD:
                return cls.__DASHBOARD
            case Views.EMOJIS:
                return cls.__EMOJIS
            case Views.DELETED:
                return cls.__DELETED
            case Views.USERS:
                return cls.__USERS
            case Views.REASONS:
                return cls.__REASONS
            case Views.LOGS:
                return cls.__LOGS
            case Views.SETTINGS:
                return cls.__SETTINGS
        raise ValueError('Undefined View')

    @classmethod
    def _get_single_info(cls, view: Views, index: int) -> Union[Optional[str], str]:
        return cls.get_info(view)[index]

    @classmethod
    def get_unselected_icon(cls, view: Views) -> Optional[str]:
        return cls._get_single_info(view, 0)

    @classmethod
    def get_selected_icon(cls, view: Views) -> Optional[str]:
        return cls._get_single_info(view, 1)

    @classmethod
    def get_text(cls, view: Views) -> str:
        return cls._get_single_info(view, 2)
