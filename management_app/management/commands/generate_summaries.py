from django.core.management.base import BaseCommand
from management_app.models import NewHotel, HotelSummary
from management_app.utils import query_gemini_summary

class Command(BaseCommand):
    help = 'Generate summaries for hotels'

    def handle(self, *args, **kwargs):
        hotels = NewHotel.objects.all()
        for hotel in hotels:
            # Remove old summary if it exists
            HotelSummary.objects.filter(hotel=hotel).delete()

            # Create the prompt for the API
            prompt = (
                f"Write a summary for the following hotel:\n"
                f"Name: {hotel.name}\n"
                f"Location: {hotel.city_name}\n"
                f"Details: {hotel.description}\n"
            )

            # Query the Gemini API
            response = query_gemini_summary(prompt)

            if response and response.get("summary"):
                try:
                    # Save the new summary in the database
                    HotelSummary.objects.create(
                        hotel=hotel,
                        property_id=hotel.property_id,
                        summary=response["summary"]
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"Summary generated for hotel: {hotel.name}")
                    )
                except Exception as e:
                    self.stderr.write(f"Error saving summary for hotel: {hotel.name}. Error: {e}")
            else:
                self.stderr.write(f"Failed to generate summary for hotel: {hotel.name}")
