from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import redis
import pandas as pd
import graphlab
import json

r = redis.StrictRedis(host='localhost', port=6379, db=0)


# Create your views here.
def index(request):
    return HttpResponse('Hello, world. You\'re at the machine-learning index.')


@csrf_exempt
def search_movies(request):
    query = request.POST['query'].split()
    terms = []
    for term in query:
        terms += [term.lower()]
        terms += [term.title()]
    movies = pd.read_json(get_movie_data())
    data = movies[movies['movie_title'].str.contains('|'.join(terms))][['movie_id', 'movie_title', 'imdb_url']].reset_index().to_json(orient='records')
    return JsonResponse(json.loads(data), safe=False)


@csrf_exempt
def rate_movie(request):
    params = request.POST
    r.hset('ratings', params['movie_id'], params['rating'])
    return JsonResponse({'success': True})


@csrf_exempt
def clear_ratings(request):
    ratings = r.hgetall('ratings')
    for key, _ in ratings.iteritems():
        r.hdel('ratings', key)
    return JsonResponse({'success': True})


@csrf_exempt
def get_recommendations(request):
    ratings = r.hgetall('ratings')
    stored_ratings = pd.read_json(get_stored_rating_data())
    # not important
    user_id, timestamp = 0, 0
    for movie_id, rating in ratings.iteritems():
        rating_df = pd.DataFrame(
            [[user_id, int(movie_id), int(rating), timestamp]],
            columns=['user_id', 'movie_id', 'rating', 'unix_timestamp']
        )
        stored_ratings = stored_ratings.append(rating_df)
    train_data = graphlab.SFrame(stored_ratings)
    item_sim_model = graphlab.item_similarity_recommender.\
            create(train_data, user_id='user_id', item_id='movie_id',
                   target='rating', similarity_type='cosine')
    item_sim_recomm = item_sim_model.recommend(users=[0], k=10)
    movie_ids = list(item_sim_recomm['movie_id'])
    movies = pd.read_json(get_movie_data())
    data = movies[movies['movie_id'].isin(movie_ids)][['movie_id', 'movie_title', 'imdb_url']].reset_index().to_json(orient='records')
    return JsonResponse(json.loads(data), safe=False)


def get_movie_data():
    movies = r.get('movies')
    if movies:
        return movies
    i_cols = ['movie_id', 'movie_title', 'release_date', 'video_release_date',
              'imdb_url', 'unknown', 'Action', 'Adventure', 'Animation',
              'Children\'s', 'Comedy', 'Crime', 'Documentary', 'Drama',
              'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery',
              'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
              ]
    movies = pd.read_csv('ml-100k/u.item', sep='|', names=i_cols,
                         encoding='latin-1').reset_index().to_json(orient='records')
    r.set('movies', movies)
    return movies


def get_stored_rating_data():
    ratings = r.get('stored_ratings')
    if ratings:
        return ratings
    r_cols = ['user_id', 'movie_id', 'rating', 'unix_timestamp']
    ratings = pd.read_csv('ml-100k/u.data', sep='\t', names=r_cols,
                          encoding='latin-1').reset_index().to_json(orient='records')
    r.set('stored_ratings', ratings)
    return ratings
