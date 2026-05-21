from flask import Blueprint, jsonify, render_template, request

from app.utils import search_dsa_questions


search_bp = Blueprint("search", __name__)


@search_bp.route("/search")
def search():
    initial_query = request.args.get("q", "").strip()
    return render_template("search.html", initial_query=initial_query)


@search_bp.route("/api/search_questions")
def api_search_questions():
    raw_query = request.args.get("q", "")
    try:
        limit = min(max(int(request.args.get("limit", 40)), 1), 80)
    except ValueError:
        limit = 40

    payload = search_dsa_questions(raw_query, limit=limit)
    return jsonify(payload)
