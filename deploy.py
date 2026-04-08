import pickle
import streamlit as st
import requests

import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# ---------- PAGE CONFIG ----------
st.set_page_config(layout="wide")

# ---------- SESSION STATE ----------
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

if "last_movie" not in st.session_state:
    st.session_state.last_movie = None

# ---------- FUNCTIONS ----------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')

    if poster_path:
        return "https://image.tmdb.org/t/p/original/" + poster_path
    return "https://via.placeholder.com/500x750"

def recommend(movie, progress_bar, progress_text):
    index = movies[movies['title'] == movie].index[0]

    # Step 1
    progress_bar.progress(10)
    progress_text.markdown(
        "<div style='text-align:center; color:white;'>Finding similar movies... 10%</div>",
        unsafe_allow_html=True
    )

    distances = sorted(list(enumerate(similarity[index])),
                       reverse=True, key=lambda x: x[1])

    # Step 2
    progress_bar.progress(30)
    progress_text.markdown(
        "<div style='text-align:center; color:white;'>Processing similarity... 30%</div>",
        unsafe_allow_html=True
    )

    names = []
    posters = []

    total_movies = 5

    # Step 3 (real progress per API call)
    for count, i in enumerate(distances[1:6]):
        movie_id = movies.iloc[i[0]].movie_id

        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))

        percent = 30 + int(((count + 1) / total_movies) * 70)

        progress_bar.progress(percent)
        progress_text.markdown(
            f"<div style='text-align:center; color:white;'>Searching similar movies... {percent}%</div>",
            unsafe_allow_html=True
        )

    return names, posters


# ---------- LOAD DATA ----------
movies = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

# ---------- SELECT MOVIE ----------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_movie = st.selectbox("Select a movie", movies['title'].values)

# ---------- RESET ----------
if st.session_state.last_movie != selected_movie:
    st.session_state.recommendations = None
    st.session_state.last_movie = selected_movie

# ---------- BACKGROUND ----------
movie_id = movies[movies['title'] == selected_movie].iloc[0].movie_id
bg_poster = fetch_poster(movie_id)

# ---------- CSS ----------
st.markdown(f"""
<style>

/* Background */
.stApp {{
    background: url("{bg_poster}");
    background-size: cover;
    background-position: center;
}}

.stApp::before {{
    content: "";
    position: fixed;
    width: 100%;
    height: 100%;
    backdrop-filter: blur(14px);
    background: rgba(0,0,0,0.65);
    z-index: -1;
}}

/* Header */
.header-box {{
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    width: fit-content;
    margin: auto;
    margin-bottom: 30px;
}}

.title {{
    font-size: 48px;
    color: white;
    font-weight: 700;
}}

.subtitle {{
    color: #d1d5db;
    font-size: 16px;
}}

/* Selectbox */
div[data-baseweb="select"] {{
    background: rgba(255,255,255,0.15) !important;
    backdrop-filter: blur(15px);
    border-radius: 12px;
    padding: 8px;
    font-size: 18px;
    color: white;
}}

/* Button */
.stButton > button {{
    background: transparent;
    color: white;
    border: 2px solid white;
    border-radius: 30px;
    padding: 12px 40px;
    font-weight: bold;
    font-size: 16px;
}}

/* Movie cards */
.movie-card {{
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    border-radius: 12px;
    padding: 10px;
    transition: 0.3s;
}}

.movie-card:hover {{
    transform: scale(1.08);
}}

/* Movie title */
.movie-title {{
    color: #ffffff;
    margin-top: 10px;
    font-size: 18px;
    font-weight: 600;
    text-align: center;
    padding: 6px;
    background: rgba(0,0,0,0.6);
    border-radius: 8px;
    white-space: normal;
    word-wrap: break-word;
    line-height: 1.3;
}}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="header-box">
    <div class="title">Movie Recommender System</div>
    <div class="subtitle">Find movies similar to your favorites</div>
</div>
""", unsafe_allow_html=True)

# ---------- BUTTON + REAL PROGRESS ----------
progress_bar_placeholder = st.empty()
progress_text_placeholder = st.empty()

col1, col2, col3 = st.columns([2,1,2])
with col2:
    if st.button("Get Recommendations"):

        bar = progress_bar_placeholder.progress(0)

        progress_text_placeholder.markdown(
            "<div style='text-align:center; color:white;'>Starting...</div>",
            unsafe_allow_html=True
        )

        names, posters = recommend(
            selected_movie,
            bar,
            progress_text_placeholder
        )

        st.session_state.recommendations = (names, posters)

        # Clear loader
        progress_bar_placeholder.empty()
        progress_text_placeholder.empty()

# ---------- DISPLAY ----------
if st.session_state.recommendations:
    names, posters = st.session_state.recommendations

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{posters[i]}" width="100%">
                    <div class="movie-title">{names[i]}</div>
                </div>
            """, unsafe_allow_html=True)