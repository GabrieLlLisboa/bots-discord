import json
import os

_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "nicks.json")


def _ensure_file():
    os.makedirs(os.path.dirname(_FILE), exist_ok=True)
    if not os.path.exists(_FILE):
        with open(_FILE, "w") as f:
            json.dump({}, f)


def _load() -> dict[int, str]:
    _ensure_file()
    with open(_FILE, "r") as f:
        raw = json.load(f)
    # Chaves são salvas como string no JSON, converte de volta para int
    return {int(k): v for k, v in raw.items()}


def _save(data: dict[int, str]):
    _ensure_file()
    with open(_FILE, "w") as f:
        json.dump({str(k): v for k, v in data.items()}, f, indent=2, ensure_ascii=False)


def get(member_id: int) -> str | None:
    return _load().get(member_id)


def set(member_id: int, nick: str):
    data = _load()
    data[member_id] = nick
    _save(data)


def delete(member_id: int):
    data = _load()
    data.pop(member_id, None)
    _save(data)
