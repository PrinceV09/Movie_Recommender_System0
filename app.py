import streamlit as st
import pickle
import requests

# ------------------ LOAD DATA ------------------
movies = pickle.load(open('movies.pkl', 'rb'))   # DataFrame with movie_id, title, tags
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ------------------ TMDB API KEY ------------------
API_KEY = st.secrets["TMDB_API_KEY"]


# ------------------ FETCH POSTER ------------------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "language": "en-US"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        if response.status_code != 200:
            return None

        data = response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        return None

    except requests.exceptions.RequestException:
        return None

# ------------------ RECOMMEND FUNCTION ------------------
def recommend(movie_name):
    if movie_name not in movies['title'].values:
        return [], []

    movie_index = movies[movies['title'] == movie_name].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

# ------------------ STREAMLIT UI ------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie:",
    movies['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            if poster:
                st.image(poster)
            else:
                st.write("Poster not available")