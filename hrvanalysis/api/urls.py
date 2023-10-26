from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('users', views.UserView)
router.register('profiles', views.ProfileView)
router.register('subjects', views.SubjectView)
router.register('results', views.ResultView)
router.register('samples', views.SampleView)


urlpatterns = [
    path('', include(router.urls)),
]