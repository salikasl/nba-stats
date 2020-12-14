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
    cur.execute("CREATE TABLE IF NOT EXISTS NCAA (name TEXT, id TEXT, season STRING, total_points INTEGER, points FLOAT, assists INTEGER, rebounds INTEGER, blocks INTEGER, steals INTEGER, field_goal_perc FLOAT, three_point_percentage FLOAT, minutes INTEGER, points_per_minute FLOAT)")

def getPlayers(cur,conn):
    NBA_names = cur.execute("SELECT name FROM players").fetchall()
    NCAA_names = cur.execute("SELECT name FROM NCAA").fetchall() 
    current_list = [x[0] for x in NCAA_names]
    name_list = [x[0] for x in NBA_names]
    schools = getSchools()
    seasons = ['2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016']
    for team in schools:
        for x in seasons: 
            roster = Roster(team,x,False)
            for player in roster.players:
                if player.name in name_list and player.name not in current_list:
                    print("Found " + player.name + " played in NCAA in " + x)
                    season = x[:3]+(str(int(x[3])-1))+'-'+(x[2:])
                    if season == '201-1-10':
                        season = '2009-10'
                    cur.execute("INSERT INTO NCAA (name, id, season) VALUES (?,?,?)", (player.name,player.player_id,season,))
                    conn.commit()
        if len(current_list) < len(cur.execute("SELECT name from NCAA").fetchall()):
            break 

   
def getSchools():
    rankings = Rankings()
    return list(rankings.current.keys())

def insertNCAAstats(cur,conn):
    players = cur.execute("SELECT name,id,season FROM NCAA").fetchall()
    for name,ids,season in players:
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
        cur.execute("INSERT INTO NCAA (total_points, points, assists, rebounds, blocks, steals, field_goal_perc, three_point_percentage, minutes, points_per_minute) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(total_points,point,assist,rebound,block,steal,fieldgoals,three_point_perc,minutes,points_per_minute,))
    conn.commit() 
    
def calculate(cur,conn):
    avg_points = []
    avg_fg_perc = []
    ncaa_seasons = []

    players = cur.execute("SELECT name from NCAA").fetchall()
    for name in players:
        points = cur.execute("SELECT total_points FROM NCAA WHERE name = ?", (name[0],)).fetchall()
        points = [int(x[0]) for x in points]
        sum_points = sum(points)
        avg_points.append(sum_points/len(points))
        fg = cur.execute('SELECT field_goal_percentage FROM NCAA WHERE name = ?', (name[0],)).fetchall() 
        fg = [(x[0]) for x in fg]
        sum_fg = sum(fg)
        avg_fg_perc.append(sum_fg/len(fg))
        season = cur.execute('SELECT name FROM NCAA WHERE name = ?', (name[0],)).fetchall()
        ncaa_seasons.append(len(season))

    return avg_points,avg_fg_perc,ncaa_seasons

def write_file(points,fg,seasons):
    with open("ncaa_data.txt", 'w') as file1:
        print('Average Points'.ljust(10), 'AVG FG %'.ljust(10), 'NCAA # of Seasons', file=file1)
        for (point, field, season) in zip(points, fg, seasons):
            print(str(round(point, 2)).ljust(10), str(round(field, 2)).ljust(10), str(round(season, 3)).ljust(10), file=file1)

def NCAA_vis(points, fg, seasons):
    seasons = list(map(str, seasons))
    data = {
        'Points':points,
        'FG %':fg,
        'Seasons':seasons
    }
    df = pd.DataFrame (data, columns= ['Points','FG %','Seasons'])
    fig = px.scatter(df, x='Points', y='FG %', title='Average Points vs Field Goal %', color='Seasons', labels={'Points':'Average Points','FG %':'Average Field Goal %','seasons':'Seasons Played'})
    fig.show()

def NBA_vis(cur,conn):
    df = pd.read_sql_query("SELECT NBA.points, NBA.field_goal_percentage, NBA.minutes FROM NBA JOIN players ON NBA.player_id = players.player_id WHERE minutes>20",conn)
    fig = px.scatter(df,x='points',y='field_goal_percentage',color='minutes',trendline='ols', labels={
        'points': 'Points Per Game',
        'field_goal_percentage': 'Field Goal Percentage (%)',
        'minutes': 'Minutes Played'
    },
    title='Minutes Impact on NBA Points Per Game vs FG %')
    fig.show()

def main():
    cur,conn = setUpDatabase('stats.db')
    #setUpTable(cur,conn)
    #getPlayers(cur,conn)
    #if len(cur.execute("SELECT name from NCAA").fetchall()) > 100:
    #    insertNCAAstats(cur,conn)
    #NCAA_vis(cur,conn)
    #NBA_vis(cur,conn)
   # x,y,z = calculate(cur,conn)
   # write_file(x,y,z)
    #NCAA_vis(x,y,z)
    NBA_vis(cur,conn)

main()