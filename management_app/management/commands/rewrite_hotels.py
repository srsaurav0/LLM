from django.core.management.base import BaseCommand
from management_app.models import NewHotel
from management_app.utils import query_gemini_api


class Command(BaseCommand):
    help = "Rewrite name and description using Google AI Studio API"

    def handle(self, *args, **kwargs):
        new_hotels = NewHotel.objects.all()
        for hotel in new_hotels:
            prompt = (
                f"Rewrite the name in a unique way and generate a unique description within 100 words for a hotel named "
                f"'{hotel.name}' located at: '{hotel.city_name}'."
            )
            response = query_gemini_api(prompt)

            if response:
                hotel.name = response.get("name", hotel.name)
                hotel.description = response.get("description", hotel.description)
                hotel.save()

        self.stdout.write(self.style.SUCCESS("Hotel names and descriptions updated!"))
        # time.sleep(5)
