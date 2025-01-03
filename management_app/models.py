from django.db import models


class City(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "cities"  # Link to the existing 'cities' table
        managed = False  # Prevent Django from modifying this table


class Hotel(models.Model):
    id = models.IntegerField(primary_key=True)
    property_id = models.IntegerField()
    name = models.CharField(max_length=255)
    rating = models.FloatField()
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    room_type = models.CharField(max_length=255)
    price = models.FloatField()
    image_path = models.CharField(max_length=255)
    city_id = models.IntegerField()
    city_name = models.CharField(max_length=255)

    class Meta:
        db_table = "hotels"  # Link to the existing 'hotels' table
        managed = False  # Prevent Django from modifying this table


class NewHotel(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-increment ID for the new table
    property_id = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)  # New description field
    rating = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    room_type = models.CharField(max_length=255, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    image_path = models.CharField(max_length=255, null=True, blank=True)
    city_id = models.IntegerField(null=True, blank=True)
    city_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "new_hotels"  # Specify the new table name
        managed = True  # Let Django manage this table


class HotelSummary(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented primary key
    property_id = models.IntegerField()  # Stores the ID of the related property
    summary = models.TextField()  # Stores the summary of the hotel

    class Meta:
        db_table = "hotel_summaries"


class HotelRatingReview(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented primary key
    property_id = models.IntegerField()  # Stores the ID of the related property
    rating = models.DecimalField(
        max_digits=3, decimal_places=2
    )  # Stores the rating (0.00 to 999.99)
    review = models.TextField()  # Stores the review text

    class Meta:
        db_table = "hotel_ratings_reviews"
