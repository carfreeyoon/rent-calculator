"""Server-side immutable share links. No database URLs or payloads are logged."""
import base64
import json
import re
import secrets
import string
import time


class ShareError(Exception):
    pass


class ShareUnavailable(ShareError):
    pass


class ShareNotFound(ShareError):
    pass


class ShareInvalid(ShareError):
    pass


def canonical(payload):
    if not isinstance(payload, dict) or not payload:
        raise ShareInvalid("Invalid quote payload")
    try:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError):
        raise ShareInvalid("Invalid quote JSON") from None


def connect_database(url):
    if not url:
        raise ShareUnavailable("Share database is not configured")
    import psycopg
    import certifi
    # Explicit CA + hostname verification; fresh connection wakes idle compute.
    return psycopg.connect(url, connect_timeout=12, sslmode="verify-full",
                           sslrootcert=certifi.where(), autocommit=False)


def transient(exc):
    state = getattr(exc, "sqlstate", "") or ""
    return state.startswith("08") or state in {"40001", "40P01", "57P01", "57P02", "57P03", "53300"} or (
        not state and exc.__class__.__name__ in {"OperationalError", "InterfaceError", "TimeoutError"})


class ShareStore:
    def __init__(self, url, connect=connect_database, sleep=time.sleep, code_factory=None):
        self.url, self.connect, self.sleep = url, connect, sleep
        self.code_factory = code_factory or (lambda: "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)))

    def _run(self, operation):
        for attempt in range(3):
            try:
                # No cached socket survives sleep; context commits/closes every operation.
                with self.connect(self.url) as conn:
                    conn.execute("SET LOCAL statement_timeout = '10000ms'")
                    return operation(conn)
            except ShareError:
                raise
            except Exception as exc:
                if transient(exc) and attempt < 2:
                    self.sleep(0.5 * 2 ** attempt)
                    continue
                raise ShareUnavailable("Share database operation failed") from None

    def load(self, code):
        if not re.fullmatch(r"[A-Z0-9]{6,10}", code):
            raise ShareInvalid("Invalid share code")
        row = self._run(lambda c: c.execute("SELECT payload FROM public.share_links WHERE code = %s", (code,)).fetchone())
        if row is None:
            raise ShareNotFound("Share link not found")
        canonical(row[0])
        return row[0]

    def save(self, payload):
        encoded = canonical(payload)
        for _ in range(5):
            code = self.code_factory()
            if not re.fullmatch(r"[A-Z0-9]{6,10}", code):
                raise ShareInvalid("Invalid generated code")
            def insert(conn):
                row = conn.execute(
                    "INSERT INTO public.share_links (code, payload) VALUES (%s, %s::jsonb) "
                    "ON CONFLICT (code) DO NOTHING RETURNING code", (code, encoded)).fetchone()
                if row:
                    return True
                # Resolves ambiguous commit retries without overwriting any existing quote.
                existing = conn.execute("SELECT payload FROM public.share_links WHERE code = %s", (code,)).fetchone()
                return existing is not None and canonical(existing[0]) == encoded
            if self._run(insert):
                return code
        raise ShareUnavailable("Share code collisions exhausted")


def decode_share(value, store):
    value = str(value or "").strip()
    if re.fullmatch(r"[A-Z0-9]{6,10}", value):
        return store.load(value)
    try:
        payload = json.loads(base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True).decode("utf-8"))
        canonical(payload)
        return payload
    except (ValueError, TypeError, UnicodeError):
        raise ShareInvalid("Invalid shared quote") from None
