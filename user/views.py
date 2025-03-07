from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class HelloWorldView(APIView):

    def post(self, request):
        return Response({"message": "Hello, world!"})