import requests
import json
import os
import sqlite3
from sportsreference.ncaab.roster import Player
from sportsreference.ncaab.teams import Teams
from sportsreference.ncaab.roster import Roster


def readDataFromFile(filename):
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path, encoding='utf-8')
    file_data = f.read()
    f.close()
    json_data = json.loads(file_data)
    return json_data

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

#def create_table(data, cur,conn):


#def main():
 #   cur, conn = setUpDatabase('stats.db')

#main()
def insertNCAAstats(cur,conn):
    cur, conn = setUpDatabase('stats.db')
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
