
from core import registry

class SelectionIsSelfMade():
    def __init__(self, no: bool, yes: bool):
        self.no = no
        self.yes = yes

    def _filter(self, target: bool) -> bool:
        if target:
            return self.yes
        else:
            return self.no

class SelectionRiskLevel():
    def __init__(self, notset: bool, low: bool, medium: bool, high: bool, danger: bool):
        self.notset = notset
        self.low = low
        self.medium = medium
        self.high = high
        self.danger = danger

    def _filter(self, target: int) -> bool:
        match target:
            case 0:
                return self.low
            case 1:
                return self.medium
            case 2:
                return self.high
            case 3:
                return self.danger
            case None:
                return self.notset
            case _:
                return False

class SelectionReasonGenre():
    def __init__(self, mapping: dict[str | None, bool]):
        self.mapping = mapping

    def _filter(self, target: str | None) -> bool:
        target0 = target if target not in ['', None] else None

        if target0 not in self.mapping:
            return False

        return self.mapping[target0]

class SelectionCheckStatus():
    def __init__(self, need_check: bool, checked: bool, need_recheck: bool):
        self.need_check = need_check
        self.checked = checked
        self.need_recheck = need_recheck

    def _filter(self, target: int) -> bool:
        match target:
            case 0:
                return self.need_check
            case 1:
                return self.checked
            case 2:
                return self.need_recheck
            case _:
                return False

class EmojiFilter():

    @classmethod
    def no_filter(cls):
        return cls(
            False,
            False, False, False, False, False, False, False, False, False, False,
            '', '', '', SelectionIsSelfMade(False, False), '', '', SelectionRiskLevel(False, False, False, False, False), SelectionReasonGenre({}), '', SelectionCheckStatus(False, False, False),
            False, False, False, False, False
        )

    def __init__(
        self,
        enabled: bool,
        enabled_name: bool,
        enabled_category: bool,
        enabled_tags: bool,
        enabled_is_self_made: bool,
        enabled_licence: bool,
        enabled_username: bool,
        enabled_risk_level: bool,
        enabled_reason_genre: bool,
        enabled_remark: bool,
        enabled_status: bool,
        name: str,
        category: str,
        tags: str,
        is_self_made: SelectionIsSelfMade,
        licence: str,
        username: str,
        risk_level: SelectionRiskLevel,
        reason_genre: SelectionReasonGenre,
        remark: str,
        status: SelectionCheckStatus,
        empty_category: bool,
        empty_tags: bool,
        empty_licence: bool,
        empty_username: bool,
        empty_remark: bool,
    ):
        self.name = name
        self.category = category if not empty_category else None
        self.tags = tags if not empty_tags else None
        self.is_self_made = is_self_made
        self.licence = licence if not empty_licence else None
        self.username = username if not empty_username else None
        self.risk_level = risk_level
        self.reason_genre = reason_genre
        self.remark = remark if not empty_remark else None
        self.status = status

        self.enabled = enabled

        self.enabled_name = enabled_name
        self.enabled_category = enabled_category
        self.enabled_tags = enabled_tags
        self.enabled_is_self_made = enabled_is_self_made
        self.enabled_licence = enabled_licence
        self.enabled_username = enabled_username
        self.enabled_risk_level = enabled_risk_level
        self.enabled_reason_genre = enabled_reason_genre
        self.enabled_remark = enabled_remark
        self.enabled_status = enabled_status

        self.empty_category = empty_category
        self.empty_tags = empty_tags
        self.empty_licence = empty_licence
        self.empty_username = empty_username
        self.empty_remark = empty_remark

    def filter_all(self, emojis: list[str]) -> list[str]:
        return [eid for eid in emojis if self.filter(eid)]

    def filter(self, eid: str) -> bool:
        emoji = registry.get_emoji(eid)
        if emoji is None:
            return False

        name = emoji.name
        category = emoji.category
        tags = ' '.join(emoji.tags)
        is_self_made = emoji.is_self_made
        licence = emoji.license

        uid = emoji.owner_id
        user = registry.get_user(uid)
        if user is not None:
            username = user.username
        else:
            username = ''

        rid = emoji.risk_id
        risk = registry.get_risk(rid)
        if risk is not None:
            risk_level = risk.level
            remark = risk.remark
            status = risk.checked

            rsid = risk.reason_genre
        else:
            risk_level = None
            remark = None
            status = 0
            rsid = None

        return (
            (not (self.enabled and self.enabled_name) or self._filter_name(name))
            and (not (self.enabled and self.enabled_category) or self._filter_category(category))
            and (not (self.enabled and self.enabled_tags) or self._filter_tags(tags))
            and (not (self.enabled and self.enabled_is_self_made) or self._filter_is_self_made(is_self_made))
            and (not (self.enabled and self.enabled_licence) or self._filter_licence(licence))
            and (not (self.enabled and self.enabled_username) or self._filter_username(username))
            and (not (self.enabled and self.enabled_risk_level) or self._filter_risk_level(risk_level))
            and (not (self.enabled and self.enabled_remark) or self._filter_remark(remark))
            and (not (self.enabled and self.enabled_status) or self._filter_status(status))
            and (not (self.enabled and self.enabled_reason_genre) or self._filter_reason_genre(rsid))
        )

    def _filter_str(self, target: str | None, filtering: str | None) -> bool:
        if filtering is not None:
            if filtering == '':
                return True

            if target is None:
                return False

            return all([i in target for i in filtering.split()])
        else:
            return target in ['', None]

    def _filter_name(self, name: str | None) -> bool:
        return self._filter_str(name, self.name)

    def _filter_category(self, category: str | None) -> bool:
        return self._filter_str(category, self.category)

    def _filter_tags(self, tags: str | None) -> bool:
        return self._filter_str(tags, self.tags)

    def _filter_licence(self, licence: str | None) -> bool:
        return self._filter_str(licence, self.licence)

    def _filter_username(self, username: str | None) -> bool:
        return self._filter_str(username, self.username)

    def _filter_remark(self, remark: str | None) -> bool:
        return self._filter_str(remark, self.remark)

    def _filter_is_self_made(self, is_self_made: bool) -> bool:
        return self.is_self_made._filter(is_self_made)

    def _filter_risk_level(self, risk_level: int | None) -> bool:
        return self.risk_level._filter(risk_level)

    def _filter_reason_genre(self, reason_genre: str | None) -> bool:
        return self.reason_genre._filter(reason_genre)

    def _filter_status(self, status: bool) -> bool:
        return self.status._filter(status)

    def get_filter_status(self):
        return (
            self.enabled
            and (
                self.enabled_name
                or self.enabled_category
                or self.enabled_tags
                or self.enabled_is_self_made
                or self.enabled_licence
                or self.enabled_username
                or self.enabled_risk_level
                or self.enabled_reason_genre
                or self.enabled_remark
                or self.enabled_status
            )
        )

class DeletedEmojiFilter(EmojiFilter):
    @classmethod
    def no_filter(cls):
        return cls(
            False,
            False, False, False, False, False, False, False, False, False, False,
            '', '', '', SelectionIsSelfMade(False, False), '', '', SelectionRiskLevel(False, False, False, False, False), SelectionReasonGenre({}), '', SelectionCheckStatus(False, False, False),
            False, False, False, False, False
        )

    def __init__(
        self,
        enabled: bool,
        enabled_name: bool,
        enabled_category: bool,
        enabled_tags: bool,
        enabled_is_self_made: bool,
        enabled_licence: bool,
        enabled_username: bool,
        enabled_risk_level: bool,
        enabled_reason_genre: bool,
        enabled_remark: bool,
        enabled_status: bool,
        name: str,
        category: str,
        tags: str,
        is_self_made: SelectionIsSelfMade,
        licence: str,
        username: str,
        risk_level: SelectionRiskLevel,
        reason_genre: SelectionReasonGenre,
        remark: str,
        status: SelectionCheckStatus,
        empty_category: bool,
        empty_tags: bool,
        empty_licence: bool,
        empty_username: bool,
        empty_remark: bool,
    ):
        super().__init__(enabled, enabled_name, enabled_category, enabled_tags, enabled_is_self_made, enabled_licence, enabled_username, enabled_risk_level, enabled_reason_genre, enabled_remark, enabled_status, name, category, tags, is_self_made, licence, username, risk_level, reason_genre, remark, status, empty_category, empty_tags, empty_licence, empty_username, empty_remark)

    def filter(self, eid: str) -> bool:
        emoji = registry.get_deleted_emoji(eid)
        if emoji is None:
            return False

        name = emoji.name
        category = emoji.category
        tags = ' '.join(emoji.tags)
        is_self_made = emoji.is_self_made
        licence = emoji.license

        uid = emoji.owner_id
        user = registry.get_user(uid)
        if user is not None:
            username = user.username
        else:
            username = ''

        rid = emoji.risk_id
        risk = registry.get_risk(rid)
        if risk is not None:
            risk_level = risk.level
            remark = risk.remark
            status = risk.checked

            rsid = risk.reason_genre
        else:
            risk_level = None
            remark = None
            status = 0
            rsid = None

        return (
            (not (self.enabled and self.enabled_name) or self._filter_name(name))
            and (not (self.enabled and self.enabled_category) or self._filter_category(category))
            and (not (self.enabled and self.enabled_tags) or self._filter_tags(tags))
            and (not (self.enabled and self.enabled_is_self_made) or self._filter_is_self_made(is_self_made))
            and (not (self.enabled and self.enabled_licence) or self._filter_licence(licence))
            and (not (self.enabled and self.enabled_username) or self._filter_username(username))
            and (not (self.enabled and self.enabled_risk_level) or self._filter_risk_level(risk_level))
            and (not (self.enabled and self.enabled_remark) or self._filter_remark(remark))
            and (not (self.enabled and self.enabled_status) or self._filter_status(status))
            and (not (self.enabled and self.enabled_reason_genre) or self._filter_reason_genre(rsid))
        )
