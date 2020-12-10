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
    cur.execute("CREATE TABLE NCAA (name TEXT, id TEXT, season STRING, points INTEGER, assists INTEGER, blocks INTEGER, steals INTEGER, field_goal_percentage FLOAT, three_point_percentage FLOAT, minutes_played INTEGER, games_played INTEGER)")
    cur.execute("SELECT name FROM players")
    NBA_names = cur.fetchall() 
    name_list = [x[0] for x in NBA_names]
    seasons = ['2010','2011','2012','2013','2014','2015','2016']
    teams = Teams()
    for team in teams:
        for x in seasons: 
            try:
                roster = Roster(team.abbreviation,x,False)
                for player in roster.players:
                    if player.name in name_list:
                        print("Worked")
                        player_name = player.name
                        ids = player.player_id
                        season = x 
                        assist = player.assists
                        block = player.blocks
                        fg_percentage = player.field_goal_percentage
                        minutes = player.minutes_played
                        point = player.points
                        steal = player.steals
                        three_point_perc = player.three_point_percentage
                        games_played = player.games_played
                        cur.execute("INSERT INTO NCAA (name, id, season, points, assists, blocks, steals, field_goal_percentage, three_point_percentage, minutes_played, games_played) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(player_name,ids,season,point,assist,block,steal,fg_percentage,three_point_perc,minutes,games_played))
            except:
                continue
                 
    conn.commit()

def catch_error():
    teams = Teams()
    for _ in range(200):
        try: 
            for team in teams:
                print("Works:"+team.name)
        except:
            print(team.name)
            continue

    
    
    
def main():
    cur,conn = setUpDatabase('stats.db')
    insertNCAAstats(cur,conn)


main() 