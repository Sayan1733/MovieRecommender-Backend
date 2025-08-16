from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import requests
import os
import gdown
app = Flask(__name__)
CORS(app)

# Load movies & similarity

movie_file = "movies.pkl"
if not os.path.exists(movie_file):
    url = "https://drive.google.com/uc?id=1HJXCa7frc4zPkJQgUw0wbcdWQ4JA_L3b"  # replace with actual FILE_ID
    gdown.download(url, movie_file, quiet=False)

with open(movie_file, "rb") as f:
    movies = pickle.load(f)

# Similarity PKL
similarity_file = "similarity.pkl"
if not os.path.exists(similarity_file):
    url = "https://drive.google.com/uc?id=1OWWhhJl0nOQ3GGunNLG2SMLF0QoAOnMJ"
    gdown.download(url, similarity_file, quiet=False)

with open(similarity_file, "rb") as f:
    similarity = pickle.load(f)
# TMDB poster fetch function
def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=19b14193a2190d4e4e34415ee90f6fbc&language=en-US"
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500" + data['poster_path']

# Recommendation function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommendations = []
    for idx, i in enumerate(movies_list, start=1):
        movie_id = movies.iloc[i[0]].movie_id
        recommendations.append({
            "number": idx,  # 1, 2, 3, 4, 5
            "title": movies.iloc[i[0]].title,
            "poster_url": fetch_poster(movie_id)
        })
    return recommendations

@app.route('/recommend', methods=['GET', 'POST'])
def recommend_route():
    if request.method == 'GET':
        movie_name = request.args.get('movie')
    else:
        movie_name = request.json.get('movie')

    if not movie_name:
        return jsonify({"error": "No movie name provided"}), 400

    try:
        results = recommend(movie_name)
        return jsonify({"recommendations": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

