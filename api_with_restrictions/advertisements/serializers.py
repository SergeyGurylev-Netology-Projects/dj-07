from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework import serializers

from advertisements.models import Advertisement

MAX_ADS_COUNT = 10


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator', 'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        # TODO: добавьте требуемую валидацию
        method = self.context["request"].method
        if method in ['POST', 'PATCH'] and data.get('status', {'POST': 'OPEN', 'PATCH': ''}[method]) == 'OPEN':
            if Advertisement.objects.filter(creator=self.context["request"].user, status='OPEN').count() >= MAX_ADS_COUNT:
                raise ValidationError('Too many ads')

        return data
