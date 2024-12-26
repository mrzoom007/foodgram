from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'

    def get_page_size(self, request):
        try:
            print(int(request.query_params.get(self.page_size_query_param,
                                               self.page_size)))
            return int(request.query_params.get(self.page_size_query_param,
                                                self.page_size))
        except (TypeError, ValueError):
            return self.page_size
