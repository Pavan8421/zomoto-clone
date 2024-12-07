from django.db import models

# Create your models here.

class Restaurant(models.Model):
    restaurant_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    country_code = models.IntegerField()
    city = models.CharField(max_length=100)
    address = models.TextField()
    locality = models.CharField(max_length=100)
    locality_verbose = models.TextField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    avg_cost_for_two = models.FloatField()
    currency = models.CharField(max_length=10)
    has_table_booking = models.BooleanField()
    has_online_delivery = models.BooleanField()
    is_delivering = models.BooleanField()
    price_range = models.IntegerField()
    aggregate_rating = models.FloatField()
    rating_color = models.CharField(max_length=20)
    rating_text = models.CharField(max_length=20)
    votes = models.IntegerField()
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Cuisine(models.Model):
    name = models.CharField(max_length=100)  # Name of the cuisine (e.g., Italian, Chinese)
    restaurant = models.ForeignKey(Restaurant, related_name='cuisines', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name