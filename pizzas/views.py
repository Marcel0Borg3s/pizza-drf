from rest_framework import generics
from pizzas.models import Pizza
from pizzas.serializers import PizzaSerializer


class PizzaCreateListView(generics.ListCreateAPIView):
    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer

class PizzaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer
