import os
import tempfile
from django.shortcuts import render
from .models import *
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .clipmodel_predict import *
from django.db.models import Q
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.test import RequestFactory
from django.urls import reverse
from django.urls import resolve
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


def build_page_url(request, page, page_size, restaurant_id = -1, latitude = -1, longitude = -1,radius = -1, cuisine = None):
    #base_url = request.build_absolute_uri(reverse('get_restaurants_with_pagination'))
    base_url = "http://127.0.0.1:8000/api/restaurants/"
    query_params = f"page={page}&page_size={page_size}"
    
    if restaurant_id != -1:
        query_params += f"&restaurant_id={restaurant_id}"
    
    if latitude != -1 and longitude != -1:
        query_params += f"&latitude={latitude}&longitude={longitude}&radius={radius}"

    if cuisine:
        query_params += f"&cuisine={cuisine}"

    return f"{base_url}?{query_params}"

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

def get_restaurants_with_pagination(request):
  
  try:
    page_number = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    restaurant_id = int(request.GET.get('restaurant_id', -1))
    latitude = float(request.GET.get('latitude', -1))
    longitude = float(request.GET.get('longitude', -1))
    radius = float(request.GET.get('radius', -1)) 
    cuisine = request.GET.get('cuisine', None)
  
  except ValueError:
    return JsonResponse({
      'status': False,
      'error' : 'Invalid page or page-size parameter. Must be integers.'
    }, status = 400)

  query = Q()
  if restaurant_id != -1:
    query &= Q(restaurant_id=restaurant_id)

  if cuisine:
        query &= Q(cuisines__name__iexact=cuisine)

  restaurants = Restaurant.objects.prefetch_related('cuisines').filter(query)


  if latitude != -1 and longitude != -1 and radius > 0.0:

    nearby_restaurants = []
    for restaurant in restaurants:
      distance = calculate_distance(latitude, longitude, restaurant.latitude, restaurant.longitude)
      #print(distance)
      if distance <= radius:
        nearby_restaurants.append(restaurant)
    restaurants = nearby_restaurants
    

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
      'previous_page': build_page_url(request, page_obj.previous_page_number(), page_size, restaurant_id, latitude, longitude, radius, cuisine) if page_obj.has_previous() else None,
      'next_page': build_page_url(request, page_obj.next_page_number(), page_size, restaurant_id, latitude, longitude, radius, cuisine) if page_obj.has_next() else None,
      'restaurants': restaurant_list,  # List of restaurants
  }
  #print(response)
  return JsonResponse(response)




@csrf_exempt
def search_restaurants_by_image(request):
  if request.method == "POST" and request.FILES.get('image'):
    uploaded_image = request.FILES['image']
    # Validate file extension
    valid_extensions = ['jpg', 'png', 'jpeg']
    file_extension = uploaded_image.name.split('.')[-1].lower()
    if file_extension not in valid_extensions:
        return JsonResponse({
                              'status' : False,
                              'error' : 'Wrong file format image uploaded.'
                            }, status = 400)
    
    # Specify a custom directory for temporary files
    custom_temp_dir = "./"
    if not os.path.exists(custom_temp_dir):
        os.makedirs(custom_temp_dir)

    # Save the uploaded image as a temporary file in the custom directory
    with tempfile.NamedTemporaryFile(delete=False, dir=custom_temp_dir, suffix=f".{file_extension}") as temp_file:
        for chunk in uploaded_image.chunks():
            temp_file.write(chunk)
        temp_image_path = temp_file.name

    try:
      # Process the temporary image file
      predicted_cuisine = classify_cuisine(temp_image_path)
    finally:
      # Clean up the temporary file
      os.remove(temp_image_path)

    return JsonResponse({
      'status': True,
      'cuisine': predicted_cuisine,
      'message': "Cuisine found successfully",
    }, status = 200)


