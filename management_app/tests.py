from django.test import TestCase
from management_app.models import NewHotel, HotelSummary, HotelRatingReview
from unittest.mock import patch
from management_app.utils import (
    query_gemini_api,
    query_gemini_summary,
    query_gemini_ratings_reviews,
)
from django.core.management import call_command
from django.db import connection
from decimal import Decimal


class ModelsTestCase(TestCase):
    def setUp(self):
        # Create a NewHotel instance
        self.new_hotel = NewHotel.objects.create(
            property_id=214,
            name="Azure Torrent Retreat",
            description="A tranquil retreat with ocean views.",
            rating=4.5,
            location="Teknaf Upazila",
            latitude=21.366,
            longitude=92.2,
            room_type="Deluxe",
            price=200.0,
            image_path="/images/azure.jpg",
            city_id=1,
            city_name="Teknaf",
        )

    def test_new_hotel_creation(self):
        # Verify the NewHotel instance was created successfully
        hotel = NewHotel.objects.get(property_id=214)
        self.assertEqual(hotel.name, "Azure Torrent Retreat")
        self.assertEqual(hotel.city_name, "Teknaf")
        self.assertEqual(hotel.rating, 4.5)

    def test_hotel_summary_creation(self):
        # Create a HotelSummary for the NewHotel
        summary = HotelSummary.objects.create(
            property_id=self.new_hotel.property_id,
            summary="A beautiful retreat offering stunning views.",
        )

        # Verify the summary was created with the correct property_id
        self.assertEqual(summary.property_id, 214)
        self.assertEqual(
            summary.summary, "A beautiful retreat offering stunning views."
        )

    def test_hotel_rating_review_creation(self):
        # Create a HotelRatingReview for the NewHotel
        rating_review = HotelRatingReview.objects.create(
            property_id=self.new_hotel.property_id,
            rating=4.5,
            review="An amazing experience with excellent amenities.",
        )

        # Verify the rating and review were created with the correct property_id
        self.assertEqual(rating_review.property_id, 214)
        self.assertEqual(rating_review.rating, 4.5)
        self.assertEqual(
            rating_review.review, "An amazing experience with excellent amenities."
        )

    def test_manual_cascade_deletion(self):
        # Create a HotelSummary and HotelRatingReview for the NewHotel
        HotelSummary.objects.create(
            property_id=self.new_hotel.property_id,
            summary="A beautiful retreat offering stunning views.",
        )
        HotelRatingReview.objects.create(
            property_id=self.new_hotel.property_id,
            rating=4.5,
            review="An amazing experience with excellent amenities.",
        )

        # Manually delete related records before deleting the NewHotel instance
        HotelSummary.objects.filter(property_id=self.new_hotel.property_id).delete()
        HotelRatingReview.objects.filter(property_id=self.new_hotel.property_id).delete()

        # Delete the NewHotel instance
        self.new_hotel.delete()

        # Verify that the NewHotel instance is deleted
        self.assertFalse(NewHotel.objects.filter(property_id=214).exists())

        # Verify that related HotelSummary and HotelRatingReview instances are also deleted
        self.assertFalse(HotelSummary.objects.filter(property_id=214).exists())
        self.assertFalse(HotelRatingReview.objects.filter(property_id=214).exists())

class TestGeminiUtils(TestCase):
    @patch("management_app.utils.requests.post")
    def test_query_gemini_api_success(self, mock_post):
        # Mock a successful API response
        mock_response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "**Name:** Azure Torrent Retreat\n\n**Description:** A tranquil retreat with ocean views."
                            }
                        ],
                        "role": "model",
                    },
                    "finishReason": "STOP",
                }
            ]
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        prompt = "Rewrite the name and generate a description for the following hotel."
        result = query_gemini_api(prompt)

        self.assertEqual(result["name"], "Azure Torrent Retreat")
        self.assertEqual(result["description"], "A tranquil retreat with ocean views.")

    @patch("management_app.utils.requests.post")
    def test_query_gemini_summary_success(self, mock_post):
        # Mock a successful API response for summary
        mock_response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "A beautiful retreat with stunning views and modern amenities."
                            }
                        ],
                        "role": "model",
                    },
                    "finishReason": "STOP",
                }
            ]
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        prompt = "Generate a summary for the following hotel."
        result = query_gemini_summary(prompt)

        self.assertEqual(
            result["summary"],
            "A beautiful retreat with stunning views and modern amenities.",
        )

    @patch("management_app.utils.requests.post")
    def test_query_gemini_ratings_reviews_success(self, mock_post):
        # Mock a successful API response for ratings and reviews
        mock_response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "Rating: 4.5/5\n\nA wonderful stay with excellent service and amenities."
                            }
                        ],
                        "role": "model",
                    },
                    "finishReason": "STOP",
                }
            ]
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        prompt = "Generate a rating and a review for the following hotel."
        result = query_gemini_ratings_reviews(prompt)

        self.assertEqual(result["rating"], 4.5)
        self.assertEqual(
            result["review"], "A wonderful stay with excellent service and amenities."
        )

    @patch("management_app.utils.requests.post")
    def test_query_gemini_api_failure(self, mock_post):
        # Mock a failed API response
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Bad Request"

        prompt = "Invalid prompt"
        result = query_gemini_api(prompt)

        self.assertIsNone(result)

    @patch("management_app.utils.requests.post")
    def test_query_gemini_summary_failure(self, mock_post):
        # Mock a failed API response for summary
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"

        prompt = "Invalid prompt"
        result = query_gemini_summary(prompt)

        self.assertIsNone(result)

    @patch("management_app.utils.requests.post")
    def test_query_gemini_ratings_reviews_failure(self, mock_post):
        # Mock a failed API response for ratings and reviews
        mock_post.return_value.status_code = 429
        mock_post.return_value.text = "Rate Limit Exceeded"

        prompt = "Invalid prompt"
        result = query_gemini_ratings_reviews(prompt)

        self.assertIsNone(result)


class CopyHotelDataCommandTest(TestCase):
    def setUp(self):
        # Create the mock `hotels` table manually
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE hotels (
                    id SERIAL PRIMARY KEY,
                    property_id INTEGER NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    rating FLOAT NOT NULL,
                    location VARCHAR(255) NOT NULL,
                    latitude FLOAT NOT NULL,
                    longitude FLOAT NOT NULL,
                    room_type VARCHAR(255),
                    price FLOAT,
                    image_path VARCHAR(255),
                    city_id INTEGER,
                    city_name VARCHAR(255)
                )
            """
            )

        # Insert test data into the `hotels` table
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO hotels (id, property_id, name, rating, location, latitude, longitude, room_type, price, image_path, city_id, city_name)
                VALUES
                (1, 101, 'Hotel Alpha', 4.2, 'Location A', 12.34, 56.78, 'Deluxe', 200.0, '/images/hotel_alpha.jpg', 1, 'City A'),
                (2, 102, 'Hotel Beta', 3.8, 'Location B', 21.43, 65.87, 'Standard', 150.0, '/images/hotel_beta.jpg', 2, 'City B')
            """
            )

        # Add initial data to `new_hotels` (to test replacement)
        NewHotel.objects.create(
            property_id=999,
            name="Old Hotel",
            description="Old description",
            rating=1.0,
            location="Old Location",
            latitude=0.0,
            longitude=0.0,
            room_type="Old Room",
            price=50.0,
            image_path="/images/old_hotel.jpg",
            city_id=999,
            city_name="Old City",
        )

    def tearDown(self):
        # Drop the `hotels` table after the test
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE hotels")

    def test_replace_data_command(self):
        # Ensure `new_hotels` initially has the old data
        self.assertEqual(NewHotel.objects.count(), 1)
        old_hotel = NewHotel.objects.first()
        self.assertEqual(old_hotel.name, "Old Hotel")

        # Run the management command
        call_command("copy_hotel_data")

        # Validate that `new_hotels` now contains the data from `hotels`
        self.assertEqual(
            NewHotel.objects.count(), 2
        )  # Should match the count in `hotels`

        # Check the first record
        new_hotel1 = NewHotel.objects.get(property_id=101)
        self.assertEqual(new_hotel1.name, "Hotel Alpha")
        self.assertEqual(new_hotel1.city_name, "City A")
        self.assertEqual(new_hotel1.rating, 4.2)

        # Check the second record
        new_hotel2 = NewHotel.objects.get(property_id=102)
        self.assertEqual(new_hotel2.name, "Hotel Beta")
        self.assertEqual(new_hotel2.city_name, "City B")
        self.assertEqual(new_hotel2.rating, 3.8)


class RewriteHotelsCommandTest(TestCase):
    def setUp(self):
        # Create test data in the NewHotel table
        self.hotel1 = NewHotel.objects.create(
            property_id=101,
            name="Hotel Alpha",
            description="A basic hotel description.",
            rating=4.5,
            location="Location A",
            latitude=12.34,
            longitude=56.78,
            room_type="Deluxe",
            price=200.0,
            image_path="/images/hotel_alpha.jpg",
            city_id=1,
            city_name="City A",
        )

        self.hotel2 = NewHotel.objects.create(
            property_id=102,
            name="Hotel Beta",
            description="Another basic hotel description.",
            rating=3.8,
            location="Location B",
            latitude=21.43,
            longitude=65.87,
            room_type="Standard",
            price=150.0,
            image_path="/images/hotel_beta.jpg",
            city_id=2,
            city_name="City B",
        )

    @patch("management_app.management.commands.rewrite_hotels.query_gemini_api")
    def test_rewrite_name_and_description_success(self, mock_query_gemini_api):
        # Mock the API responses for rewriting name and description
        mock_query_gemini_api.side_effect = [
            {
                "name": "Alpha Retreat",
                "description": "A luxurious hotel with breathtaking views.",
            },
            {
                "name": "Beta Haven",
                "description": "An urban escape with modern amenities.",
            },
        ]

        # Run the management command
        call_command("rewrite_hotels")

        # Verify that the names and descriptions were updated in the database
        updated_hotel1 = NewHotel.objects.get(property_id=101)
        self.assertEqual(updated_hotel1.name, "Alpha Retreat")
        self.assertEqual(
            updated_hotel1.description, "A luxurious hotel with breathtaking views."
        )

        updated_hotel2 = NewHotel.objects.get(property_id=102)
        self.assertEqual(updated_hotel2.name, "Beta Haven")
        self.assertEqual(
            updated_hotel2.description, "An urban escape with modern amenities."
        )

    @patch("management_app.management.commands.rewrite_hotels.query_gemini_api")
    def test_rewrite_name_and_description_partial_success(self, mock_query_gemini_api):
        # Mock the API response to return partial data for one hotel
        mock_query_gemini_api.side_effect = [
            {"name": "Alpha Retreat"},  # No description provided
            {
                "description": "An urban escape with modern amenities."
            },  # No name provided
        ]

        # Run the management command
        call_command("rewrite_hotels")

        # Verify the updates in the database
        updated_hotel1 = NewHotel.objects.get(property_id=101)
        self.assertEqual(updated_hotel1.name, "Alpha Retreat")  # Name updated
        self.assertEqual(
            updated_hotel1.description, "A basic hotel description."
        )  # Description unchanged

        updated_hotel2 = NewHotel.objects.get(property_id=102)
        self.assertEqual(updated_hotel2.name, "Hotel Beta")  # Name unchanged
        self.assertEqual(
            updated_hotel2.description, "An urban escape with modern amenities."
        )  # Description updated

    @patch("management_app.management.commands.rewrite_hotels.query_gemini_api")
    def test_rewrite_name_and_description_failure(self, mock_query_gemini_api):
        # Mock the API response to simulate failure
        mock_query_gemini_api.return_value = None

        # Run the management command
        call_command("rewrite_hotels")

        # Verify that no changes were made to the database
        unchanged_hotel1 = NewHotel.objects.get(property_id=101)
        self.assertEqual(unchanged_hotel1.name, "Hotel Alpha")
        self.assertEqual(unchanged_hotel1.description, "A basic hotel description.")

        unchanged_hotel2 = NewHotel.objects.get(property_id=102)
        self.assertEqual(unchanged_hotel2.name, "Hotel Beta")
        self.assertEqual(
            unchanged_hotel2.description, "Another basic hotel description."
        )


class GenerateRatingsReviewsCommandTest(TestCase):
    def setUp(self):
        # Create test data in NewHotel table
        self.hotel1 = NewHotel.objects.create(
            property_id=101,
            name="Hotel Alpha",
            description="A tranquil retreat with ocean views.",
            rating=4.5,
            location="Location A",
            latitude=12.34,
            longitude=56.78,
            room_type="Deluxe",
            price=200.0,
            image_path="/images/hotel_alpha.jpg",
            city_id=1,
            city_name="City A",
        )

        self.hotel2 = NewHotel.objects.create(
            property_id=102,
            name="Hotel Beta",
            description="An urban escape with modern amenities.",
            rating=3.8,
            location="Location B",
            latitude=21.43,
            longitude=65.87,
            room_type="Standard",
            price=150.0,
            image_path="/images/hotel_beta.jpg",
            city_id=2,
            city_name="City B",
        )

    @patch(
        "management_app.management.commands.generate_ratings_reviews.query_gemini_ratings_reviews"
    )
    def test_generate_ratings_reviews_success(self, mock_query_gemini_ratings_reviews):
        # Mock the API response for successful rating and review generation
        mock_query_gemini_ratings_reviews.side_effect = [
            {"rating": 4.5, "review": "An amazing experience with excellent service."},
            {"rating": 3.8, "review": "A great stay with modern facilities."},
        ]

        # Run the management command
        call_command("generate_ratings_reviews")

        # Verify the ratings and reviews were created in the database
        self.assertEqual(HotelRatingReview.objects.count(), 2)

        # Validate the first hotel's rating and review
        rating_review1 = HotelRatingReview.objects.get(property_id=101)
        self.assertEqual(rating_review1.property_id, 101)
        self.assertEqual(rating_review1.rating, Decimal("4.50"))  # Compare as Decimal
        self.assertEqual(
            rating_review1.review, "An amazing experience with excellent service."
        )

        # Validate the second hotel's rating and review
        rating_review2 = HotelRatingReview.objects.get(property_id=102)
        self.assertEqual(rating_review2.property_id, 102)
        self.assertEqual(rating_review2.rating, Decimal("3.80"))  # Compare as Decimal
        self.assertEqual(rating_review2.review, "A great stay with modern facilities.")

    @patch(
        "management_app.management.commands.generate_ratings_reviews.query_gemini_ratings_reviews"
    )
    def test_generate_ratings_reviews_failure(self, mock_query_gemini_ratings_reviews):
        # Mock the API response for failure (e.g., API error or no response)
        mock_query_gemini_ratings_reviews.return_value = None

        # Run the management command
        call_command("generate_ratings_reviews")

        # Verify that no ratings or reviews were created in the database
        self.assertEqual(HotelRatingReview.objects.count(), 0)

    @patch(
        "management_app.management.commands.generate_ratings_reviews.query_gemini_ratings_reviews"
    )
    def test_replace_existing_ratings_reviews(self, mock_query_gemini_ratings_reviews):
        # Create an existing rating and review for the first hotel
        HotelRatingReview.objects.create(
            property_id=101,
            rating=3.0,
            review="An outdated review.",
        )

        # Mock the API response for updated ratings and reviews
        mock_query_gemini_ratings_reviews.side_effect = [
            {"rating": 4.5, "review": "An amazing experience with excellent service."},
            {"rating": 3.8, "review": "A great stay with modern facilities."},
        ]

        # Run the management command
        call_command("generate_ratings_reviews")

        # Verify the ratings and reviews were replaced
        self.assertEqual(HotelRatingReview.objects.count(), 2)

        # Validate the updated rating and review for the first hotel
        updated_rating_review1 = HotelRatingReview.objects.get(property_id=101)
        self.assertEqual(updated_rating_review1.property_id, 101)
        self.assertEqual(updated_rating_review1.rating, Decimal("4.50"))
        self.assertEqual(
            updated_rating_review1.review,
            "An amazing experience with excellent service.",
        )

        # Validate the updated rating and review for the second hotel
        updated_rating_review2 = HotelRatingReview.objects.get(property_id=102)
        self.assertEqual(updated_rating_review2.property_id, 102)
        self.assertEqual(updated_rating_review2.rating, Decimal("3.80"))
        self.assertEqual(
            updated_rating_review2.review, "A great stay with modern facilities."
        )


class GenerateSummariesCommandTest(TestCase):
    def setUp(self):
        # Create test data in the NewHotel table
        self.hotel1 = NewHotel.objects.create(
            property_id=101,
            name="Hotel Alpha",
            description="A tranquil retreat with ocean views.",
            rating=4.5,
            location="Location A",
            latitude=12.34,
            longitude=56.78,
            room_type="Deluxe",
            price=200.0,
            image_path="/images/hotel_alpha.jpg",
            city_id=1,
            city_name="City A",
        )

        self.hotel2 = NewHotel.objects.create(
            property_id=102,
            name="Hotel Beta",
            description="An urban escape with modern amenities.",
            rating=3.8,
            location="Location B",
            latitude=21.43,
            longitude=65.87,
            room_type="Standard",
            price=150.0,
            image_path="/images/hotel_beta.jpg",
            city_id=2,
            city_name="City B",
        )

    @patch("management_app.management.commands.generate_summaries.query_gemini_summary")
    def test_generate_summaries_success(self, mock_query_gemini_summary):
        # Mock the API responses for generating summaries
        mock_query_gemini_summary.side_effect = [
            {
                "summary": "A beautiful retreat offering stunning views and luxurious amenities."
            },
            {
                "summary": "An urban oasis with cutting-edge facilities and top-notch service."
            },
        ]

        # Run the management command
        call_command("generate_summaries")

        # Verify that summaries were created in the database
        self.assertEqual(HotelSummary.objects.count(), 2)

        # Validate the first hotel's summary
        summary1 = HotelSummary.objects.get(property_id=101)
        self.assertEqual(summary1.property_id, 101)
        self.assertEqual(
            summary1.summary,
            "A beautiful retreat offering stunning views and luxurious amenities.",
        )

        # Validate the second hotel's summary
        summary2 = HotelSummary.objects.get(property_id=102)
        self.assertEqual(summary2.property_id, 102)
        self.assertEqual(
            summary2.summary,
            "An urban oasis with cutting-edge facilities and top-notch service.",
        )

    @patch("management_app.management.commands.generate_summaries.query_gemini_summary")
    def test_generate_summaries_partial_success(self, mock_query_gemini_summary):
        # Mock the API response to return a summary for only one hotel
        mock_query_gemini_summary.side_effect = [
            {
                "summary": "A beautiful retreat offering stunning views and luxurious amenities."
            },
            None,  # Simulate failure for the second hotel
        ]

        # Run the management command
        call_command("generate_summaries")

        # Verify the first summary was created
        self.assertEqual(HotelSummary.objects.count(), 1)
        summary1 = HotelSummary.objects.get(property_id=101)
        self.assertEqual(summary1.property_id, 101)
        self.assertEqual(
            summary1.summary,
            "A beautiful retreat offering stunning views and luxurious amenities.",
        )

        # Ensure no summary exists for the second hotel
        self.assertFalse(HotelSummary.objects.filter(property_id=102).exists())

    @patch("management_app.management.commands.generate_summaries.query_gemini_summary")
    def test_replace_existing_summary(self, mock_query_gemini_summary):
        # Create an existing summary for the first hotel
        HotelSummary.objects.create(
            property_id=101,
            summary="An outdated summary.",
        )

        # Mock the API responses for updated summaries
        mock_query_gemini_summary.side_effect = [
            {
                "summary": "A beautiful retreat offering stunning views and luxurious amenities."
            },
            {
                "summary": "An urban oasis with cutting-edge facilities and top-notch service."
            },
        ]

        # Run the management command
        call_command("generate_summaries")

        # Verify that the summary was replaced for the first hotel
        self.assertEqual(HotelSummary.objects.count(), 2)
        updated_summary1 = HotelSummary.objects.get(property_id=101)
        self.assertEqual(
            updated_summary1.summary,
            "A beautiful retreat offering stunning views and luxurious amenities.",
        )

        # Verify the second hotel's summary was created
        summary2 = HotelSummary.objects.get(property_id=102)
        self.assertEqual(summary2.property_id, 102)
        self.assertEqual(
            summary2.summary,
            "An urban oasis with cutting-edge facilities and top-notch service.",
        )
