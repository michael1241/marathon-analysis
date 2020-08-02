#! /usr/bin/env python3

import json

import pandas as pd
import plotly.express as px


outfile = 'summer20.csv'

def rawAnalysis():
    infilegames = 'summer20.json'
    infilestandings = 'summer20standings.json'

    results = {}

    def startDict(jsonrow):
        white = jsonrow['players']['white']['user']['name']
        black = jsonrow['players']['black']['user']['name']
        if white not in results:
            results[white] = {'playtime': 0, 'initRating': jsonrow['players']['white']['rating'], 'zperf': 0, 'nperf': 0, 'games': 0, 'start': jsonrow['createdAt']}
        if black not in results:
            results[black] = {'playtime': 0, 'initRating': jsonrow['players']['black']['rating'], 'zperf': 0, 'nperf': 0, 'games': 0, 'start': jsonrow['createdAt']}
        return white, black

    def userPlaytime(jsonrow, white, black):
        playmsec = (jsonrow['lastMoveAt'] - jsonrow['createdAt']) / (1000*60)
        results[white]['playtime'] += playmsec
        results[black]['playtime'] += playmsec

    def zerkPerf(jsonrow, white, black):
        white_zerk = jsonrow['players']['white'].get('berserk')
        white_add_to = 'zperf' if white_zerk else 'nperf'
        results[white][white_add_to] += jsonrow['players']['white']['ratingDiff']
        black_zerk = jsonrow['players']['black'].get('berserk')
        black_add_to = 'zperf' if black_zerk else 'nperf'
        results[black][black_add_to] += jsonrow['players']['black']['ratingDiff']

    def gamesCount(jsonrow, white, black):
        results[white]['games'] += 1
        results[black]['games'] += 1

    with open(infilegames, 'r') as d:
        for row in reversed(list(d)):
            jsonrow = json.loads(row)
            white, black = startDict(jsonrow)
            userPlaytime(jsonrow, white, black)
            zerkPerf(jsonrow, white, black)
            gamesCount(jsonrow, white, black)

    with open(infilestandings, 'r') as s:
        for row in s:
            jsonrow = json.loads(row)
            username = jsonrow['username']
            if username not in results: #no games played
                continue
            results[username]['placement'] = jsonrow['rank']
            results[username]['score'] = jsonrow['score']
            results[username]['finalRating'] = jsonrow['rating']
            results[username]['performance'] = jsonrow['performance']

    for player in results.items():
        player[1]['ppg'] = player[1]['score'] / player[1]['games']

    with open(outfile, 'w') as f:
        print('player,Playtime (min),Initial Rating,Berserk Perf,Normal Perf,Game Count,Start Time,Placement,Score,Final Rating,Performance,Points Per Game', file=f)
        for player in results.items():
            print(player[0], ",", ", ".join([str(x) for x in player[1].values()]), file=f)

def plots():
    df = pd.read_csv(outfile)

    fig = px.scatter(df, x='Game Count', y='Placement',
        color='Initial Rating', color_continuous_scale='thermal',
        title='Finishing Position vs Games Played',
        template='plotly_dark')
    fig.update_yaxes(autorange='reversed')
    fig.show()

    fig = px.scatter(df, x='Score', y='Placement',
        color='Initial Rating', color_continuous_scale='thermal',
        log_y=True,
        title='Finishing Position vs Score',
        template='plotly_dark')
    fig.update_yaxes(autorange='reversed')
    fig.show()

    fig = px.histogram(df, x='Initial Rating',
        color='Score', color_continuous_scale='thermal',
        template='plotly_dark')
    fig.show()

    #points per game vs time (binned by rating)
    df_10_plus_games = df[df['Game Count'] >= 10]
    df_10_plus_games['Binned Rating'] = ((df_10_plus_games['Initial Rating'] / 500).astype(int) * 500).astype(str)
    df_10_plus_games = df_10_plus_games[df_10_plus_games['Binned Rating'] == '2500']
    fig = px.scatter(df_10_plus_games, x='Start Time', y='Points Per Game',
        title='Start Time vs Points Per Game',
        template='plotly_dark',
        trendline='ols')
    fig.show()

    fig = px.scatter(df, x='Playtime (min)', y='Placement',
        color='Initial Rating', color_continuous_scale='thermal',
        log_y=True,
        title='Finishing Position vs Playtime',
        template='plotly_dark')
    fig.update_yaxes(autorange='reversed')
    fig.show()


rawAnalysis()
plots()
