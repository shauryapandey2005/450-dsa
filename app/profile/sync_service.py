import json

from app.platforms.fetchers import (
    fetch_atcoder,
    fetch_coding_ninjas,
    fetch_gfg,
    fetch_github,
    fetch_hr_badges,
    fetch_lc_badges,
    fetch_leetcode,
    fetch_leetcode_rating_history,
)
from app.utils import ensure_utc_datetime, normalize_coding_ninjas_profile_id, utc_now


def build_sync_platforms_response(platform_status: dict):
    attempted = sum(1 for value in platform_status.values() if value.get("status") != "skipped")
    synced = sum(1 for value in platform_status.values() if value.get("status") == "synced")
    failed = sum(1 for value in platform_status.values() if value.get("status") == "failed")
    partial_success = bool(synced and failed)

    if attempted == 0:
        return {"success": False, "error": "No platforms provided to sync.", "platforms": platform_status}
    if synced == 0 and failed > 0:
        return {"success": False, "error": "Sync failed for all platforms.", "platforms": platform_status}

    return {"success": True, "partial_success": partial_success, "platforms": platform_status}


def sync_user_platforms(user, data, db_handle, cache_backend, now=None):
    now = now or utc_now()
    user_id = user.id

    last_sync = user.last_sync
    if last_sync:
        last_sync = ensure_utc_datetime(last_sync)
        diff = (now - last_sync).total_seconds()
        if diff < 600:
            remaining = int(600 - diff)
            mins = remaining // 60
            secs = remaining % 60
            return {
                "success": False,
                "error": f"Please wait {mins}m {secs}s before syncing again.",
            }, 200

    update_fields = {"last_sync": now}

    leetcode_username = user.leetcode_username or ""
    github_username = user.github_username or ""
    gfg_username = user.gfg_username or ""
    hackerrank_username = user.hackerrank_username or ""
    codingninjas_username = user.codingninjas_username or ""
    atcoder_username = user.atcoder_username or ""

    if "leetcode" in data:
        leetcode_username = data.get("leetcode", "").strip()
        update_fields["leetcode_username"] = leetcode_username
    if "github" in data:
        github_username = data.get("github", "").strip()
        update_fields["github_username"] = github_username
    if "gfg" in data:
        gfg_username = data.get("gfg", "").strip()
        update_fields["gfg_username"] = gfg_username
    if "hackerrank" in data:
        hackerrank_username = data.get("hackerrank", "").strip()
        update_fields["hackerrank_username"] = hackerrank_username
    if "codingninjas" in data:
        codingninjas_username = normalize_coding_ninjas_profile_id(data.get("codingninjas", ""))
        update_fields["codingninjas_username"] = codingninjas_username
    if "atcoder" in data:
        atcoder_username = data.get("atcoder", "").strip()
        update_fields["atcoder_username"] = atcoder_username

    combined_daily_counts = {}
    platform_totals = {}
    platform_status = {}

    def _mark(platform_key: str, status: str, error: str = None):
        payload = {"status": status}
        if error:
            payload["error"] = error
        platform_status[platform_key] = payload

    if leetcode_username:
        try:
            leetcode_data = fetch_leetcode(leetcode_username)
            if not leetcode_data:
                _mark("leetcode", "failed", "No data returned (username may be invalid or rate-limited).")
            else:
                _mark("leetcode", "synced")
                for key, value in leetcode_data.get("calendar", {}).items():
                    combined_daily_counts[key] = combined_daily_counts.get(key, 0) + value
                if leetcode_data.get("total") is not None:
                    platform_totals["LeetCode"] = leetcode_data.get("total")
                if leetcode_data.get("difficulty"):
                    platform_totals["LeetCode_Easy"] = leetcode_data["difficulty"].get("Easy", 0)
                    platform_totals["LeetCode_Medium"] = leetcode_data["difficulty"].get("Medium", 0)
                    platform_totals["LeetCode_Hard"] = leetcode_data["difficulty"].get("Hard", 0)
                if leetcode_data.get("contest"):
                    platform_totals["LeetCode_Contests"] = leetcode_data["contest"].get("attendedContestsCount", 0)
                    platform_totals["LeetCode_Rating"] = int(leetcode_data["contest"].get("rating", 0))
                    platform_totals["LeetCode_GlobalRank"] = leetcode_data["contest"].get("globalRanking", 0)

                try:
                    rating_history = fetch_leetcode_rating_history(leetcode_username)
                    if rating_history:
                        update_fields["rating_history"] = rating_history
                except Exception:
                    pass

                try:
                    lc_badges = fetch_lc_badges(leetcode_username)
                    update_fields["lc_badges_json"] = json.dumps(lc_badges)
                except Exception:
                    pass
        except Exception:
            _mark("leetcode", "failed", "Failed to fetch LeetCode stats.")
    else:
        _mark("leetcode", "skipped")

    if github_username:
        try:
            github_data = fetch_github(github_username)
            if not github_data:
                _mark("github", "failed", "No data returned (username may be invalid or rate-limited).")
            else:
                _mark("github", "synced")
                for key, value in github_data.get("calendar", {}).items():
                    combined_daily_counts[key] = combined_daily_counts.get(key, 0) + value
                if github_data.get("stats"):
                    platform_totals["GitHub_Issues"] = github_data["stats"]["issues"]
                    platform_totals["GitHub_PRs"] = github_data["stats"]["prs"]
                    platform_totals["GitHub_Merged_PRs"] = github_data["stats"]["merged_prs"]
                    platform_totals["GitHub_Commits"] = github_data["stats"]["commits"]
        except Exception:
            _mark("github", "failed", "Failed to fetch GitHub stats.")
    else:
        _mark("github", "skipped")

    if gfg_username:
        try:
            gfg_data = fetch_gfg(gfg_username)
            if not gfg_data:
                _mark("gfg", "failed", "No data returned (username may be invalid or rate-limited).")
            else:
                _mark("gfg", "synced")
                if gfg_data.get("total") is not None:
                    platform_totals["GFG"] = int(gfg_data.get("total", 0))
        except Exception:
            _mark("gfg", "failed", "Failed to fetch GFG stats.")
    else:
        _mark("gfg", "skipped")

    if codingninjas_username:
        try:
            codingninjas_data = fetch_coding_ninjas(codingninjas_username)
            if not codingninjas_data:
                _mark("codingninjas", "failed", "No data returned (username may be invalid or rate-limited).")
            else:
                _mark("codingninjas", "synced")
                if codingninjas_data.get("total") is not None:
                    platform_totals["Coding Ninjas"] = int(codingninjas_data.get("total", 0))
        except Exception:
            _mark("codingninjas", "failed", "Failed to fetch Coding Ninjas stats.")
    else:
        _mark("codingninjas", "skipped")

    if hackerrank_username:
        try:
            hr_badges, hr_solved = fetch_hr_badges(hackerrank_username)
            update_fields["hr_badges_json"] = json.dumps(hr_badges)
            if hr_solved > 0:
                platform_totals["HackerRank"] = hr_solved
            _mark("hackerrank", "synced")
        except Exception:
            _mark("hackerrank", "failed", "Failed to fetch HackerRank stats.")
    else:
        _mark("hackerrank", "skipped")

    if atcoder_username:
        try:
            atcoder_data = fetch_atcoder(atcoder_username)
            if not atcoder_data:
                _mark("atcoder", "failed", "No data returned (handle may be invalid or rate-limited).")
            else:
                _mark("atcoder", "synced")
                if atcoder_data.get("total") is not None:
                    platform_totals["AtCoder"] = int(atcoder_data.get("total", 0))
        except Exception:
            _mark("atcoder", "failed", "Failed to fetch AtCoder stats.")
    else:
        _mark("atcoder", "skipped")

    update_fields["external_daily_counts"] = combined_daily_counts
    update_fields["external_totals"] = platform_totals
    db_handle.user.update_one({"_id": user_id}, {"$set": update_fields})
    user.reload()

    cache_backend.clear()
    return build_sync_platforms_response(platform_status), 200
