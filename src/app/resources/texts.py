from dataclasses import dataclass

@dataclass(frozen=True)
class TextFieldsEmojiFiltering:
    DIALOG_TITLE = 'フィルター設定'
    BUTTON_CANCEL = 'キャンセル'
    BUTTON_OK = 'OK'

    MAIN = 'フィルタ機能'
    NAME = '名前'
    CATEGORY = 'カテゴリー'
    TAG = 'タグ'
    SELFMADE = '自作フラグ'
    LICENSE = 'ライセンス表記'
    OWNER = '所有者'
    RISK_LEVEL = '危険度'
    REASON_GENRE = '理由区分'
    REMARK = '備考'
    CHECK_STATUS = '状態'

    SELFMADE_YES = 'はい'
    SELFMADE_NO = 'いいえ'

    RISK_LEVEL_LOW = '低'
    RISK_LEVEL_MEDIUM = '中'
    RISK_LEVEL_HIGH = '高'
    RISK_LEVEL_DANGER = '重大'

    NEED_CHECK = '要チェック'
    CHECKED = 'チェック済'
    NEED_RECHECK = '要再チェック(絵文字更新済)'

    SEARCH_EMPTY = '空の項目のみを検索'

    MISC_NONSET = '未設定'

@dataclass(frozen=True)
class TextFieldsEmojis:
    IMAGE = '画像'
    NAME = '名前'
    CATEGORY = 'カテゴリー'
    TAG = 'タグ'
    SELFMADE = '自作\nフラグ'
    LICENSE = 'ライセンス表記'
    OWNER = '所有者'
    RISK_LEVEL = '危険度'
    REASON_GENRE = '理由区分'
    REMARK = '備考'
    CHECK_STATUS = '状態'

    IMAGE_DIALOG_TITLE = '画像表示ウィンドウ'

    NEED_CHECK = '要チェック'
    CHECKED = 'チェック済'
    NEED_RECHECK = '要再チェック\n(絵文字更新済)'

    LOAD_MORE = '更に読み込む'

    USERNAME_UNRESOLVED = '<不明>'

    MISC_MIXED = '<混在>'
    MISC_NO_SELECTED = '<未選択>'

    FILTERING: TextFieldsEmojiFiltering = TextFieldsEmojiFiltering()

@dataclass(frozen=True)
class TextFieldsDeletedEmojis(TextFieldsEmojis):
    DELETED_REASON = '削除要因'


@dataclass(frozen=True)
class TextFields:
    EMOJIS: TextFieldsEmojis = TextFieldsEmojis()
    DELETED_EMOJIS: TextFieldsDeletedEmojis = TextFieldsDeletedEmojis()


TEXT_FIELDS = TextFields()

