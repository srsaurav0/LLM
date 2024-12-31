from django.test import TestCase
from management_app.models import City, Hotel, NewHotel, HotelSummary, HotelRatingReview
from unittest.mock import patch
from management_app.utils import query_gemini_api, query_gemini_summary, query_gemini_ratings_reviews
from django.core.management import call_command

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
            city_name="Teknaf"
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
            hotel=self.new_hotel,
            property_id=self.new_hotel.property_id,
            summary="A beautiful retreat offering stunning views."
        )

        # Verify the summary was created and linked to the correct hotel
        self.assertEqual(summary.hotel, self.new_hotel)
        self.assertEqual(summary.property_id, 214)
        self.assertEqual(summary.summary, "A beautiful retreat offering stunning views.")

    def test_hotel_rating_review_creation(self):
        # Create a HotelRatingReview for the NewHotel
        rating_review = HotelRatingReview.objects.create(
            hotel=self.new_hotel,
            property_id=self.new_hotel.property_id,
            rating=4.5,
            review="An amazing experience with excellent amenities."
        )

        # Verify the rating and review were created and linked to the correct hotel
        self.assertEqual(rating_review.hotel, self.new_hotel)
        self.assertEqual(rating_review.property_id, 214)
        self.assertEqual(rating_review.rating, 4.5)
        self.assertEqual(rating_review.review, "An amazing experience with excellent amenities.")

    def test_cascade_deletion(self):
        # Create a HotelSummary and HotelRatingReview for the NewHotel
        HotelSummary.objects.create(
            hotel=self.new_hotel,
            property_id=self.new_hotel.property_id,
            summary="A beautiful retreat offering stunning views."
        )
        HotelRatingReview.objects.create(
            hotel=self.new_hotel,
            property_id=self.new_hotel.property_id,
            rating=4.5,
            review="An amazing experience with excellent amenities."
        )

        # Delete the NewHotel instance
        self.new_hotel.delete()

        # Verify that related HotelSummary and HotelRatingReview instances are also deleted
        self.assertFalse(HotelSummary.objects.filter(property_id=214).exists())
        self.assertFalse(HotelRatingReview.objects.filter(property_id=214).exists())


class TestGeminiUtils(TestCase):
    @patch('management_app.utils.requests.post')
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
                        "role": "model"
                    },
                    "finishReason": "STOP"
                }
            ]
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        prompt = "Rewrite the name and generate a description for the following hotel."
        result = query_gemini_api(prompt)

        self.assertEqual(result["name"], "Azure Torrent Retreat")
        self.assertEqual(result["description"], "A tranquil retreat with ocean views.")

    @patch('management_app.utils.requests.post')
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
                        "role": "model"
                    },
                    "finishReason": "STOP"
                }
            ]
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        prompt = "Generate a summary for the following hotel."
        result = query_gemini_summary(prompt)

        self.assertEqual(result["summary"], "A beautiful retreat with stunning views and modern amenities.")

    @patch('management_app.utils.requests.post')
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
                        "role": "model"
                    },
                    "finishReason": "STOP"
                }
            ]
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        prompt = "Generate a rating and a review for the following hotel."
        result = query_gemini_ratings_reviews(prompt)

        self.assertEqual(result["rating"], 4.5)
        self.assertEqual(result["review"], "A wonderful stay with excellent service and amenities.")

    @patch('management_app.utils.requests.post')
    def test_query_gemini_api_failure(self, mock_post):
        # Mock a failed API response
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Bad Request"

        prompt = "Invalid prompt"
        result = query_gemini_api(prompt)

        self.assertIsNone(result)

    @patch('management_app.utils.requests.post')
    def test_query_gemini_summary_failure(self, mock_post):
        # Mock a failed API response for summary
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"

        prompt = "Invalid prompt"
        result = query_gemini_summary(prompt)

        self.assertIsNone(result)

    @patch('management_app.utils.requests.post')
    def test_query_gemini_ratings_reviews_failure(self, mock_post):
        # Mock a failed API response for ratings and reviews
        mock_post.return_value.status_code = 429
        mock_post.return_value.text = "Rate Limit Exceeded"

        prompt = "Invalid prompt"
        result = query_gemini_ratings_reviews(prompt)

        self.assertIsNone(result)


# class ReplaceDataCommandTest(TestCase):
#     def setUp(self):
#         # Create test data in the Hotel table
#         self.hotel1 = Hotel.objects.create(
#             id=1,
#             property_id=101,
#             name="Hotel Alpha",
#             rating=4.2,
#             location="Location A",
#             latitude=12.34,
#             longitude=56.78,
#             room_type="Deluxe",
#             price=200.0,
#             image_path="/images/hotel_alpha.jpg",
#             city_id=1,
#             city_name="City A"
#         )

#         self.hotel2 = Hotel.objects.create(
#             id=2,
#             property_id=102,
#             name="Hotel Beta",
#             rating=3.8,
#             location="Location B",
#             latitude=21.43,
#             longitude=65.87,
#             room_type="Standard",
#             price=150.0,
#             image_path="/images/hotel_beta.jpg",
#             city_id=2,
#             city_name="City B"
#         )

#         # Add initial data to NewHotel (to test replacement)
#         NewHotel.objects.create(
#             property_id=999,
#             name="Old Hotel",
#             description="Old description",
#             rating=1.0,
#             location="Old Location",
#             latitude=0.0,
#             longitude=0.0,
#             room_type="Old Room",
#             price=50.0,
#             image_path="/images/old_hotel.jpg",
#             city_id=999,
#             city_name="Old City"
#         )

#     def test_replace_data_command(self):
#         # Ensure NewHotel initially has the old data
#         self.assertEqual(NewHotel.objects.count(), 1)
#         old_hotel = NewHotel.objects.first()
#         self.assertEqual(old_hotel.name, "Old Hotel")

#         # Run the management command
#         call_command('replace_data')

#         # Validate that NewHotel now contains the data from Hotel
#         self.assertEqual(NewHotel.objects.count(), 2)  # Should match the count in Hotel

#         # Check the first record
#         new_hotel1 = NewHotel.objects.get(property_id=101)
#         self.assertEqual(new_hotel1.name, "Hotel Alpha")
#         self.assertEqual(new_hotel1.city_name, "City A")
#         self.assertEqual(new_hotel1.rating, 4.2)

#         # Check the second record
#         new_hotel2 = NewHotel.objects.get(property_id=102)
#         self.assertEqual(new_hotel2.name, "Hotel Beta")
#         self.assertEqual(new_hotel2.city_name, "City B")
#         self.assertEqual(new_hotel2.rating, 3.8)