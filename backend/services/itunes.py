"""iTunes Search API client and response-normalization helpers."""

import json
from urllib.parse import quote
from urllib.request import urlopen


def fetch_itunes(term, entity='musicTrack', media=None, limit=10):
    search_term = (term or 'culture').strip() or 'culture'
    encoded_term = quote(search_term)
    url = f'https://itunes.apple.com/search?term={encoded_term}&entity={entity}&limit={limit}'
    if media:
        url = f'https://itunes.apple.com/search?term={encoded_term}&media={quote(media)}&entity={entity}&limit={limit}'
    try:
        with urlopen(url, timeout=15) as response:
            return json.loads(response.read().decode('utf-8')).get('results', [])
    except Exception:
        return []


def normalize_itunes_track(item):
    artwork = (item.get('artworkUrl600') or item.get('artworkUrl100') or '').replace('100x100', '600x600')
    duration_ms = item.get('trackTimeMillis')
    if duration_ms:
        minutes, seconds = divmod(int(duration_ms / 1000), 60)
        duration = f'{minutes}:{seconds:02d}'
    else:
        duration = item.get('trackTime') or 'N/A'
    return {
        'id': item.get('trackId') or item.get('collectionId') or item.get('trackName'),
        'title': item.get('trackName') or item.get('collectionName') or 'Untitled',
        'artist': item.get('artistName') or 'Unknown artist',
        'genre': item.get('primaryGenreName') or item.get('genre') or 'Music',
        'artwork': artwork,
        'audioUrl': item.get('previewUrl') or item.get('feedUrl') or '',
        'description': item.get('longDescription') or item.get('description') or 'Fresh listening from the PodClub network.',
        'duration': duration,
        'kind': 'music',
        'source': 'itunes',
    }


def normalize_itunes_podcast(item):
    artwork = (item.get('artworkUrl600') or item.get('artworkUrl100') or '').replace('100x100', '600x600')
    return {
        'id': item.get('collectionId') or item.get('trackId') or item.get('collectionName'),
        'title': item.get('collectionName') or item.get('trackName') or 'Untitled podcast',
        'artist': item.get('artistName') or 'Unknown host',
        'genre': item.get('primaryGenreName') or item.get('genre') or 'Culture',
        'artwork': artwork,
        'audioUrl': item.get('feedUrl') or item.get('previewUrl') or '',
        'description': item.get('description') or item.get('longDescription') or 'A conversation worth hearing.',
        'duration': str(item.get('trackTimeMillis') or 'N/A'),
        'kind': 'podcast',
        'source': 'itunes',
    }
