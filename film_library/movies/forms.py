from django import forms

from .models import Reviews, Rating, RatingStar


class ReviewForm(forms.ModelForm):
    """Форма отзывов"""
    # В этом классе можно создавать формы так же, как мы и создали в модели
    class Meta:
        model = Reviews
        # Указываем поля, которые хотим видеть в нашей форме:
        fields = ('name', 'email', 'text')
        # Теперь, используя эту форму, мы можем проверить валидность данных, которые приходят со стороны клиента


class RatingForm(forms.ModelForm):
    """Форма добавления рейтинга"""
    star = forms.ModelChoiceField(
        # QuerrySet - забираем все звезды, которые создали
        # widget - то, как представлена форма в html, в нашел случае RadioSelect
        # Можно было сделать или выпадающий список, или checkbox
        queryset=RatingStar.objects.all(), widget=forms.RadioSelect(), empty_label=None
        )

    class Meta:
        model = Rating
        # Чтобы выводить список добавленных нами звезд, мы переопределям star
        fields = ('star', )
