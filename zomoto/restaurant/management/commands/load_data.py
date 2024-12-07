import json
from django.core.management.base import BaseCommand
from restaurant.models import Restaurant, Cuisine  

class Command(BaseCommand):
    help = 'Load restaurant and cuisine data from a JSON file'

    def add_arguments(self, parser):
        # Add a command-line argument to accept the JSON file path
        parser.add_argument('file_path', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        # Get the file path from command-line arguments
        file_path = kwargs['file_path']

        try:
            # Open and load the JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)

            # Process each restaurant in the JSON file
            for item in data[0]['restaurants']:
                restaurant_data = item['restaurant']

                # Create or get a Restaurant instance
                restaurant, created = Restaurant.objects.get_or_create(
                    restaurant_id=restaurant_data['R']['res_id'],
                    defaults={
                        'name': restaurant_data['name'],
                        'country_code': restaurant_data['location']['country_id'],
                        'city': restaurant_data['location']['city'],
                        'address': restaurant_data['location']['address'],
                        'locality': restaurant_data['location']['locality'],
                        'locality_verbose': restaurant_data['location']['locality_verbose'],
                        'longitude': float(restaurant_data['location']['longitude']),
                        'latitude': float(restaurant_data['location']['latitude']),
                        'avg_cost_for_two': restaurant_data['average_cost_for_two'],
                        'currency': restaurant_data['currency'],
                        'has_table_booking': bool(restaurant_data['has_table_booking']),
                        'has_online_delivery': bool(restaurant_data['has_online_delivery']),
                        'is_delivering': bool(restaurant_data['is_delivering_now']),
                        'price_range': restaurant_data['price_range'],
                        'aggregate_rating': float(restaurant_data['user_rating']['aggregate_rating']),
                        'rating_color': restaurant_data['user_rating']['rating_color'],
                        'rating_text': restaurant_data['user_rating']['rating_text'],
                        'votes': int(restaurant_data['user_rating']['votes']),
                        'image_url': restaurant_data['featured_image'],
                    }
                )

                # If the restaurant was newly created, add its cuisines
                if created:
                    cuisines = restaurant_data['cuisines'].split(', ')
                    for cuisine_name in cuisines:
                        Cuisine.objects.create(name=cuisine_name, restaurant=restaurant)

                self.stdout.write(self.style.SUCCESS(f"Processed restaurant: {restaurant.name}"))

            self.stdout.write(self.style.SUCCESS("Data import completed successfully!"))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR("Invalid JSON file format"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
