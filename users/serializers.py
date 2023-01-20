from rest_framework import serializers
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import Role, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class TokenUserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}



class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'password','roles')

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):

        instance.name = validated_data.get(
            'name', instance.name)
        instance.email = validated_data.get(
            'email', instance.email)

        instance.save()
        return instance


class UserSerializerDetailed(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('__all__')

