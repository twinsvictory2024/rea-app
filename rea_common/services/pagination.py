from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import math


class Pagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)
        current_page = self.page.number

        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': total_pages,
            'current_page': current_page,
            'results': data
        })