import os
import sys
import django
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zomoto.settings')  # Replace with your project settings module
django.setup()

from restaurant.models import Restaurant, Cuisine

def load_data(file_path):
    """
    Load restaurant and cuisine data from a JSON file into the database.
    """
    try:
        # Open and load the JSON file
        with open(file_path, 'r') as file:
            total_data = json.load(file)

        # Iterate over each restaurant entry in the JSON file
        for data in total_data:
            for index, item in enumerate(data['restaurants']):
                try:
                    print(f"Processing entry at index {index}")

                    if 'restaurant' not in item:
                        continue
                    restaurant_data = item['restaurant']

                    # Create or update the Restaurant record
                    restaurant, created = Restaurant.objects.get_or_create(
                        restaurant_id=restaurant_data['R']['res_id'],
                        defaults={
                            'name': restaurant_data.get('name', '')[:200],
                            'country_code': restaurant_data['location'].get('country_id', 0),
                            'city': restaurant_data['location'].get('city', '')[:100],
                            'address': restaurant_data['location'].get('address', ''),
                            'locality': restaurant_data['location'].get('locality', '')[:100],
                            'locality_verbose': restaurant_data['location'].get('locality_verbose', ''),
                            'longitude': float(restaurant_data['location'].get('longitude', 0) or 0),
                            'latitude': float(restaurant_data['location'].get('latitude', 0) or 0),
                            'avg_cost_for_two': restaurant_data.get('average_cost_for_two', 0),
                            'currency': restaurant_data.get('currency', '')[:10],
                            'has_table_booking': bool(restaurant_data.get('has_table_booking', False)),
                            'has_online_delivery': bool(restaurant_data.get('has_online_delivery', False)),
                            'is_delivering': bool(restaurant_data.get('is_delivering_now', False)),
                            'price_range': restaurant_data.get('price_range', 1),
                            'aggregate_rating': float(restaurant_data['user_rating'].get('aggregate_rating', 0) or 0),
                            'rating_color': restaurant_data['user_rating'].get('rating_color', '')[:20],
                            'rating_text': restaurant_data['user_rating'].get('rating_text', '')[:20],
                            'votes': int(restaurant_data['user_rating'].get('votes', 0) or 0),
                            'image_url': restaurant_data.get('featured_image', None),
                        }
                    )

                    # Add cuisines if the restaurant was newly created
                    if created:
                        cuisines = restaurant_data.get('cuisines', '').split(', ')
                        for cuisine_name in cuisines:
                            if cuisine_name:  # Avoid empty cuisine names
                                Cuisine.objects.create(name=cuisine_name[:100], restaurant=restaurant)

                    print(f"Successfully processed: {restaurant.name}")

                except KeyError as e:
                    print(f"KeyError at index {index}: {e}")
                except ValueError as e:
                    print(f"ValueError at index {index}: {e}")
                except Exception as e:
                    print(f"Unexpected error at index {index}: {e}")

        print("Data loading complete.")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON file format")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python load_data.py <file_path>")
    else:
        file_path = sys.argv[1]
        load_data(file_path)
