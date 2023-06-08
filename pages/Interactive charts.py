import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

PASSWORD = ''
USERNAME = ''

st.set_page_config(
    page_title=' Interactive chart',
    page_icon= ':bar_chart:'
)




db_connection = mysql.connector.connect(
    host="localhost",
    user=USERNAME,
    password=PASSWORD,
    database="Top_250_imdb"
)
st.write('')
st.subheader("Top 10 Selling in genre Movies")
query = "SELECT DISTINCT genre FROM genre"
genres_df = pd.read_sql_query(query, con=db_connection)

list_of_genres = genres_df['genre'].tolist()
genre = st.selectbox("Select a genre", list_of_genres)


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
ax.bar(df["title"], df["gross_us_canada"])
ax.set_title(f"Best-Selling {genre} Movies")
ax.set_xticklabels(df['title'], rotation=45, ha='right',color='#04334b')

ax.set_ylabel("Box Office Revenue (in millions)")
ax.tick_params(axis="x", rotation=45,labelsize=8)
st.pyplot(fig)

db_connection.close()