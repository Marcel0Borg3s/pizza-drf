from rest_framework.exceptions import APIException


class PizzaInUseError(APIException):
    """409 when a pizza still has reviews and cannot be deleted."""

    status_code = 409
    default_detail = "Esta pizza já possui avaliações e não pode ser excluída."
    default_code = "pizza_in_use"
