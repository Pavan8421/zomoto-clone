from django.shortcuts import render
from .models import *
from django.http import JsonResponse
# Create your views here.

def get_restaurant_by_id(request, id):
  try:
    restaurant = Restaurant.objects.prefetch_related('cuisines').get(restaurant_id=id)
    return JsonResponse({
      "status": True,
      "id" : restaurant.restaurant_id,
      "name" : restaurant.name,
      "country_code": restaurant.country_code,
      "city": restaurant.city,
      "address": restaurant.address,
      "locality": restaurant.locality,
      "locality_verbose": restaurant.locality_verbose,
      "longitude": restaurant.longitude,
      "latitude": restaurant.latitude,
      "avg_cost_for_two": restaurant.avg_cost_for_two,
      "currency": restaurant.currency,
      "has_table_booking": restaurant.has_table_booking,
      "has_online_delivery": restaurant.has_online_delivery,
      "is_delivering": restaurant.is_delivering,
      "price_range": restaurant.price_range,
      "aggregate_rating": restaurant.aggregate_rating,
      "rating_color": restaurant.rating_color,
      "rating_text": restaurant.rating_text,
      "votes": restaurant.votes,
      "image_url": restaurant.image_url,
      "cuisines": [cuisine.name for cuisine in restaurant.cuisines.all()]
    }, status = 300)
  except Restaurant.DoesNotExist:
    return JsonResponse({"status" : False, "error": "Restaurant not found"}, status=404)
  except Exception as e:
    return JsonResponse({"status" : False, "error": e}, status = 500)