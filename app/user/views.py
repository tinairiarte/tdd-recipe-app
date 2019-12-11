from rest_framework import generics
# from django.shortcuts import render
from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
