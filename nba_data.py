#getting data from the nba api

import requests
import sqlite3
import os
import json
import plotly
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats, commonteamroster, teamplayerdashboard

def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_table(cur, conn):
    #cur.execute('DROP TABLE IF EXISTS NBA') #only if resetting the tables
    cur.execute('CREATE TABLE IF NOT EXISTS NBA (player_id INTEGER PRIMARY KEY, season_id TEXT, team TEXT, points FLOAT, rebounds FLOAT, assists FLOAT, three_percentage FLOAT, steals FLOAT, blocks FLOAT)')
    #cur.execute('DROP TABLE IF EXISTS players') #only if resetting the tables
    cur.execute('CREATE TABLE IF NOT EXISTS players (player_id INTEGER, name TEXT, team_id INTEGER)')
    conn.commit()

def player_ids_for_team(id):
    base_team_id = 1610612737
    id = base_team_id + id
    print(id)
    roster = commonteamroster.CommonTeamRoster(team_id=id).get_dict()
    player_ids = []
    names = []
    for player in roster['resultSets'][0]['rowSet']:
        if (player[-3] != 'R' and int(player[11]) >= 4):
            player_ids.append(player[-1])
            names.append(player[3])

    for i in range(len(player_ids)):
        cur.execute('INSERT INTO players (player_id, name, team_id) VALUES (?,?,?)', (player_ids[i], names[i], id))
    conn.commit()

def insert_stats(cur, conn, team_id):
    stat_names = ["PLAYER_ID", "SEASON_ID", "LEAGUE_ID", "TEAM_ID", "TEAM", "PLAYER_AGE", "GP", "GS", "MIN", "FGM",
    "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]
    index = {stat_names[i]: i for i in range(len(stat_names))}
    
    players = cur.execute('SELECT player_id, name FROM players WHERE team_id = (?)', (team_id,)).fetchall()
    for player_id in players:
        stats = playercareerstats.PlayerCareerStats(player_id=player_id, per_mode36='PerGame').get_dict()
        for season in stats['resultSets'][0]['rowSet']:
            cur.execute('INSERT INTO NBA (player_id, season_id, team, points, rebounds, assists, three_percentage, steals, blocks) \
                VALUES (?,?,?,?,?,?,?,?,?)', (season[index['PLAYER_ID']], season[index['SEASON_ID']], season[index['TEAM']], season[index['PTS']], \
                    season[index['REB']], season[index['AST']], season[index['FG3_PCT']], season[index['STL']], season[index['BLK']],))
        conn.commit()


def update_database(cur, conn):

    team_id = 1610612737
    newteam = False
    
    while not newteam and team_id != 1610612767:
        teamcheck = cur.execute('SELECT team_id FROM players WHERE team_id = (?)', (team_id,))
        if (not len(teamcheck.fetchall())):
            newteam = True
        else:
            team_id += 1

    insert_players(cur, conn, team_id)
    insert_stats(cur, conn, team_id)
        
    conn.commit()
        

if __name__ == '__main__':
    cur, conn = set_up_database('stats.db')
    set_up_table(cur, conn)
    for i in range(2):
        update_database(cur, conn)
    

    