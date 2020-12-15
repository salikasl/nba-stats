import requests
import json
import os
import sqlite3
import plotly 
import plotly.express as px
import pandas as pd 
from sportsreference.ncaab.roster import Player, Roster
from sportsreference.ncaab.teams import Teams
from sportsreference.ncaab.rankings import Rankings

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpTable(cur,conn):
    cur.execute("CREATE TABLE IF NOT EXISTS NCAA (name TEXT, id TEXT, season STRING, total_points INTEGER, points FLOAT, assists INTEGER, rebounds INTEGER, blocks INTEGER, steals INTEGER, field_goal_perc FLOAT, three_point_percentage FLOAT, minutes INTEGER, points_per_minute FLOAT)")
    conn.commit()

def getSchools():
    rankings = Rankings()
    return list(rankings.current.keys())

def getPlayers(cur,conn):
    NBA_names = cur.execute("SELECT name FROM players").fetchall()
    NCAA_names = cur.execute("SELECT name FROM NCAA").fetchall() 
    count = 0
    current_list = [x[0] for x in NCAA_names]
    name_list = [x[0] for x in NBA_names]
    names = set(name_list)
    name_list = [item for item in names if item not in current_list]
    schools = getSchools()
    seasons = ['2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016']
    for team in schools:
        for x in seasons: 
            roster = Roster(team,x,False)
            for player in roster.players:
                if player.name in name_list and player.name not in current_list:
                    if len(current_list) < 100:
                        count+=1
                        if count > 24:
                            break
                    print("Found " + player.name + " played in NCAA in " + x)
                    season = x[:3]+(str(int(x[3])-1))+'-'+(x[2:])
                    if season == '201-1-10':
                        season = '2009-10'
                    games_played = player(season).games_played 
                    assist = player(season).assists/games_played
                    rebound = player(season).total_rebounds/games_played
                    block = player(season).blocks/games_played
                    fieldgoals = player(season).field_goal_percentage
                    minutes = player(season).minutes_played/games_played
                    total_points = player(season).points
                    point = player(season).points/games_played
                    steal = player(season).steals/games_played
                    three_point_perc = player(season).three_point_percentage 
                    points_per_minute = player(season).points/minutes  
                    cur.execute("INSERT INTO NCAA (name, id, season,total_points,points,assists,rebounds,blocks,steals,field_goal_perc,three_point_percentage,minutes,points_per_minute) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (player.name,player.player_id,season,total_points,point,assist,rebound,block,steal,fieldgoals,three_point_perc,minutes,points_per_minute,))
                    conn.commit()           
        if len(current_list) < len(cur.execute("SELECT name from NCAA").fetchall()):
            break 

def insertNCAAstats(cur,conn):
    players = cur.execute("SELECT name,id,season FROM NCAA").fetchall()
    for name,ids,season in players:
        try:
            player = Player(ids)
            games_played = player(season).games_played 
            assist = player(season).assists/games_played
            rebound = player(season).total_rebounds/games_played
            block = player(season).blocks/games_played
            fieldgoals = player(season).field_goal_percentage
            minutes = player(season).minutes_played/games_played
            total_points = player(season).points
            point = player(season).points/games_played
            steal = player(season).steals/games_played
            three_point_perc = player(season).three_point_percentage 
            points_per_minute = player(season).points/minutes                 
            cur.execute("UPDATE NCAA SET total_points = ?, points = ?, assists= ?, rebounds = ?, blocks = ?, steals = ?, field_goal_perc = ?, three_point_percentage = ?, minutes = ?, points_per_minute = ? WHERE name = ?",(total_points,point,assist,rebound,block,steal,fieldgoals,three_point_perc,minutes,points_per_minute,name,))
        except:
            continue
    conn.commit() 
    

def main():
    cur,conn = setUpDatabase('stats.db')
    #setUpTable(cur,conn)
    getPlayers(cur,conn)
    #if len(cur.execute("SELECT name from NCAA").fetchall()) > 100:
       #insertNCAAstats(cur,conn)
   

main()