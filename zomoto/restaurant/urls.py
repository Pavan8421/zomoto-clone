from django.urls import path
from . import views
urlpatterns = [
    path('restaurant/<int:id>/', views.get_restaurant_by_id, name = 'get_restaurant_by_id'),
    path('restaurants/',views.get_restaurants_with_pagination, name = 'get_restaurants_with_pagination'),
    path('search-restaurants/', views.search_restaurants_by_distance, name = 'search_restaurants_by_distance'),
    path('search-restaurants-by-image/', views.search_restaurants_by_image, name = 'search_restaurants_by_image'),
]
