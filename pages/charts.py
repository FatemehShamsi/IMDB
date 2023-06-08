
import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random

PASSWORD = ''
USERNAME = ''
st.set_page_config(
    page_title='chart of IMDB Top 250 Movies',
    page_icon=':bar_chart:'
)
st.title("chart of IMDB Top 250 Movies")

db_connection = mysql.connector.connect(
    host="localhost",
    user=USERNAME,
    password=PASSWORD,
    database="Top_250_imdb"
)

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

fig, ax = plt.subplots()

sales_info = df.pivot(index='genre', columns='parental_guide', values='count')

st.bar_chart(sales_info)

db_connection.close()
