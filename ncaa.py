import requests
import json
import os
import sqlite3
import plotly.express as px
import pandas as pd 
from sportsreference.ncaab.roster import Player, Roster
from sportsreference.ncaab.teams import Teams
from sportsreference.ncaab.rankings import Rankings


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

def setUpTable(cur,conn):
    cur.execute("DROP TABLE IF EXISTS NCAA")
    cur.execute("CREATE TABLE NCAA (name TEXT, id TEXT, season STRING, total_points INTEGER, points FLOAT, assists FLOAT, rebounds FLOAT, blocks FLOAT, steals FLOAT, field_goal_percentage FLOAT, three_point_percentage FLOAT, minutes_played INTEGER, points_per_minute FLOAT)")

def getPlayers(cur,conn):
    cur.execute("SELECT name FROM players")
    NBA_names = cur.fetchall() 
    name_list = [x[0] for x in NBA_names]
    schools = getSchools()
    shared_names = []
    seasons = ['2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016']
    for team in schools:
            for x in seasons: 
                roster = Roster(team,x,False)
                for player in roster.players:
                    if player.name in name_list:
                        tup = (player.name,player.player_id,x)
                        shared_names.append(tup)         
    return shared_names         
   
def getSchools():
    rankings = Rankings()
    return list(rankings.current.keys())

def insertNCAAstats(cur,conn):
    names = getPlayers(cur,conn)
    for name,ids,season in names:
        season = season[:3]+(str(int(season[3])-1))+'-'+(season[2:])
        if season == '201-1-10':
            season=='2009-10'
        player = Player(ids)
        games_played = player(season).games_played 
        assist = player(season).assists/games_played
        rebound = player(season).total_rebounds/games_played
        block = player(season).blocks/games_played
        fg_percentage = player(season).field_goal_percentage
        minutes = player(season).minutes_played
        total_points = player(season).points
        point = player(season).points/games_played
        steal = player(season).steals/games_played
        three_point_perc = player(season).three_point_percentage 
        points_per_minute = player(season).points/minutes                 
        cur.execute("INSERT INTO NCAA (name, id, season, total_points, points, assists, rebounds, blocks, steals, field_goal_percentage, three_point_percentage, minutes_played,points_per_minute) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",(name,ids,season,total_points,point,assist,rebound,block,steal,fg_percentage,three_point_perc,minutes,points_per_minute,))
        conn.commit()
    
def visualize(cur,conn):
    df = pd.read_sql_query("SELECT * FROM NCAA",conn)
    fig = px.line(df,x='season',y='points',color='name')
    fig.show()

def main():
    cur,conn = setUpDatabase('stats.db')
    setUpTable(cur,conn)
    insertNCAAstats(cur,conn)
    #visualize(cur,conn)

main()