from core.datatypes import EmojiData, UserData, RiskData, ReasonData

emojis: dict[str, EmojiData] = {}
users: dict[str, UserData] = {}
risks: dict[str, RiskData] = {}
reasons: dict[str, ReasonData] = {}

def get_username(uid):
    if uid in users:
        return users[uid].username
    else:
        return None