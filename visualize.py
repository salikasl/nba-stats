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
        print(nba_seasons)
        minutes_avg = sum(season[0] for season in nba_seasons)
        career_minutes.append(minutes_avg/len(nba_seasons))
        points_avg = sum(season[1] for season in nba_seasons)
        career_points.append(points_avg/len(nba_seasons))
        ncaa_seasons = cur.execute('SELECT name FROM NCAA WHERE name = (?)', (player,)).fetchall()
        print(ncaa_seasons)
        seasons_in_ncaa.append(len(ncaa_seasons))

    return career_minutes, career_points, seasons_in_ncaa

def scatter_plot(minutes, points, seasons):

    seasons = map(str, seasons)
    
    fig = px.scatter(x=minutes, y=points, title='Points vs Minutes Played in the NBA', color=seasons, labels={'Points':'Minutes Played'})
    fig.show()



if __name__ == '__main__':
    cur, conn = establish_connection('stats.db')
    minutes, points, num_seasons = get_nba_stats(cur, conn)
    scatter_plot(minutes, points, num_seasons)
