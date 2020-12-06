#getting data from the nba api

import requests
import sqlite3
import os
import json
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats, commonteamroster, teamplayerdashboard


def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_table(cur, conn):
    
    cur.execute('DROP TABLE IF EXISTS NBA')
    cur.execute('CREATE TABLE NBA (player_id INTEGER PRIMARY KEY, name TEXT, teams TEXT, points TEXT, rebounds TEXT, assists TEXT, three_percentages TEXT, steals TEXT, blocks TEXT)')
    conn.commit()

def player_ids_for_team(id):

    base_team_id = 1610612737
    id = base_team_id + id
    print(id)
    roster = commonteamroster.CommonTeamRoster(team_id=id).get_dict()
    
    ids_and_names = []
    for player in roster['resultSets'][0]['rowSet']:
        if (player[-3] != 'R' and int(player[11]) >= 4):
            ids_and_names.append((player[-1], player[3]))

    return ids_and_names

def insert_player_stats(cur, conn):

    stat_names = ["PLAYER_ID", "SEASON_ID", "LEAGUE_ID", "TEAM_ID", "TEAM_ABBREVIATION", "PLAYER_AGE", "GP", "GS", "MIN", "FGM",
    "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]
    stat_index = {stat_names[i]: i for i in range(len(stat_names))}

    for i in range(15): 
        team_id = i
        players = player_ids_for_team(team_id)
        for player in players:
            id = player[0]
            name = player[1]
            stats = playercareerstats.PlayerCareerStats(player_id=id, per_mode36='PerGame').get_dict()
            teams, points, rebounds, assists, three_percentages, steals, blocks = ([] for i in range(7))
            for season in stats['resultSets'][0]['rowSet']:
                teams.append(season[stat_index['TEAM_ABBREVIATION']])
                points.append(season[stat_index['PTS']])
                rebounds.append(season[stat_index['REB']])
                assists.append(season[stat_index['AST']])
                three_percentages.append(season[stat_index['FG3_PCT']])
                steals.append(season[stat_index['STL']])
                blocks.append(season[stat_index['BLK']])

            teams = ','.join(teams)
            points = ','.join(map(str, points))
            rebounds = ','.join(map(str, rebounds))
            assists = ','.join(map(str, assists))
            three_percentages = ','.join(map(str, three_percentages))
            steals = ','.join(map(str, steals))
            blocks = ','.join(map(str, blocks))

            cur.execute('INSERT INTO NBA (player_id, name, teams, points, rebounds, assists, three_percentages, steals, blocks) VALUES (?,?,?,?,?,?,?,?,?)', \
                (id, name, teams, points, rebounds, assists, three_percentages, steals, blocks,))
        
        conn.commit()

        

if __name__ == '__main__':
    #cur, conn = set_up_database('basketball.db')
    #set_up_table(cur, conn)
    #insert_player_stats(cur, conn)

    print(player_ids_for_team(0))