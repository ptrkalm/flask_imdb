from flask import *
from database import session, Movie
from sqlalchemy import or_
from __main__ import app
import json
import requests
import itertools
import os

url = "https://movie-database-imdb-alternative.p.rapidapi.com/"

headers = {
    'x-rapidapi-host': "movie-database-imdb-alternative.p.rapidapi.com",
    'x-rapidapi-key': os.getenv('IMDB_RAPIDAPI_API_KEY')
}


@app.route('/')
def home():
    return redirect("http://127.0.0.1:5000/collection", code=302)


@app.route('/collection')
def collection():
    sort_by = request.args.get('sort_by')
    sort_by = sort_by if sort_by else 'title'

    genres = request.args.get('genres')
    genres = genres.split(',') if genres else []

    collection = session \
        .query(Movie) \
        .filter(
            or_(Movie.genre.contains(genre) for genre in genres)
        ) \
        .order_by(getattr(Movie, sort_by))

    collection = [movie.as_dict() for movie in collection]
    
    return render_template(
        'collection.html',
        collection=collection,
        all_genres=get_all_genres()
    )


def get_all_genres():
    all_genres = session.query(Movie.genre).all()
    all_genres = list(itertools.chain(*all_genres))
    all_genres = [genres.split(', ') for genres in all_genres]
    all_genres = [genre for genres in all_genres for genre in genres]
    all_genres = sorted(set(all_genres))
    return all_genres


@app.route('/collection/<id>', methods=['GET', 'POST', 'DELETE', 'UPDATE'])
def collection_entry(id):
    if request.method == 'GET':
        return get_collection_entry(id)

    if request.method == 'POST':
        return post_collection_entry(id)

    if request.method == 'UPDATE':
        return update_collection_entry(id)

    if request.method == 'DELETE':
        return delete_collection_entry(id)

    return Response(status=405)


def get_collection_entry(id):
    movie = session.query(Movie).filter(Movie.imdbId == id).first()
    movie_info = {
        "inCollection": bool(movie),
        "myRating": movie.myRating if movie else None
    }
    return jsonify(movie_info)


def post_collection_entry(id):
    data = request.json
    movie = Movie(
        imdbId=id,
        title=data['title'],
        year=int(data['year']),
        genre=data['genre'],
        imdbRating=float(data['imdbRating']),
        poster=data['poster'],
        myRating=data['myRating']
    )
    session.add(movie)
    session.commit()

    return Response(status=200)


def update_collection_entry(id):
    data = request.json
    movie = session \
        .query(Movie) \
        .filter(Movie.imdbId == id) \
        .first()

    if (not movie):
        session.commit()
        return Response(status=309)

    movie.myRating = data['myRating']
    session.commit()

    return Response(status=200)


def delete_collection_entry(id):
    movie = session \
        .query(Movie) \
        .filter(Movie.imdbId == id) \
        .first()
    if (movie):
        session.delete(movie)
    session.commit()

    return Response(status=200)


@app.route('/movie/<id>')
def movie(id):
    movie = requests.get(
        url,
        headers=headers,
        params={'i': id}
    ).json()

    collected_movie = session \
        .query(Movie) \
        .filter(Movie.imdbId == id) \
        .first()

    collected_movie = {
        "myRating": collected_movie.myRating
    } if collected_movie else None

    return render_template(
        'movie.html',
        movie=movie,
        collected_movie=collected_movie
    )


@app.route('/search/')
@app.route('/search/<query>')
def search(query=None):
    page = request.args.get('page')
    response = requests.get(
        url,
        headers=headers,
        params={'s': query, 'type': 'movie', 'page': page}
    ).json()
    movies = []
    results = 0
    if (response["Response"] == "True"):
        movies = response['Search']
        results = int(response['totalResults'])

    for movie in movies:
        collected_movie = session \
            .query(Movie) \
            .filter(Movie.imdbId == movie['imdbID']) \
            .first()

        movie['inMyCollection'] = True if collected_movie else False

    return render_template(
        'search.html',
        movies=movies,
        results=results
    )
