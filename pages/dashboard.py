import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
import plotly.graph_objs as go
import plotly
import networkx as nx

PASSWORD = ''
USERNAME = ''

db_connection = mysql.connector.connect(
    host="localhost",
    user=USERNAME,
    password=PASSWORD,
    database="Top_250_imdb"
)



st.set_page_config(
    page_title='IMDb Top 250 Movies',
    page_icon= ':clapper:'
)


st.title("IMDb Top 250 Movies")
st.write('')

image = plt.imread('C:/Users/Fatemeh/Desktop/advanced_python/pages/imdb.png')

st.image(image)


st.write('')
st.header("Tables of IMDB Top 250 Movies")

# --------------------------------- 1 ------------------------------------------
st.write('')
st.subheader("Filter movies by year")
st.write('')
start_year = st.number_input("Enter start year:", min_value=1900, max_value=2023, value=1997)
end_year = st.number_input("Enter end year:", min_value=1900, max_value=2023, value=2021)


query = f"SELECT * FROM movie WHERE year >= {start_year} AND year <= {end_year}"
movies_df = pd.read_sql_query(query, con=db_connection)

st.dataframe(movies_df)
st.write("---")
st.write('')
# ----------------------------------- 2 ----------------------------------------
st.write('')
st.subheader("Filter movies by run time")
st.write('')
query = "SELECT MIN(run_time) FROM movie"
min_run_tim = pd.read_sql_query(query, con=db_connection)
DEFAULT_DURATION_MIN = int(min_run_tim.iloc[0])
query = "SELECT MAX(run_time) FROM movie"
max_run_tim = pd.read_sql_query(query, con=db_connection)
DEFAULT_DURATION_MAX = int(max_run_tim.iloc[0])


duration_min, duration_max = st.slider(
    "Select duration range (in minutes)",
    min_value=DEFAULT_DURATION_MIN,
    max_value=DEFAULT_DURATION_MAX,
    value=(DEFAULT_DURATION_MIN, DEFAULT_DURATION_MAX),
    step=1
)


query = f"""SELECT title,year,run_time,parental_guide FROM movie 
WHERE run_time BETWEEN {duration_min} AND {duration_max}"""
movies_df = pd.read_sql_query(query, con=db_connection)


st.dataframe(movies_df)

st.write("---")
st.write('')
# ----------------------------------- 3 ----------------------------------------
st.write('')
st.subheader("Filter movies by select actor")
st.write('')
query = "SELECT DISTINCT name FROM cast JOIN person ON cast.person_id = person.id"
actors = pd.read_sql_query(query, con=db_connection)["name"].tolist()


selected_actors = st.multiselect("Select actors", actors)


query = """SELECT title,year,name,parental_guide FROM cast 
JOIN person ON cast.person_id = person.id JOIN movie ON movie.id=cast.movie_id """

for idx, actor in enumerate(selected_actors):
    query += f" WHERE name = '{actor}'"
    if idx < len(selected_actors) - 1:
        query += " OR"


movies_df = pd.read_sql_query(query, con=db_connection)


st.dataframe(movies_df)
st.write("---")
st.write('')
# ----------------------------------- 4 ---------------------------------
st.write('')
st.subheader("Filter movies by select genre")
st.write('')
query = "SELECT DISTINCT genre FROM genre"
genres_df = pd.read_sql_query(query, con=db_connection)

genres = genres_df['genre'].tolist()

selected_genre = st.selectbox("Select a genre", genres)

query = f"""SELECT title,year,parental_guide,genre FROM movie 
JOIN genre ON movie.id=genre.movie_id 
WHERE genre = '{selected_genre}'"""

movies_df = pd.read_sql_query(query, con=db_connection)


st.dataframe(movies_df)
st.write("---")
st.write('')
# ----------------------------------- 5 ---------------------------------
st.write('')
st.subheader("Addition: Filter movies by director")
st.write('')
query = """
SELECT DISTINCT name FROM crew
JOIN person ON crew.person_id=person.id
WHERE role='director'
 """
director_df = pd.read_sql_query(query, con=db_connection)

directors = director_df['name'].tolist()
selected_director = st.selectbox("Select a director", directors)

query = f"""SELECT title,year,parental_guide FROM movie 
JOIN crew ON movie.id=crew.movie_id 
JOIN person ON person.id=crew.person_id 
WHERE name = '{selected_director}'"""

movies_df = pd.read_sql_query(query, con=db_connection)

st.dataframe(movies_df)

st.write("---")
st.write('')
# ----------------------------------- 5 ---------------------------------
st.write('')
st.subheader("Addition: Filter movies by director and actor")
st.write('')
query = """
SELECT DISTINCT name FROM crew
JOIN person ON crew.person_id=person.id
WHERE role='director'
 """
director_df = pd.read_sql_query(query, con=db_connection)

directors = director_df['name'].tolist()
selected_director1 = st.selectbox("Select a director", directors,key="selectbox1")

query = """
SELECT DISTINCT name FROM cast
JOIN person ON cast.person_id=person.id
 """
actor_df = pd.read_sql_query(query, con=db_connection)

actors = actor_df['name'].tolist()
selected_actor1 = st.selectbox("Select a actor", actors)

query = f"""SELECT title,year,parental_guide FROM movie 
JOIN crew ON movie.id=crew.movie_id 
JOIN person pd ON pd.id=crew.person_id 
JOIN cast ON movie.id=cast.movie_id 
JOIN person ps ON ps.id=cast.person_id 
WHERE pd.name = '{selected_director1}' AND ps.name = '{selected_actor1}';"""
movies_df = pd.read_sql_query(query, con=db_connection)

st.dataframe(movies_df)

###############################################################################
st.write('')
st.header("chart of IMDB Top 250 Movies")
# --------------------------------- 1 ------------------------------------------

st.write('')
st.subheader("Top 10 gross US & Canada")

query = f"SELECT * FROM movie ORDER BY gross_us_canada DESC LIMIT 10;"
movies_df = pd.read_sql_query(query, con=db_connection)

fig, ax = plt.subplots()

ax.bar(movies_df['title'], movies_df['gross_us_canada'], color='#04334b')
ax.set_xticklabels(movies_df['title'], rotation=45, ha='right')
ax.set_xlabel('Movie Title', fontsize=10)
ax.set_ylabel('Number of Sales', fontsize=12)

st.pyplot(fig)
st.write("---")
st.write('')

# --------------------------------- 2 ------------------------------------------

st.write('')
st.subheader("Top 5 Actors with Most Movie Appearances")
query = """
SELECT name,COUNT(name) as count_name FROM cast
    JOIN movie m on m.id = cast.movie_id
    JOIN person p on p.id = cast.person_id
GROUP BY name
ORDER BY count_name DESC
LIMIT 5;
"""
#
movies_df = pd.read_sql_query(query, con=db_connection)

fig, ax = plt.subplots()
ax.bar(movies_df['name'], movies_df['count_name'], color='#04334b')

ax.set_xticklabels(movies_df['name'], rotation=45, ha='right', fontsize=10)
ax.set_ylabel('Number of Movies', fontsize=12)

st.pyplot(fig)
st.write("---")
st.write('')

# --------------------------------- 3 ------------------------------------------

st.subheader("Pie charts of the number of different genres")
st.write('')
query = """
SELECT genre,COUNT(genre) as c_g FROM 
movie JOIN genre ON movie.id=genre.movie_id 
GROUP BY genre;
"""
movies_df = pd.read_sql_query(query, con=db_connection)

recipe = movies_df['genre'].to_list()
color = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
         for i in range(len(recipe))]

fig, ax = plt.subplots(figsize=(8, 8))

wedges, texts, = ax.pie(movies_df['c_g'], wedgeprops=dict(width=0.8, edgecolor='w'), startangle=-40, counterclock=False)
for i, wedge in enumerate(ax.patches):
    wedge.set_facecolor(color[i])
ax.legend(wedges, recipe,
          title="Genres",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1))

ax.set_title('Movie Genres', fontsize=14, fontweight='bold')
st.pyplot(fig)

st.write("---")
st.write('')

# --------------------------------- 4 ------------------------------------------

st.write('')
st.subheader('Pie chart  of the number of parental guide of movies')
query = """
SELECT parental_guide,COUNT(parental_guide) as c_g FROM movie  
GROUP BY parental_guide 
order by parental_guide desc;
"""
movies_df = pd.read_sql_query(query, con=db_connection)
fig4, ax4 = plt.subplots(figsize=(8, 8))
parental_guide = movies_df['parental_guide'].to_list()
wedges4, texts4 = ax4.pie(movies_df['c_g'], wedgeprops=dict(width=0.8, edgecolor='w'), startangle=40,
                          counterclock=False, textprops=dict(color="w"))
bbox_props = dict(boxstyle="square,pad=0.4", fc="w", ec="k", lw=0.72)
kw = dict(arrowprops=dict(arrowstyle="-"),
          bbox=bbox_props, zorder=0, va="center")

for i, p in enumerate(wedges4):
    ang = (p.theta2 - p.theta1) / 2. + p.theta1
    y = np.sin(np.deg2rad(ang))
    x = np.cos(np.deg2rad(ang))
    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    connectionstyle = f"angle,angleA=0,angleB={ang}"
    kw["arrowprops"].update({"connectionstyle": connectionstyle})
    ax4.annotate(parental_guide[i], xy=(x, y), xytext=(1.5 * np.sign(x), 1.1 * y),
                 horizontalalignment=horizontalalignment, fontsize=10, **kw)

ax4.set_title('Movie Parental guide', fontsize=14, fontweight='bold')
st.pyplot(fig4)
st.write('')
st.write('----')

# --------------------------------- 5 ------------------------------------------

st.subheader("Number of occurrences of each parental guide in each genre")
st.write('')

query = """
SELECT parental_guide, genre, COUNT(*) AS count
FROM movie
JOIN genre ON movie.id = genre.movie_id
GROUP BY parental_guide, genre
ORDER BY parental_guide
"""
df = pd.read_sql(query, con=db_connection)



gen_parental_info = df.pivot(index='genre', columns='parental_guide', values='count')

st.bar_chart(gen_parental_info,width=1200, height=600)
# #############################################################################
st.header('Interactive chart')
st.write('')
st.subheader("Top 10 Selling in genre Movies")
query = "SELECT DISTINCT genre FROM genre"
genres_df = pd.read_sql_query(query, con=db_connection)

list_of_genres = genres_df['genre'].tolist()
genre = st.selectbox("Select a genre", list_of_genres,key="selectbox2")


query = f"""
SELECT title, gross_us_canada
FROM movie
JOIN genre ON genre.movie_id = movie.id
WHERE genre = '{genre}'
ORDER BY gross_us_canada DESC
LIMIT 10
"""
df = pd.read_sql_query(query, con=db_connection)


fig, ax = plt.subplots()
ax.bar(df["title"], df["gross_us_canada"],color='#04334b')
ax.set_title(f"Best-Selling {genre} Movies")
ax.set_xticklabels(df['title'], rotation=45, ha='right',color='#04334b')

ax.set_ylabel("Box Office Revenue (in millions)")
ax.tick_params(axis="x", rotation=45,labelsize=8)
st.pyplot(fig)

# ###############################################################################
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

db_connection.close()