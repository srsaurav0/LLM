from django.contrib import admin
from .models import NewHotel, HotelSummary, HotelRatingReview

@admin.register(NewHotel)
class NewHotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'property_id', 'city_name', 'rating', 'price')
    search_fields = ('name', 'city_name')
    list_filter = ('city_name', 'rating')

@admin.register(HotelSummary)
class HotelSummaryAdmin(admin.ModelAdmin):
    list_display = ('property_id', 'summary')
    search_fields = ('property_id', 'summary')

@admin.register(HotelRatingReview)
class HotelRatingReviewAdmin(admin.ModelAdmin):
    list_display = ('property_id', 'rating', 'review')
    search_fields = ('property_id', 'review')
