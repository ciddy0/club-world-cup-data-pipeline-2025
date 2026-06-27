from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_to_supabase(results, match_id, match_info):
    # Insert match metadata
    supabase.table("matches").upsert({
        "id": match_id,
        "date": match_info["date"],
        "home_team": match_info["home_team"],
        "away_team": match_info["away_team"],
        "home_team_id": match_info["home_team_id"],
        "away_team_id": match_info["away_team_id"]
    }, on_conflict=["id"]).execute()

    # Upsert teams (to avoid duplicates) (DENORMORALIZE THIS SHIT)
    for team in results["team_stats"]:
        supabase.table("teams").upsert({
            "team_id": team["teamId"],
            "team_name": team["teamName"],
            "abbreviation": team.get("abbreviation"),
            "logo": team.get("logo")
        }, on_conflict=["team_id"]).execute()

    # Insert team stats linked to team_id and match_id
    for team in results["team_stats"]:
        stats = team["stats"]
        supabase.table("team_stats").insert({
            "match_id": match_id,
            "team_id": team["teamId"],
            "fouls": safe_int(stats.get("foulsCommitted", 0)),
            "yellow_cards": safe_int(stats.get("yellowCards", 0)),
            "red_cards": safe_int(stats.get("redCards", 0)),
            "offsides": safe_int(stats.get("offsides", 0)),
            "corners": safe_int(stats.get("wonCorners", 0)),
            "saves": safe_int(stats.get("saves", 0)),
            "possession_pct": safe_float(stats.get("possessionPct", 0)),
            "total_shots": safe_int(stats.get("totalShots", 0)),
            "shots_on_target": safe_int(stats.get("shotsOnTarget", 0)),
            "shot_pct": safe_float(stats.get("shotPct", 0)),
            "penalty_goals": safe_int(stats.get("penaltyKickGoals", 0)),
            "penalty_shots": safe_int(stats.get("penaltyKickShots", 0)),
            "accurate_passes": safe_int(stats.get("accuratePasses", 0)),
            "total_passes": safe_int(stats.get("totalPasses", 0)),
            "pass_pct": safe_float(stats.get("passPct", 0)),
            "accurate_crosses": safe_int(stats.get("accurateCrosses", 0)),
            "total_crosses": safe_int(stats.get("totalCrosses", 0)),
            "cross_pct": safe_float(stats.get("crossPct", 0)),
            "total_long_balls": safe_int(stats.get("totalLongBalls", 0)),
            "accurate_long_balls": safe_int(stats.get("accurateLongBalls", 0)),
            "longball_pct": safe_float(stats.get("longballPct", 0)),
            "blocked_shots": safe_int(stats.get("blockedShots", 0)),
            "effective_tackles": safe_int(stats.get("effectiveTackles", 0)),
            "total_tackles": safe_int(stats.get("totalTackles", 0)),
            "tackle_pct": safe_float(stats.get("tacklePct", 0)),
            "interceptions": safe_int(stats.get("interceptions", 0)),
            "effective_clearance": safe_int(stats.get("effectiveClearance", 0)),
            "total_clearance": safe_int(stats.get("totalClearance", 0)),
            "stats": stats
        }).execute()

    # Insert player data
    for player in results["rosters"]:
        # Upsert player info
        supabase.table("players").upsert({
            "player_id": player["playerId"],
            "full_name": player["fullName"],
            "team_id": player["teamId"],
            "team_name": player["team"],
            "position": player.get("position"),
            "position_abbr": player.get("position_abbr"),
            "jersey": player["jersey"],
            "headshot": player.get("headshot")
        }, on_conflict=["player_id"]).execute()

        # Insert player stats
        stats = player["stats"]
        supabase.table("player_stats").insert({
            "match_id": match_id,
            "player_id": player["playerId"],
            "starter": player["starter"],
            "active": player["active"],
            "subbed_in": player["subbedIn"],
            "subbed_out": player["subbedOut"],
            "goals": safe_int(stats.get("totalGoals", 0)),
            "assists": safe_int(stats.get("goalAssists", 0)),
            "shots": safe_int(stats.get("totalShots", 0)),
            "shots_on_target": safe_int(stats.get("shotsOnTarget", 0)),
            "yellow_cards": safe_int(stats.get("yellowCards", 0)),
            "red_cards": safe_int(stats.get("redCards", 0)),
            "fouls_committed": safe_int(stats.get("foulsCommitted", 0)),
            "fouls_suffered": safe_int(stats.get("foulsSuffered", 0)),
            "offsides": safe_int(stats.get("offsides", 0)),
            "stats": player["stats"]
        }).execute()
        
def safe_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0