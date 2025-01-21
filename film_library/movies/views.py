from django.urls import reverse_lazy
from django import forms
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import Q
from django.http import HttpResponse

from .forms import ReviewForm, RatingForm


# Create your views here.

from .models import Movie, Actor, Genre, Rating, Category


class CategorySearch(ListView):
    def category_view(request, category_id):
        category = get_object_or_404(Category, id=category_id)
        movies = Movie.objects.filter(category=category)
        return render(request, 'movie_list.html', {'category': category, 'movies': movies})
    model = Movie
    template_name = 'movies/movie_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.kwargs.get('category_id')
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        return queryset


class GenreYear():
    """Жанры и года выхода фильмов"""

    # Получение всех жанров
    def get_genres(self):
        return Genre.objects.all()

    # Получение всех фильмов, которые НЕ черновики
    def get_years(self):
        return Movie.objects.filter(draft=False).values('year')

# # Создаем класс MoviesView и наследуемся от класса Django View
# class MoviesView(View):
#     """Список фильмов"""
#     # Создаем метод get, он будет принимать get запросы HTTP
#     # Этот метод принимает request
#     # request - это вся информация, присланная от клиента(браузера)

#     def get(self, request):
#         # objects - метод, который идет по умолчанию, он забирает все записи
#         # Затем querry-set мы сохраняем в переменную movies
#         movies = Movie.objects.all()
#         # Возвращаем render, который передает: request,
#         # Ссылку на наш шаблон html,
#         # И контекст
#         # Контекст - это словарь
#         return render(request,
#                       'movies/movies.html',
#                       {'movie_list': movies})


# class MovieDetailView(View):
#     """Полное описание фильма"""

#     def get(self, request, slug):
#         # pk - это некое число, которое мы передаем из url
#         # А вообще по хорошему это Primary Key)))
#         movie = Movie.objects.get(url=slug)  # Запрос в БД, до этого было id = pk
#         return render(request, "movies/movie_detail.html", {"movie": movie})

# Перепишем классы Django с View на более интересные - ListView и DetailView


class MoviesView(GenreYear, ListView):
    """Список фильмов"""
    # В данном классе мы указываем модель - Movie
    model = Movie
    # Используем не all, а фильтр , чтобы отсортировать те, которые не отмечены черновиком
    queryset = Movie.objects.filter(draft=False)
    # Адрес к нашему таблону
    # template_name = 'movies/movies.html'
    # Указываем template, так как наш шаблон называется movies.html
    # А Django по стандарту будет искать movie(имя модели)_list
    # UPD - переименовано
    paginate_by = 6


class MovieDetailView(GenreYear, DetailView):
    """Полное описание фильма"""
    model = Movie
    slug_field = 'url'
    # В данном классе мы не указывали template name, так как
    # Django автоматически поставляет суффикс к нашему шаблону
    # Он будет искать шаблон movie_detail
    # Добавляем метод для отображения категорий справа сверху

    # Добавляем форму рейтинга
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем к словарю еще один форм и значение заносим в нашу форму RatingForm
        context['star_form'] = RatingForm()
        return context


class AddReview(View):
    """Отзывы"""
    # В данном классе используем метод post. Это будет POST запроса HTTP
    # Принимаем request
    # pk - будет наш id фильма

    def post(self, request, pk):
        # Посмотрим в консоле, что приходит к нам в POSt запросе
        # # print(request.POST)
        form = ReviewForm(request.POST)
        movie = Movie.objects.get(id=pk)
        if form.is_valid():  # Проверяем форму на валидность
            form = form.save(commit=False)
            # Добавляем возможность ответа на коммент
            # В нашем POST запросе будем искать ключ parent
            # Ключ parent - это имя нашего поля
            if request.POST.get('parent', None):
                form.parent_id = int(request.POST.get('parent'))
            form.movie = movie
            form.save()
        # При отправке отзыва будет переправлять нашего пользователя на главную страницу
        # UPD . Добавили метод из модели movie, который отвечает за перенаправление на ту же страницу,
        # куда и добавляли отзыв
        return redirect(movie.get_absolute_url())

        # Добавляем класс, который будет отображать информациб об актерах


class ActorView(GenreYear, DetailView):
    '''Вывод информации об актере/режиссере'''
    model = Actor
    template_name = 'movies/actor.html'
    slug_field = 'name'


class FilterMoviesView(GenreYear, ListView):
    """Фильтр фильмов"""
    # Вызывая данный метод мы будет фильтровать Movie,там где
    # года(year_in) будут входить в список, который будет нам возвращаться с фронтенда
    # Это список наших годов. С помозью getlist будем доставать все значения годов и будем возвращать
    # В данных queryset
    paginate_by = 1

    def get_queryset(self):
        queryset = Movie.objects.filter(
            Q(year__in=self.request.GET.getlist('year')) |
            Q(genres__in=self.request.GET.getlist('genre'))
        )
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["year"] = ''.join([f"year={x}&" for x in self.request.GET.getlist("year")])
        context["genre"] = ''.join([f"genre={x}&" for x in self.request.GET.getlist("genre")])
        return context


class AddStarRating(View):
    """Добавление рейтинга фильму"""

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                movie_id=int(request.POST.get("movie")),
                defaults={'star_id': int(request.POST.get("star"))}
            )
            content = "Ваш голос успешно засчитан! <a href='/'>На главную</a>"
            return HttpResponse(content, status=201)
        else:
            return HttpResponse('Ошибка', status=400)


class Search(ListView):
    """Поиск фильмов"""
    paginate_by = 3

    def get_queryset(self):
        return Movie.objects.filter(title__icontains=self.request.GET.get('q'))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['q'] = f'q={self.request.GET.get("q")}&'
        return context
