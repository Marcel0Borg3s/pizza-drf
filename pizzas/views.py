from django.db.models.deletion import ProtectedError
from rest_framework import generics

from pizzas.exceptions import PizzaInUseError
from pizzas.models import Pizza
from pizzas.serializers import PizzaSerializer


class PizzaCreateListView(generics.ListCreateAPIView):
    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer

class PizzaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer

    def perform_destroy(self, instance):
        """Refuse to delete a pizza that already has reviews (keeps history)."""
        try:
            instance.delete()
        except ProtectedError as exc:
            raise PizzaInUseError() from exc
