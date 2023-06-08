import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title='IMDb Top 250 Movies',
    page_icon= ':clapper:'
)


st.title("IMDb Top 250 Movies")
st.write('')

image = plt.imread('C:/Users/Fatemeh/Desktop/advanced_python/pages/imdb.png')

st.image(image)

