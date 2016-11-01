from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search_movies/$', views.search_movies),
    url(r'^rate_movie/$', views.rate_movie),
    url(r'^clear_ratings/$', views.clear_ratings),
    url(r'^get_recommendations/$', views.get_recommendations),
]
