from django.urls import path,include
from rest_framework import routers
from .views import BoardView,Card,CardFileView,CardView,ListView,BoardMemberView,CardMemberView,CardCommentView
from rest_framework_nested.routers import NestedDefaultRouter


router = routers.DefaultRouter()
router.register('board',BoardView,basename='board')

nested_boardmember_router = NestedDefaultRouter(router,'board',lookup='board')
nested_boardmember_router.register('board_member',BoardMemberView,basename='board_member')

nested_list_router = NestedDefaultRouter(router,'board',lookup='board')
nested_list_router.register('list',ListView,basename='list')

nested_card_router = NestedDefaultRouter(nested_list_router,'list',lookup='list')
nested_card_router.register('card',CardView,basename='card')

nested_file_router = NestedDefaultRouter(nested_card_router,'card',lookup='card')
nested_file_router.register('file',CardFileView,basename='file')

nested_comment_router = NestedDefaultRouter(nested_card_router,'card',lookup='card')
nested_comment_router.register('comment',CardCommentView,basename='comment')

nested_member_router = NestedDefaultRouter(nested_card_router,'card',lookup='card')
nested_member_router.register('card_member',CardMemberView,basename='card_member')


urlpatterns = [
    path('',include(router.urls)),
    path('',include(nested_card_router.urls)),
    path('',include(nested_card_router.urls)),
    path('',include(nested_list_router.urls)),
    path('',include(nested_file_router.urls)),
    path('',include(nested_comment_router.urls)),
    path('',include(nested_member_router.urls)),   
    path('',include(nested_boardmember_router.urls)),   
]