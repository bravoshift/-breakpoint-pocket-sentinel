"""Local HMAC-protected demo history. Not protection from same-user compromise."""
import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path

LOCKOUT_THRESHOLD = 3  # Shared persistent-history lockout threshold

BASE = Path(__file__).resolve().parent
HISTORY = BASE / "behavior_history.json"
TAG = BASE / "behavior_history.hmac"
KEY = BASE / ".breakpoint_state/history.key"

class HistoryIntegrityError(RuntimeError):
    pass

def _key():
    if KEY.exists():
        key = KEY.read_bytes()
        if len(key) != 32:
            raise HistoryIntegrityError("Invalid local history key; access denied")
        return key
    if HISTORY.exists() or TAG.exists():
        raise HistoryIntegrityError("History exists without a key; access denied. Back up records before resetting.")
    KEY.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(KEY, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return _key()
    with os.fdopen(fd, "wb") as f:
        f.write(secrets.token_bytes(32))
    return KEY.read_bytes()

def load_history():
    first_run = not KEY.exists() and not HISTORY.exists() and not TAG.exists()
    key = _key()
    if not HISTORY.exists() and not TAG.exists():
        if first_run:
            save_history({})
            return {}
        raise HistoryIntegrityError("Authenticated history missing; access denied")
    if not HISTORY.exists() or not TAG.exists():
        raise HistoryIntegrityError("History or authentication tag missing; access denied")
    data = HISTORY.read_bytes()
    expected = hmac.new(key, data, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, TAG.read_text().strip()):
        raise HistoryIntegrityError("History authentication failed; access denied")
    try:
        history = json.loads(data)
        if not isinstance(history, dict) or any(
            not isinstance(k, str) or type(v) is not int or v < 0
            for k, v in history.items()
        ):
            raise ValueError("Invalid history structure")
        return history
    except (ValueError, UnicodeError) as exc:
        raise HistoryIntegrityError("Invalid history data; access denied") from exc

def save_history(history):
    key = _key()
    data = (json.dumps(history, indent=2, sort_keys=True) + "
").encode()
    tag = hmac.new(key, data, hashlib.sha256).hexdigest() + "
"
    for target, content in ((HISTORY, data), (TAG, tag.encode())):
        temporary = target.with_suffix(target.suffix + ".tmp")
        with open(temporary, "wb") as f:
            f.write(content)
        os.replace(temporary, target)

def verify_history():
    if not HISTORY.exists() and not TAG.exists() and not KEY.exists():
        return "NOT FOUND"
    try:
        load_history()
        return "VERIFIED" if HISTORY.exists() else "NOT FOUND"
    except HistoryIntegrityError:
        return "ALERT"
