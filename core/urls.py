from django.urls import include,path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import UserView,UsersView

routers = DefaultRouter()
routers.register('signup',UserViewSet,basename='signup')
routers.register('user',UserView,basename='user')
routers.register('all_users',UsersView,basename='all_users')

urlpatterns = [
    path('',include(routers.urls)),
    path(r'login/',TokenObtainPairView.as_view(),name='login'),
    path(r'refresh_token/',TokenRefreshView.as_view(),name='refresh_token')
]



