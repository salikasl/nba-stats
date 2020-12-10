import requests
import json
import os
import sqlite3
from sportsreference.ncaab.roster import Player
from sportsreference.ncaab.teams import Teams
from sportsreference.ncaab.roster import Roster
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
    cur.execute("CREATE TABLE NCAA (name TEXT, id TEXT, season STRING, points INTEGER, assists INTEGER, blocks INTEGER, steals INTEGER, field_goal_percentage FLOAT, three_point_percentage FLOAT, minutes_played INTEGER, games_played INTEGER)")

def getPlayers(cur,conn):
    cur.execute("SELECT name FROM players")
    NBA_names = cur.fetchall() 
    name_list = [x[0] for x in NBA_names]
    schools = getSchools()
    shared_names = []
    seasons = ['2009','2010','2011','2012','2013','2014','2015','2016']
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
        season_param = season[:3]+(str(int(season[3])-1))+'-'+(season[2:])
        player = Player(ids)
        assist = player(season_param).assists
        block = player(season_param).blocks
        fg_percentage = player(season_param).field_goal_percentage
        minutes = player(season_param).minutes_played
        point = player(season_param).points
        steal = player(season_param).steals
        three_point_perc = player(season_param).three_point_percentage
        games_played = player(season_param).games_played                    
        cur.execute("INSERT INTO NCAA (name, id, season, points, assists, blocks, steals, field_goal_percentage, three_point_percentage, minutes_played, games_played) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(name,ids,season,point,assist,block,steal,fg_percentage,three_point_perc,minutes,games_played))
        conn.commit()



def main():
    cur,conn = setUpDatabase('stats.db')
    setUpTable(cur,conn)
    insertNCAAstats(cur,conn)
   
    



main() 