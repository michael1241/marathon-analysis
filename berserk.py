#! /usr/bin/env python3

import json

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

def dfPrep():
    rd_bins = [x for x in range(-1000,1001,50)]
    d = {b:{zerk:{'win': 0, 'draw': 0, 'loss': 0} for zerk in ['underdogzerk', 'overdogzerk', 'doublezerk', 'nozerk']} for b in rd_bins}

    def winConv(result):
        if result == 'win':
            return 'loss'
        elif result == 'loss':
            return 'win'
        return 'draw'


    infilegames = 'summer20.json'
    with open(infilegames, 'r') as s:
        for row in s:
            jsonrow = json.loads(row)
            rating_diff = jsonrow['players']['white']['rating'] - jsonrow['players']['black']['rating']
            rd_white = max(min(round(rating_diff/50)*50,1000),-1000)
            rd_black = rd_white * -1

            winner = jsonrow.get('winner')
            if winner == 'white':
                result = 'win'
            elif winner == 'black':
                result = 'loss'
            else:
                result = 'draw'

            whitezerk = jsonrow['players']['white'].get('berserk')
            blackzerk = jsonrow['players']['black'].get('berserk')
            if whitezerk and blackzerk:
                zerk = 'doublezerk'
            elif not whitezerk and not blackzerk:
                zerk = 'nozerk'
            elif whitezerk:
                zerk = 'overdogzerk' if rating_diff >= 0 else 'underdogzerk'
            elif blackzerk:
                zerk = 'overdogzerk' if rating_diff < 0 else 'underdogzerk'

            d[rd_white][zerk][result] += 1
            d[rd_black][zerk][winConv(result)] += 1

    df = pd.DataFrame.from_dict(d, orient='index').stack().to_frame()
    df = pd.DataFrame(df[0].values.tolist(), index=df.index)
    #df.rename(columns={df.columns[-2]:'rd_bucket', df.columns[-1]:'zerk'}, inplace=True)
    #rename doesn't work, renamed file manually
    df['total'] = df.win + df.draw + df.loss
    df['win%'] = (df.win / df.total) * 100
    df['draw%'] = (df.draw / df.total) * 100
    df['loss%'] = (df.loss / df.total) * 100
    df.to_csv('berserk.csv')

def makePlot(df):
    xscale = [x for x in range(-1000,1001,50)]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["win%"],
        x= xscale,
        name="Win %",
        marker=dict(
            color='rgba(0,128,0, 0.6)',
            line=dict(color='rgba(0,128,0, 0.5)', width=0.05)
        )
    ))
    fig.add_trace(go.Bar(
        y=df["draw%"],
        x= xscale,
        name="Draw %",
        marker=dict(
            color='rgba(0,0,255, 0.6)',
            line=dict(color='rgba(0,0,255, 0.5)', width=0.05)
        )
    ))
    fig.add_trace(go.Bar(
        y=df["loss%"],
        x= xscale,
        name="Loss %",
        marker=dict(
            color='rgba(128,0,0, 0.5)',
            line=dict(color='rgba(128,0,0, 0.5)', width=0.05)
        )
    ))
    fig.update_layout(
            yaxis=dict(
            title_text="Win %",
            ticktext=["0%", "20%", "40%", "60%","80%","100%"],
            tickvals=[0, 20, 40, 60, 80, 100],
            tickmode="array",
            titlefont=dict(size=15),
    ),
    barmode='stack')
    fig.show()

#dataPrep()

df = pd.read_csv('berserk.csv')

for zerk in ['underdogzerk', 'overdogzerk', 'doublezerk', 'nozerk']:
    df_filter = df['zerk'] == zerk
    df_filter = df[df_filter]
    makePlot(df_filter)
