from django.shortcuts import render
from .models import *
from django.http import JsonResponse

from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.urls import reverse
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


def get_restaurants_with_pagination(request):

  try:
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
  
  except ValueError:
    return JsonResponse({
      'status': False,
      'error' : 'Invalid page or page-size parameter. Must be integers.'
    }, status = 400)

  restaurants = Restaurant.objects.prefetch_related('cuisines').all()

  paginator = Paginator(restaurants, page_size)
  try:
    page_obj = paginator.page(page_number)

  except PageNotAnInteger:
    return JsonResponse({
      'status' : False,
      'error' : 'Page number is not an integer.'
    }, status = 400)
  
  except EmptyPage:
    return JsonResponse({
      'status': False,
      'error' : 'Page number is out of range'
    }, status = 404)
  restaurant_list = []
  for restaurant in page_obj.object_list:
      restaurant_list.append({
          'restaurant_id': restaurant.restaurant_id,
          'name': restaurant.name,
          'country_code': restaurant.country_code,
          'city': restaurant.city,
          'address': restaurant.address,
          'locality': restaurant.locality,
          'locality_verbose': restaurant.locality_verbose,
          'longitude': restaurant.longitude,
          'latitude': restaurant.latitude,
          'avg_cost_for_two': restaurant.avg_cost_for_two,
          'currency': restaurant.currency,
          'has_table_booking': restaurant.has_table_booking,
          'has_online_delivery': restaurant.has_online_delivery,
          'is_delivering': restaurant.is_delivering,
          'price_range': restaurant.price_range,
          'aggregate_rating': restaurant.aggregate_rating,
          'rating_color': restaurant.rating_color,
          'cuisines' : [cuisine.name for cuisine in restaurant.cuisines.all()],
          'rating_text': restaurant.rating_text,
          'votes': restaurant.votes,
          'image_url': restaurant.image_url,
      })
  
  def build_page_url(page):
      base_url = request.build_absolute_uri(reverse('get_restaurants_with_pagination'))
      return f"{base_url}?page={page}&page_size={page_size}"

  # Prepare the paginated response
  response = {
      'status' : True,
      'total_count': paginator.count,  # Total number of restaurants
      'total_pages': paginator.num_pages,  # Total number of pages
      'current_page': page_obj.number,  # Current page number
      'page_size': page_size,  # Number of items per page
      'previous_page': build_page_url(page_obj.previous_page_number()) if page_obj.has_previous() else None,
      'next_page': build_page_url(page_obj.next_page_number()) if page_obj.has_next() else None,
      'restaurants': restaurant_list,  # List of restaurants
  }

  return JsonResponse(response)

