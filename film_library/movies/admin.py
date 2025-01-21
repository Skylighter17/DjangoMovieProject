from django.contrib import admin
from django.utils.safestring import mark_safe
from django import forms

from .models import Category, Genre, Movie, MovieShots, Actor, Rating, RatingStar, Reviews

from ckeditor_uploader.widgets import CKEditorUploadingWidget

# Добавлям форму из ckeditor, чтобы у нас был больший функционал в редактировании описани
# И даже добавление видео из Ютуба за счет дополнительного виджета Youtube!


class MovieAdminForm(forms.ModelForm):
    description = forms.CharField(label='Описание', widget=CKEditorUploadingWidget())

    class Meta:
        model = Movie
        fields = '__all__'

# Регистрируем наше поле Category с помощью декоратора


@admin.register(Category)
# С помощью этого класса в админке у нас будут отображаться в таблице поля имя, айди, url, что удобно!
class CategoryAdmin(admin.ModelAdmin):
    """Категории"""
    list_display = ('id', 'name', 'url')
    # С помозью link ставим гиперссылку на str фильмы, а не на id, как было до этого
    list_display_links = ('name',)  # Обязательно должно быть tuple, иначе ошибка


# Добавим класс для того, чтобы при заходе в карточку фильма отображались кадры из фильма
class MovieShotsInline(admin.TabularInline):
    model = MovieShots
    extra = 1
    readonly_fields = ('get_image',)

    def get_image(self, obj):
        return mark_safe(f"<img src={obj.image.url} width='100' height='110'>")

    get_image.short_description = 'Изображение'


# Класс для отображения отзывов при заходе в карточку фильма
# До этого было Stacked inline - просто вертикально, сейчас в виде таблицы
class ReviewInlines(admin.TabularInline):
    model = Reviews
    extra = 1  # Количество пустых отзывов
    readonly_fields = ('name', 'email')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Фильмы"""
    list_display = ('title', 'category', 'url', 'draft')
    list_filter = ('category', 'year')

    # С помощью __name указываем, что изем именно по имени категории, а не по какому-нибудь url
    search_fields = ('title', 'category__name')
    inlines = [MovieShotsInline, ReviewInlines]

    # Перенесем меню сохранения фильма вверх, чтобы не листать вниз, т.к. много отзывов
    save_on_top = True

    # Если есть заготовка для фильма, можно сделать сохранение как нового объекта
    save_as = True

    # Сделаем так, чтобы можно было редактировать поле "Черновик" прямо из списка
    list_editable = ('draft',)

    # Добавляем actions
    actions = ['publish', 'unpublish']

    # Указываем форму из ckeditor
    form = MovieAdminForm

    # Режиссеры, актеры и жанры сделаем в одну строку
    # fields = (('actors', 'directors', 'genres'),)
    # Или так
    readonly_fields = ('get_image',)

    fieldsets = (
        ('Название и заголовок', {
            'fields': (('title', 'tagline'),)
        }),
        ('Постер и описание', {
            'fields': ('description', 'poster', 'get_image'),
            'classes': ('wide',),
        }),
        (None, {
            'fields': (('year', 'world_premiere', 'country'),)
        }),
        ('Актеры, режиссеры, жанры и категории', {
            'fields': ('actors', 'directors', 'genres', 'category')
        }),
        ('Бюджет и сборы', {
            'fields': (('budget', 'fees_in_usa', 'fess_in_world'),)
        }),
        ('Options', {
            'fields': (('url', 'draft'),)
        }),

    )
    # Но у меня не работает :(

    def get_image(self, obj):
        return mark_safe(f"<img src={obj.poster.url} width='50' height='60'>")
    get_image.short_description = ('Постер')

    # С помощью этих методов у нас появляются действия прямо в административной панели
    # Мы можем выбрать фильмы и опубликовать/снять с публикации
    def unpublish(self, request, queryset):
        """Снять с публикации"""
        row_update = queryset.update(draft=True)
        if row_update == 1:
            message_bit = '1 запись была обновлена'
        else:
            message_bit = f'{row_update} записей были обновлены'
        self.message_user(request, f'{message_bit}')
    unpublish.short_description = 'Снять с публикации'
    unpublish.allowed_permissions = ('change', )

    def publish(self, request, queryset):
        """Опубликовать"""
        row_update = queryset.update(draft=False)
        if row_update == 1:
            message_bit = '1 запись была обновлена'
        else:
            message_bit = f'{row_update} записей были обновлены'
        self.message_user(request, f'{message_bit}')
    publish.short_description = 'Опубликовать'
    publish.allowed_permissions = ('change', )


@admin.register(Reviews)
class Reviews(admin.ModelAdmin):
    """Отзывы"""
    list_display = ('name', 'email', 'parent', 'movie', 'id')
    # Скрываем от редактирования имя и email пользователя
    readonly_fields = ('name', 'email')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Жанры"""
    list_display = ('name', 'url')


@admin.register(MovieShots)
class MovieShotsAdmin(admin.ModelAdmin):
    """Кадры из фильма"""
    list_display = ('title', 'movie', 'get_image')
    readonly_fields = ('get_image',)

    def get_image(self, obj):
        return mark_safe(f"<img src={obj.image.url} width='50' height='60'>")

    get_image.short_description = 'Изображение'


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'get_image')
    readonly_fields = ('get_image',)

    # Напишем метод, который будет выводить изображения:
    def get_image(self, obj):
        return mark_safe(f"<img src={obj.image.url} width='50' height='60'>")

    get_image.short_description = 'Изображение'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Рейтинг"""
    list_display = ('star', 'movie', 'ip')


# Можно убрать, так как зарегистрировали с помощью декоратора
# admin.site.register(Category, CategoryAdmin)
# admin.site.register(Genre)
# admin.site.register(Movie)
# admin.site.register(MovieShots)
# admin.site.register(Actor)
# admin.site.register(Rating)
admin.site.register(RatingStar)
# admin.site.register(Reviews)

admin.site.site_title = 'Django Movies Админка'
admin.site.site_header = 'Django Movies Админка'
