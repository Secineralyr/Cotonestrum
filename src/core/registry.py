from core.datatypes import EmojiData, UserData, RiskData, ReasonData

emojis: dict[str, EmojiData] = {}
users: dict[str, UserData] = {}
risks: dict[str, RiskData] = {}
reasons: dict[str, ReasonData] = {}

def put_emoji(eid, misskey_id, name, category, tags, url, is_self_made, license, owner_id, risk_id, created_at, updated_at):
    emojis[eid] = EmojiData(eid, misskey_id, name, category, tags, url, is_self_made, license, owner_id, risk_id, created_at, updated_at)

def get_emoji(eid):
    if eid in emojis:
        return emojis[eid]
    else:
        return None

def pop_emoji(eid):
    if eid in emojis:
        return emojis.pop(eid)
    else:
        return None

def put_user(uid, misskey_id, username):
    users[uid] = UserData(uid, misskey_id, username)

def get_user(uid):
    if uid in users:
        return users[uid]
    else:
        return None

def put_risk(rid, checked, level, reason_genre, remark, created_at, updated_at):
    risks[rid] = RiskData(rid, checked, level, reason_genre, remark, created_at, updated_at)

def get_risk(rid):
    if rid in risks:
        return risks[rid]
    else:
        return None

def put_reason(rsid, text, created_at, updated_at):
    reasons[rsid] = ReasonData(rsid, text, created_at, updated_at)

def pop_reason(rsid):
    if rsid in reasons:
        return reasons.pop(rsid)
    else:
        return None

def get_reason(rsid):
    if rsid in reasons:
        return reasons[rsid]
    else:
        return None