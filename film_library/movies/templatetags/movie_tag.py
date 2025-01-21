from django import template
from movies.models import Category, Movie

# Создаем экземпляр Library для регистрации наших template тэгов
register = template.Library()


@register.simple_tag()
def get_categories():
    """Вывод всех категорий справа сверху"""
    return Category.objects.all()


@register.inclusion_tag('movies/tags/last_movie.html')
def get_last_movies(count=5):
    # Из нашей модели movie берем фильмы, отобранные с помощью SQL запроса order by
    # И с помозью среза выбираем последние пять
    movies = Movie.objects.order_by('id')[:count]
    return {'last_movies': movies}
