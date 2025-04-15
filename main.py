import streamlit as st
import pickle as pkl
import pandas as pd
import requests
import os
from auth import login, signup

# Ensure users.json exists and is valid
if not os.path.exists("users.json"):
    with open("users.json", "w") as file:
        file.write("{}")  # Write an empty JSON object

# Load image
image_path = "/Users/dastagira/Desktop/3RD Yr PROJECT /Movies-Recommender-system/Netflix Sits At 231 Million Subscribers_.jpeg"
if os.path.exists(image_path):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(image_path, use_container_width=True)
else:
    st.error(f"Image path {image_path} is not available")

# Function to fetch movie posters and links
def fetch_posters_and_links(movie_id):
    api_key = "7e4ab0a38e62584f95638cf72d5ca6d5"  # Replace with your actual API key
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=7e4ab0a38e62584f95638cf72d5ca6d5&language=en-US")
    data = response.json()

    poster_path = None
    movie_link = None

    if 'poster_path' in data and data['poster_path']:
        poster_path = "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    if 'id' in data:
        movie_link = f"https://www.themoviedb.org/movie/{data['id']}"

    return poster_path, movie_link

# Function to recommend movies
def recommend(movie, slider):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        m_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:slider + 1]

        recommended_movie_id = []
        recommended_movie_poster = []
        recommended_movie_name = []
        recommended_movie_links = []
        for i in m_list:
            movie_id = movies.iloc[i[0]].id
            movie_name = movies.iloc[i[0]].title
            recommended_movie_id.append(movie_id)
            recommended_movie_name.append(movie_name)
            # Fetch posters and links from API
            poster_path, movie_link = fetch_posters_and_links(movie_id)
            recommended_movie_poster.append(poster_path)
            recommended_movie_links.append(movie_link)

        return recommended_movie_id, recommended_movie_name, recommended_movie_poster, recommended_movie_links
    except Exception as e:
        st.error(f"Error in recommendation: {e}")
        return [], [], [], []

# Load data
movies_dict = pkl.load(open('/Users/dastagira/Desktop/3RD Yr PROJECT /Movies-Recommender-system/movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pkl.load(open('/Users/dastagira/Desktop/3RD Yr PROJECT /Movies-Recommender-system/similarity.pkl', 'rb'))

# Initialize session state for authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "signup_mode" not in st.session_state:
    st.session_state.signup_mode = False

# Sidebar for login/signup
st.sidebar.title("Login or Sign Up")

if not st.session_state.logged_in:
    if st.session_state.signup_mode:
        # Signup form
        st.sidebar.subheader("Sign Up")
        signup_email = st.sidebar.text_input("Email Address (Sign Up)")
        signup_password = st.sidebar.text_input("Password (Sign Up)", type="password")
        if st.sidebar.button("Sign Up"):
            success, message = signup(signup_email, signup_password)
            if success:
                st.sidebar.success(message)
                st.session_state.signup_mode = False  # Switch back to login
            else:
                st.sidebar.error(message)
        if st.sidebar.button("Back to Login"):
            st.session_state.signup_mode = False
    else:
        # Login form
        st.sidebar.subheader("Login")
        login_email = st.sidebar.text_input("Email Address (Login)")
        login_password = st.sidebar.text_input("Password (Login)", type="password")
        if st.sidebar.button("Login"):
            success, message = login(login_email, login_password)
            if success:
                st.session_state.logged_in = True
                st.sidebar.success(message)
            else:
                st.sidebar.error(message)
        if st.sidebar.button("Sign Up Instead"):
            st.session_state.signup_mode = True

# Main app (only accessible if logged in)
if st.session_state.logged_in:
    st.title('Movie Recommender System')

    selected_movie_name = st.selectbox(
        'Which type of Movies would you like to watch !?', (movies['title'].values)
    )

    slider = st.slider("Select How many Movies you want !", 1, 20)

    if st.button('Recommend'):
        id, names, posters, links = recommend(selected_movie_name, slider)

        if len(names) == 0:
            st.error("No recommendations found. Please try another movie.")
        else:
            # Display recommendations in a grid format
            cols_per_row = 5  # Number of columns per row
            num_rows = (len(names) + cols_per_row - 1) // cols_per_row  # Calculate number of rows

            for row in range(num_rows):
                cols = st.columns(cols_per_row)  # Create columns for each row
                for col in range(cols_per_row):
                    index = row * cols_per_row + col
                    if index < len(names):  # Ensure we don't exceed the number of recommendations
                        with cols[col]:
                            st.markdown(f"**{names[index]}**")  # Display movie name
                            if posters[index] and links[index]:  # Check if poster and link are available
                                st.markdown(
                                    f'<a href="{links[index]}"><img src="{posters[index]}" width="100%"></a>',
                                    unsafe_allow_html=True
                                )
                            elif posters[index]:  # If only poster is available
                                st.image(posters[index], use_container_width=True)
                            else:  # If no poster is available
                                st.markdown("🎬 **Poster not available**")
else:
    st.warning("Please log in or sign up to access the movie recommender.")