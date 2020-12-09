#getting data from the nba api

import requests
import sqlite3
import os
import json
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats, commonteamroster, teamplayerdashboard
from sportsreference.ncaab.roster import Player
from sportsreference.ncaab.teams import Teams
from sportsreference.ncaab.roster import Roster


def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_table(cur, conn):
    cur.execute('DROP TABLE IF EXISTS NBA')
    cur.execute('CREATE TABLE NBA (player_id INTEGER PRIMARY KEY, name TEXT, teams TEXT, points TEXT, rebounds TEXT, assists TEXT, three_percentages TEXT, steals TEXT, blocks TEXT)')
    conn.commit()

def readDataFromFile(filename):
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path, encoding='utf-8')
    file_data = f.read()
    f.close()
    json_data = json.loads(file_data)
    return json_data

def player_ids_for_team(id):
    base_team_id = 1610612737
    id = base_team_id + id
    #print(id)
    roster = commonteamroster.CommonTeamRoster(team_id=id).get_dict()
    #print(roster)
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
            #print(teams)
            #print(points)

            cur.execute('INSERT INTO NBA (player_id, name, teams, points, rebounds, assists, three_percentages, steals, blocks) VALUES (?,?,?,?,?,?,?,?,?)', \
                (id, name, teams, points, rebounds, assists, three_percentages, steals, blocks,))
        
        conn.commit()

def insertNCAAstats(cur,conn):
    cur, conn = set_up_database('stats.db')
    cur.execute("SELECT name from NBA")
    nba_names = cur.fetchall()
    print(nba_names)
    cur.execute("DROP TABLE IF EXISTS NCAA")
    cur.execute("CREATE TABLE NCAA (name TEXT, id TEXT, season STRING, assists FLOAT, blocks FLOAT, effective_field_goal_percentage FLOAT, field_goal_percentage FLOAT, free_throw_percentage FLOAT, minutes_played INTEGER, points INTEGER)")
    schools = ['Michigan']
    seasons = ['2017,2018,2019']
    x = '2018'
    teams = Teams()
    for team in teams:
        if team.name in schools: 
            name = team.abbreviation 
            roster = Roster(name,x,False)
            for player in roster.players:
                player_name = player.name
                ids = player.player_id
                season = x 
                assists = player.assist_percentage
                blocks = player.block_percentage
                effective_fg = player.effective_field_goal_percentage
                fg_percentage = player.field_goal_percentage
                ft_percentage = player.free_throw_percentage
                minutes = player.minutes_played
                point = player.points
                steal = player.steals
                three_point_perc = player.three_point_percentage
                true_shooting_perc = player.true_shooting_percentage
                turnover_perc  = player.turnover_percentage
                two_point_perc  = player.two_point_percentage
                usage_perc = player.usage_percentage
                cur.execute("INSERT INTO NCAA (name, id, season, assists, blocks, effective_field_goal_percentage, field_goal_percentage, free_throw_percentage, minutes_played, points) VALUES (?,?,?,?,?,?,?,?,?,?)",(player_name,ids,season,assists,blocks,effective_fg,fg_percentage,ft_percentage,minutes,point))
    conn.commit()
        

if __name__ == '__main__':
    cur, conn = set_up_database('stats.db')
    set_up_table(cur, conn)
    insert_player_stats(cur, conn)
    insertNCAAstats(cur,conn)
    #print(player_ids_for_team(0))