#getting data from the nba api

import requests
import json
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats
from nba_api.stats.static import players

def testing():
    
    stat_names = ["PLAYER_ID", "SEASON_ID", "LEAGUE_ID", "TEAM_ID", "TEAM_ABBREVIATION", "PLAYER_AGE", "GP", "GS", "MIN", "FGM",
    "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]

    stat_index = {stat_names[i]: i for i in range(len(stat_names))}

    print('hi')
    hi = commonplayerinfo.CommonPlayerInfo(player_id=2544)
    data = hi.available_seasons.get_dict()

    hi = playercareerstats.PlayerCareerStats(player_id=2544, per_mode36='PerGame')
    data = hi.get_json()
    data = json.loads(data)
    
    for season in data['resultSets'][0]['rowSet']:
        print(season[stat_index['SEASON_ID']])



if __name__ == '__main__':
    testing()