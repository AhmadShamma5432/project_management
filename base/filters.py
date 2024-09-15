import django_filters
from django_filters import FilterSet
from .models import CardComment,BoardMember,Card,Board,List

class BoardFilter(django_filters.FilterSet):
    list_name = django_filters.CharFilter(field_name='lists__name',lookup_expr='icontains')
    card_name = django_filters.CharFilter(field_name='lists__cards__name',lookup_expr='icontains')

    class Meta:
        model = Board
        fields = {
            'name': ['icontains'],
            'description': ['icontains'],
            'created_at': ['date', 'gte', 'lte'],
        }

class ListFilter(FilterSet):
    card_name = django_filters.CharFilter(field_name='cards__name',lookup_expr='icontains')
    class Meta:
        model = List
        fields = {
            'name':['icontains'],
            'created_at': ['date','gte','lte']
        }

class CardFilter(FilterSet):
    class Meta:
        model = Card
        fields = {
            'name':['icontains'],
            'starts_Date':['gte'],
            'finish_Date':['lte']
        }

class CardCommentsFilter(FilterSet):
    class Meta:
        model = CardComment
        fields = {
            'text': ['icontains'],
            'date': ['exact','gt','lt']
        }

class BoardMemberFilter(FilterSet):
    class Meta:
        model = BoardMember
        fields = {
            'role' : ['exact']  
        }
