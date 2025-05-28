import re


GAME_NAME_BY_APPID = {
    '753': 'Steam',
    '570': 'Dota 2',
    '730': 'Counter-Strike 2',
    '440': 'Team Fortress 2',
    '578080': 'PUBG: BATTLEGROUNDS',
    '252490': 'Rust',
}


def parse_price_value(value: str) -> float | None:
    value = re.sub(r"[^\d.,]", "", value)
    if not value:
        return None
    last_sep = max(value.rfind('.'), value.rfind(','))
    if last_sep == -1:
        return float(value)
    integer_part = value[:last_sep].replace(',', '').replace('.', '')
    fractional_part = value[last_sep + 1:]
    try:
        return float(f"{integer_part}.{fractional_part}" if integer_part else f"0.{fractional_part}")
    except ValueError:
        return None
