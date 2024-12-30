from django.core.management.base import BaseCommand
from management_app.models import Hotel, NewHotel

class Command(BaseCommand):
    help = 'Copy data from hotels to new_hotels'

    def handle(self, *args, **kwargs):
        hotels = Hotel.objects.all()
        for hotel in hotels:
            NewHotel.objects.create(
                property_id=hotel.property_id,
                name=hotel.name,
                description='',  # Initialize with an empty description
                rating=hotel.rating,
                location=hotel.location,
                latitude=hotel.latitude,
                longitude=hotel.longitude,
                room_type=hotel.room_type,
                price=hotel.price,
                image_path=hotel.image_path,
                city_id=hotel.city_id,
                city_name=hotel.city_name,
            )
        self.stdout.write(self.style.SUCCESS("Data copied successfully to new_hotels!"))
