import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly
import networkx as nx

PASSWORD = ''
USERNAME = ''

st.set_page_config(
    page_title=' Interactive chart',
    page_icon=':bar_chart:'
)

db_connection = mysql.connector.connect(
    host="localhost",
    user=USERNAME,
    password=PASSWORD,
    database="Top_250_imdb"
)


st.subheader('Actor Collaboration Graph')

query = """
SELECT mc2.name as 'person #1' , mc1.name as 'person #2' , COUNT(mc1.movie_id) as  movies_played_together
FROM (SELECT movie_id,cast.person_id,name FROM cast
    JOIN person p on p.id = cast.person_id) mc1
    JOIN (SELECT movie_id,cast.person_id,name FROM cast
    JOIN person p on p.id = cast.person_id) mc2
        ON mc1.movie_id=mc2.movie_id AND mc1.person_id > mc2.person_id
GROUP BY mc1.name  , mc2.name
ORDER BY movies_played_together DESC,mc2.name,mc1.name
"""

movies_df = pd.read_sql_query(query, db_connection)


actor_collaboration = {}
for index, row in movies_df.iterrows():
    actor_pair = tuple((row['person #1'], row['person #2']))
    actor_collaboration[actor_pair] = row['movies_played_together']

G = nx.Graph()
for actor_pair, count in actor_collaboration.items():
    actor1, actor2 = actor_pair
    G.add_node(actor1)
    G.add_node(actor1)
    G.add_edge(actor1, actor2, weight=count)

pos = nx.spring_layout(G, k=0.2, iterations=50)
for n, p in pos.items():
    G.nodes[n]['pos'] = p

edge_trace = go.Scatter(
    x=[],
    y=[],
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

for edge in G.edges():
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    edge_trace['x'] += tuple([x0, x1, None])
    edge_trace['y'] += tuple([y0, y1, None])

node_trace = go.Scatter(
    x=[],
    y=[],
    text=[],
    mode='markers',
    hoverinfo='text',
    marker=dict(
        color=[],
        size=15,
        line=dict(width=0)))

for node in G.nodes():
    x, y = G.nodes[node]['pos']
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])
    node_trace['text'] += tuple([node])

fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    showlegend=False,
                    width=1000,
                    height=800,
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

st.plotly_chart(fig)


