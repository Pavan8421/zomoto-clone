import os
import tempfile
from django.shortcuts import render
from .models import *
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .clipmodel_predict import *

from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.urls import reverse
from math import radians, cos, sin, sqrt, atan2
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
      "cuisines": [cuisine.name for cuisine in restaurant.cuisines.all()],
    }, status = 200)
  except Restaurant.DoesNotExist:
    return JsonResponse({"status" : False, "error": "Restaurant not found"}, status=404)
  except Exception as e:
    return JsonResponse({"status" : False, "error": e}, status = 500)


def build_page_url(request, page, page_size):
      base_url = request.build_absolute_uri(reverse('get_restaurants_with_pagination'))
      return f"{base_url}?page={page}&page_size={page_size}"

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

  # Prepare the paginated response
  response = {
      'status' : True,
      'total_count': paginator.count,  # Total number of restaurants
      'total_pages': paginator.num_pages,  # Total number of pages
      'current_page': page_obj.number,  # Current page number
      'page_size': page_size,  # Number of items per page
      'previous_page': build_page_url(request, page_obj.previous_page_number(), page_size) if page_obj.has_previous() else None,
      'next_page': build_page_url(request, page_obj.next_page_number(), page_size) if page_obj.has_next() else None,
      'restaurants': restaurant_list,  # List of restaurants
  }

  return JsonResponse(response)


def search_restaurants_by_distance(request):

    def calculate_distance(lat1, lon1, lat2, lon2):
      """
      Calculate the Haversine distance between two points.
      """
      R = 6371  # Earth radius in kilometers
      lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
      dlat = lat2 - lat1
      dlon = lon2 - lon1

      a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
      c = 2 * atan2(sqrt(a), sqrt(1 - a))
      distance = R * c
      return distance

    latitude = float(request.GET.get('latitude', 0))
    longitude = float(request.GET.get('longitude', 0))
    radius = float(request.GET.get('radius', 3))  # Default radius is 3 km
    page_number = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))  # Default page size is 10

    all_restaurants =  Restaurant.objects.prefetch_related('cuisines').all()

    nearby_restaurants = []
    for restaurant in all_restaurants:
      distance = calculate_distance(latitude, longitude, restaurant.latitude, restaurant.longitude)
      if distance <= radius:
        nearby_restaurants.append(restaurant)
    
    paginator = Paginator(nearby_restaurants, page_size)
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

    restaurant_list = [
        {
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
        }
        for restaurant in page_obj.object_list
    ]

    # Prepare the paginated response
    response = {
        'status' : True,
        'total_count': paginator.count,  # Total number of restaurants
        'total_pages': paginator.num_pages,  # Total number of pages
        'current_page': page_obj.number,  # Current page number
        'page_size': page_size,  # Number of items per page
        'previous_page': build_page_url(request, page_obj.previous_page_number(), page_size) if page_obj.has_previous() else None,
        'next_page': build_page_url(request, page_obj.next_page_number(), page_size) if page_obj.has_next() else None,
        'restaurants': restaurant_list,  # List of restaurants
    }

    return JsonResponse(response)
  

@csrf_exempt
def search_restaurants_by_image(request):
  if request.method == "POST" and request.FILES.get('image'):
    print("Request recieved and post method")
    print("Request.Files", request.FILES)
    uploaded_image = request.FILES['image']
    print("Image recieved", uploaded_image.name)
    page_number = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))  # Default page size is 10
    print(1)
    # Validate file extension
    valid_extensions = ['jpg', 'png', 'jpeg']
    file_extension = uploaded_image.name.split('.')[-1].lower()
    if file_extension not in valid_extensions:
        return JsonResponse({
                              'status' : False,
                              'error' : 'Wrong file format image uploaded.'
                            }, status = 400)

    # Specify a custom directory for temporary files
    custom_temp_dir = "E:/projects/zomoto/zomoto/restaurant/"
    if not os.path.exists(custom_temp_dir):
        os.makedirs(custom_temp_dir)

    # Save the uploaded image as a temporary file in the custom directory
    with tempfile.NamedTemporaryFile(delete=False, dir=custom_temp_dir, suffix=f".{file_extension}") as temp_file:
        for chunk in uploaded_image.chunks():
            temp_file.write(chunk)
        temp_image_path = temp_file.name

    try:
      # Process the temporary image file
      cuisine = classify_cuisine(temp_image_path)
    finally:
      # Clean up the temporary file
      os.remove(temp_image_path)

    restaurants = Restaurant.objects.filter(cuisines__name__iexact=cuisine).distinct()

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
    
    restaurant_list = [
      {
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
      }
      for restaurant in page_obj.object_list
    ]

    # Prepare the paginated response
    response = {
        'status' : True,
        'total_count': paginator.count,  # Total number of restaurants
        'total_pages': paginator.num_pages,  # Total number of pages
        'current_page': page_obj.number,  # Current page number
        'page_size': page_size,  # Number of items per page
        'previous_page': build_page_url(request, page_obj.previous_page_number(), page_size) if page_obj.has_previous() else None,
        'next_page': build_page_url(request, page_obj.next_page_number(), page_size) if page_obj.has_next() else None,
        'restaurants': restaurant_list,  # List of restaurants
    }
    print("Returning Response")
    return JsonResponse(response)
  else:
    return JsonResponse({
        'status': False,
        'error' : 'Not required type of request'
    },status = 400)
