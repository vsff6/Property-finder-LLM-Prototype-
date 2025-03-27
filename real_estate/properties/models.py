from django.db import models

# Create your models here.
class Property(models.Model):
    broker_title = models.CharField(max_length=255)
    property_type = models.CharField(max_length=100)
    price = models.FloatField()
    beds = models.IntegerField()
    bath = models.FloatField()
    property_sqft = models.FloatField()
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.property_type} in {self.city}"
    
class Rating(models.Model):
    message = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class Correction(models.Model):
    message = models.TextField()
    correction = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)