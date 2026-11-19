import uuid

from rest_framework import generics

from reviews.models import Review
from reviews.serializers import ReviewSerializer


class ReviewCreatListView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        """List reviews, newest first, optionally filtered by ``?pizza=<uuid>``."""
        queryset = Review.objects.select_related("pizza").order_by("-created_at")
        pizza = self.request.query_params.get("pizza")
        if not pizza:
            return queryset
        try:
            pizza_id = uuid.UUID(str(pizza))
        except (ValueError, TypeError):
            return queryset.none()
        return queryset.filter(pizza_id=pizza_id)


class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
