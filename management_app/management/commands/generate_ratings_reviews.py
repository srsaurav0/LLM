from django.core.management.base import BaseCommand
from management_app.models import NewHotel, HotelRatingReview
from management_app.utils import query_gemini_ratings_reviews


class Command(BaseCommand):
    help = "Generate ratings and reviews for hotels"

    def handle(self, *args, **kwargs):
        hotels = NewHotel.objects.all()
        for hotel in hotels:
            # Remove old ratings and reviews if they exist
            HotelRatingReview.objects.filter(property_id=hotel.property_id).delete()

            # Create the prompt for the API
            prompt = (
                f"Generate a numerical rating (0-5) and a review within 100 words for the following hotel:\n"
                f"Name: {hotel.name}\n"
                f"Location: {hotel.city_name}\n"
                f"Details: {hotel.description}\n"
            )

            # Query the Gemini API
            response = query_gemini_ratings_reviews(prompt)

            if (
                response
                and response.get("rating") is not None
                and response.get("review")
            ):
                try:
                    # Save the new rating and review in the database
                    HotelRatingReview.objects.create(
                        property_id=hotel.property_id,
                        rating=response["rating"],
                        review=response["review"],
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Rating and review generated for hotel: {hotel.name}"
                        )
                    )
                except Exception as e:
                    self.stderr.write(
                        f"Error saving rating/review for hotel: {hotel.name}. Error: {e}"
                    )
            else:
                self.stderr.write(
                    f"Failed to generate rating/review for hotel: {hotel.name}"
                )
