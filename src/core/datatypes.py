
class EmojiData():
    def __init__(self, eid, misskey_id, name, category, tags, url, is_self_made, license, owner_id, risk_id, created_at, updated_at):
        self.id = eid

        self.misskey_id = misskey_id
        self.name = name
        self.category = category
        self.tags = tags
        self.url = url
        self.is_self_made = is_self_made
        self.license = license

        self.owner_id = owner_id
        self.risk_id = risk_id

        self.created_at = created_at
        self.updated_at = updated_at

class DeletedEmojiData():
    def __init__(self, eid, misskey_id, name, category, tags, url, is_self_made, license, owner_id, risk_id, info, deleted_at):
        self.id = eid

        self.misskey_id = misskey_id
        self.name = name
        self.category = category
        self.tags = tags
        self.url = url
        self.is_self_made = is_self_made
        self.license = license

        self.owner_id = owner_id
        self.risk_id = risk_id

        self.info = info

        self.deleted_at = deleted_at

class UserData():
    def __init__(self, uid, misskey_id, username):
        self.id = uid

        self.misskey_id = misskey_id
        self.username = username

class RiskData():
    def __init__(self, rid, checked, level, reason_genre, remark, created_at, updated_at):
        self.id = rid

        self.checked = checked
        self.level = level
        self.reason_genre = reason_genre
        self.remark = remark

        self.created_at = created_at
        self.updated_at = updated_at

class ReasonData():
    def __init__(self, rsid, text, created_at, updated_at):
        self.id = rsid

        self.text = text

        self.created_at = created_at
        self.updated_at = updated_at
