from django.urls import path
from . import views
urlpatterns = [
    path('restaurant/<int:id>/', views.get_restaurant_by_id, name = 'get_restaurant_by_id')
]
