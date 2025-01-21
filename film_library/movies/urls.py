from django.urls import path

from . import views

urlpatterns = [
    path('', views.MoviesView.as_view()),
    # Принимаем pk как число, int означает - что integer
    # path('<int:pk>/', views.MovieDetailView.as_view())
    # Добавляем фильтр в URL
    # ВАЖНО добавить этот url до MovieDetail, чтобы фильтр не попадал под шаблон поиска нашего фильма по slug
    path('filter/', views.FilterMoviesView.as_view(), name='filter'),
    # Добавление звезд рейтинга
    path('add-rating/', views.AddStarRating.as_view(), name='add_rating'),

    path('category/<int:category_id>/', views.CategorySearch.as_view(), name='category'),
    # дОБАВЛЯЕМ url ПОИСКА
    path('search/', views.Search.as_view(), name='search'),

    # Исправленная версия, чтобы можно было смотреть описание фильма просто забивая его (url) в адрессную строку
    path('<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail'),

    # Здесь мы будем принмать некий primary key
    # У нас будет путь review/pk
    # Используем наш класс AddReview
    # Имя нашего URL будет add_review
    path('review/<int:pk>/', views.AddReview.as_view(), name='add_review'),
    path('actor/<str:slug>/', views.ActorView.as_view(), name='actor_detail'),
]
