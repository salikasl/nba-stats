#make a scatter plot based comparing points vs minutes played

import sqlite3
import os
import plotly.express as px
import pandas as pd

def establish_connection(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def get_players(cur, conn):
    players = cur.execute('SELECT players.name FROM players JOIN NCAA ON players.name = NCAA.name').fetchall()
    return list(set([player[0] for player in players]))

def get_nba_stats(cur, conn):

    career_minutes = []
    career_points = []
    seasons_in_ncaa = []

    players = get_players(cur, conn)

    for player in players:
        nba_seasons = cur.execute('SELECT NBA.minutes, NBA.points FROM NBA JOIN players ON NBA.player_id = players.player_id WHERE players.name = (?)', (player,)).fetchall()
        minutes_avg = sum(season[0] for season in nba_seasons)
        career_minutes.append(minutes_avg/len(nba_seasons))
        points_avg = sum(season[1] for season in nba_seasons)
        career_points.append(points_avg/len(nba_seasons))
        ncaa_seasons = cur.execute('SELECT name FROM NCAA WHERE name = (?)', (player,)).fetchall()
        seasons_in_ncaa.append(len(ncaa_seasons))

    return career_minutes, career_points, seasons_in_ncaa

def write_data(minutes, points, seasons):
    with open('scatter_data.txt', 'w') as f:
        print('Minutes'.ljust(10), 'Points'.ljust(10), 'NCAA # of Seasons', file=f)
        for (minute, pts, szn) in zip(minutes, points, seasons):
            print(str(round(minute, 3)).ljust(10), str(round(pts, 3)).ljust(10), str(round(szn, 3)).ljust(10), file=f)

def scatter_plot(minutes, points, seasons):

    seasons = list(map(str, seasons))

    data = {
        'minutes':minutes,
        'points':points,
        'seasons':seasons
    }
    
    df = pd.DataFrame (data, columns= ['minutes','points','seasons'])
    fig = px.scatter(df, x='minutes', y='points', title='Points vs Minutes Played in the NBA', color='seasons', labels={'minutes':'Minutes Played','points':'Points','seasons':'Seasons in the NCAA'})
    fig.show()



if __name__ == '__main__':
    cur, conn = establish_connection('stats.db')
    minutes, points, num_seasons = get_nba_stats(cur, conn)
    write_data(minutes, points, num_seasons)
    scatter_plot(minutes, points, num_seasons)
    
