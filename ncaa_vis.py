import sqlite3
import os
import plotly.express as px
import pandas as pd

def establish_connection(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

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
    file1.close() 

def NCAA_vis(points, fg, seasons):
    seasons = list(map(str, seasons))
    data = {
        'Points':points,
        'FG %':fg,
        'Seasons':seasons
    }
    df = pd.DataFrame (data, columns= ['Points','FG %','Seasons'])
    fig = px.scatter(df, x='Points', y='FG %', trendline='ols',title='NCAA Player Average Points vs Field Goal %', color='Seasons', labels={'Points':'Average Points','FG %':'Average Field Goal %','seasons':'Seasons Played'})
    fig.show()

def NBA_vis(cur,conn):
    df = pd.read_sql_query("SELECT NBA.points, NBA.field_goal_percentage, NBA.minutes FROM NBA JOIN players ON NBA.player_id = players.player_id WHERE minutes>20",conn)
    fig = px.scatter(df,x='points',y='field_goal_percentage',color='minutes',trendline='ols', labels={
        'points': 'Points Per Game',
        'field_goal_percentage': 'Field Goal Percentage (%)',
        'minutes': 'Minutes Played'
    },
    title='NBA Players Minutes Played Impact on Points Per Game vs FG %')
    fig.show()

def main():
    cur,conn = establish_connection('stats.db')
    x,y,z = calculate(cur,conn)
    write_file(x,y,z)
    NCAA_vis(x,y,z)
    NBA_vis(cur,conn)

main() 