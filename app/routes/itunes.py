"""iTunes Search API proxy — powers music & podcast discovery."""
import requests
from flask import Blueprint, request, jsonify, current_app
from ..exceptions import ValidationError

itunes_bp = Blueprint("itunes", __name__, url_prefix="/api/itunes")

ITUNES_SEARCH_URL = "https://itunes.apple.com/search"
ALLOWED_MEDIA = ("music", "podcast", "musicVideo", "ebook")


@itunes_bp.get("/search")
def search():
    """Proxy a search to the iTunes Search API."""
    term = (request.args.get("term") or "").strip()
    media = (request.args.get("media") or "podcast").strip()
    limit = min(request.args.get("limit", 20, type=int) or 20, 50)
    country = (request.args.get("country") or "US").strip()

    if not term:
        raise ValidationError("term query parameter is required")
    if media not in ALLOWED_MEDIA:
        media = "podcast"

    params = {
        "term": term,
        "media": media,
        "entity": "podcast" if media == "podcast" else "song",
        "limit": limit,
        "country": country,
    }

    try:
        resp = requests.get(ITUNES_SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        current_app.logger.warning("iTunes search failed: %s", exc)
        return jsonify({"resultCount": 0, "results": []}), 200

    return jsonify(resp.json()), 200
