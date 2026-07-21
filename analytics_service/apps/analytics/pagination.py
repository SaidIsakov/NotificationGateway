from rest_framework.pagination import PageNumberPagination


class DailyMetricsPagination(PageNumberPagination):
  page_size = 10
