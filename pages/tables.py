
import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot

PASSWORD = ''
USERNAME = ''

st.set_page_config(
    page_title='Tables of IMDB Top 250 Movies',
    page_icon= ':page_facing_up:'
)
st.title("Tables of IMDB Top 250 Movies")
# Create a connection to the MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user=USERNAME,
    password=PASSWORD,
    database="Top_250_imdb"
)

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

db_connection.close()
