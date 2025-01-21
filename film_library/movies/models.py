from django.db import models
from datetime import date
from django.urls import reverse
# Импортируем models из django.db, он отвечает за БД
# Create your models here.


# Создаем класс Category, который наследуется от класса Model (из django.db)
class Category(models.Model):
    """Категории"""
    # Описываем поля, они же столбцы в таблице
    # Пишем атрибуты класса(экземпляры класса полей)

    name = models.CharField('Категория', max_length=150)
    description = models.TextField('Описание')
    # Slug - содердит только цифры, буквы, как раз для URL
    url = models.SlugField(max_length=160, unique=True)

    # Метод str вернет строковое представление нашей модели
    def __str__(self):
        return self.name

    # Класс Meta - просто контейнер класса с некоторыми опциями, метаданными, прикрепленный к нашей модели
    # Он определяет такие вещи: имя связанной таблицы БД, является ли модель абстрактной или нет
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Actor(models.Model):
    """Актеры и режиссеры"""
    name = models.CharField('Имя', max_length=100)
    age = models.PositiveSmallIntegerField('Возраст', default=0)
    description = models.TextField('Описание')
    image = models.ImageField('Изобраение', upload_to='actors/')
    # Проверяет является ли загруженный объект допустим изображением
    # Указываем директорию, куда будем загружать изображение

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Актеры и режиссеры"
        verbose_name_plural = "Актеры и режиссеры"


class Genre(models.Model):
    """Жанры"""
    name = models.CharField("Имя", max_length=100)
    description = models.TextField("Описание")
    url = models.SlugField(max_length=160, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Movie(models.Model):
    """Фильм"""
    title = models.CharField('Название', max_length=100)
    tagline = models.CharField('Слоган', max_length=100, default='')
    description = models.TextField("Описание")
    poster = models.ImageField('Постер', upload_to='movies/')
    year = models.PositiveSmallIntegerField('Дата выхода', default=2019)
    country = models.CharField('Страна', max_length=30)
    directors = models.ManyToManyField(
        # verbose_name - явно передаем имя для поля
        # related_name - имя, используемое для отношения от связываемого объекта
        Actor, verbose_name="режиссер", related_name="film_director"
    )
    actors = models.ManyToManyField(
        Actor, verbose_name='актеры', related_name='film_actor'
    )
    genres = models.ManyToManyField(Genre, verbose_name='жанры')
    world_premiere = models.DateField("Премьера в мире", default=date.today)
    budget = models.PositiveIntegerField("Бюджет", default=0,
                                         help_text="указывать сумму в долларах")
    fees_in_usa = models.PositiveIntegerField(
        "Сборы в США", default=0, help_text="указывать сумму в долларах"
    )
    fess_in_world = models.PositiveIntegerField(
        "Сборы в мире", default=0, help_text="указывать сумму в долларах"
    )
    category = models.ForeignKey(
        # Отношение многие к одному
        # В таблице фильмы - ОДНО id категории
        # В таблице Category несколько id, связываем
        Category, verbose_name="Категория", on_delete=models.SET_NULL, null=True
        # Обязательно делаем аргумент on_delete,
        # Он указывает что будет происходит при удалении связанной записи
        # Если мы удалим категорию из таблицы Category - данное поле станет NULL
    )
    url = models.SlugField(max_length=130, unique=True)
    draft = models.BooleanField("Черновик", default=False)

    def __str__(self):
        return self.title

# Отошел в магазин, 7 урок, момент, где он добавляет метод для перехода на сайт
    def get_absolute_url(self):
        # В методе reverse передаем имя нашего URL
        # И в словаре передать параметры, которые мы передаем url
        # Таким образом django передаст нужный нам URL
        return reverse("movie_detail", kwargs={"slug": self.url})

    def get_review(self):
        return self.reviews_set.filter(parent__isnull=True)

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"


class MovieShots(models.Model):
    """Кадры из фильма"""
    title = models.CharField("Заголовок", max_length=100)
    description = models.TextField("Описание")
    image = models.ImageField("Изображение", upload_to="movie_shots/")
    movie = models.ForeignKey(
        Movie, verbose_name="Фильм", on_delete=models.CASCADE)
    # models.CASCADE - при удалении фильма все связанные кадры тоже удалятся

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Кадр из фильма"
        verbose_name_plural = "Кадры из фильма"


class RatingStar(models.Model):
    """Звезда рейтинга"""
    value = models.SmallIntegerField("Значение", default=0)

    def __str__(self):
        return f'{self.value}'

    class Meta:
        verbose_name = "Звезда рейтинга"
        verbose_name_plural = "Звезды рейтинга"


class Rating(models.Model):
    """Рейтинг"""
    ip = models.CharField("IP адрес", max_length=15)
    star = models.ForeignKey(
        # Привязка с помощью Foreign Key к звезде рейтинга, которую выбрал пользователь
        RatingStar, on_delete=models.CASCADE, verbose_name="звезда"
    )
    movie = models.ForeignKey(
        # Привязка с помощью Foreign Key к фильму
        Movie, on_delete=models.CASCADE, verbose_name="фильм", related_name="ratings"
    )
    # Таким образом мы знаем кто, к какому фильму какую звезду поставил

    def __str__(self):
        return f"{self.star} - {self.movie}"

    class Meta:
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"


class Reviews(models.Model):
    """Отзывы"""
    email = models.EmailField()
    name = models.CharField("Имя", max_length=100)
    text = models.TextField("Сообщение", max_length=5000)
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    # movie - это атрибут, через который идет привязка к фильму
    movie = models.ForeignKey(
        Movie, verbose_name="фильм", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.movie}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
