"""Small two-phase switch. Supabase reads remain available during write freeze."""
import json
import urllib.request
import urllib.error
import urllib.parse
from share_store import ShareStore, ShareUnavailable, ShareNotFound, ShareInvalid, canonical


class ShareWritesPaused(ShareUnavailable):
    pass


def flag(value):
    if isinstance(value, bool):
        return value
    value = str(value).strip().lower()
    if value in {'true', '1', 'yes'}:
        return True
    if value in {'false', '0', 'no'}:
        return False
    raise ShareUnavailable('Invalid write-pause configuration')


class SupabaseReadStore:
    """Temporary read-only legacy adapter; no POST or credential exposure."""
    def __init__(self, url, key, opener=urllib.request.urlopen):
        self.url, self.key, self.opener = url.rstrip('/'), key, opener

    def load(self, code):
        import re
        if not re.fullmatch(r'[A-Z0-9]{6,10}', code):
            raise ShareInvalid('Invalid share code')
        if not self.url or not self.key:
            raise ShareUnavailable('Legacy share store not configured')
        request = urllib.request.Request(
            self.url + '/rest/v1/share_links?code=eq.' + urllib.parse.quote(code) + '&select=payload',
            headers={'apikey': self.key, 'Authorization': 'Bearer ' + self.key}, method='GET')
        try:
            with self.opener(request, timeout=12) as response:
                rows = json.loads(response.read().decode('utf-8'))
        except Exception:
            raise ShareUnavailable('Legacy share lookup failed') from None
        if rows == []:
            raise ShareNotFound('Share link not found')
        if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
            raise ShareInvalid('Invalid legacy share response')
        payload = rows[0].get('payload')
        canonical(payload)
        return payload

    def save(self, payload):
        raise ShareWritesPaused('Legacy writes disabled during migration')


class RoutedStore:
    def __init__(self, backend, paused, neon, supabase):
        self.backend = str(backend).strip().lower()
        if self.backend not in {'supabase', 'neon'}:
            raise ShareUnavailable('Invalid share backend')
        self.paused = flag(paused)
        self.store = {'neon': neon, 'supabase': supabase}[self.backend]

    def load(self, code):
        return self.store.load(code)

    def save(self, payload):
        if self.paused:
            raise ShareWritesPaused('Short link writes temporarily paused')
        return self.store.save(payload)


def configured_store(settings):
    # Safe phase-1 defaults; final cutover explicitly sets neon + false.
    return RoutedStore(settings.get('SHARE_BACKEND', 'supabase'),
                       settings.get('SHARE_WRITES_PAUSED', True),
                       ShareStore(settings.get('NEON_DATABASE_URL', '')),
                       SupabaseReadStore(settings.get('SUPABASE_URL', ''), settings.get('SUPABASE_KEY', '')))
