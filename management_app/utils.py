import time
import requests

def query_gemini_api(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyDw-28lH3PIJ-PHaHAhU7qZM3HveJJzftM"

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        time.sleep(2)
        response = requests.post(url, json=payload, headers=headers)
        print(response.json())
        if response.status_code == 200:
            data = response.json()

            # Extract the content text from the response
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

            # Parse name and description from the content
            name = ""
            description = ""

            if "**Name:**" in text and "**Description:**" in text:
                name_start = text.find("**Name:**") + len("**Name:**")
                description_start = text.find("**Description:**")
                
                # Extract and clean the name
                name = text[name_start:description_start].strip()
                
                # Extract and clean the description
                description = text[description_start + len("**Description:**"):].strip()

            return {
                "name": name,
                "description": description,
            }
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return None


def query_gemini_summary(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyDw-28lH3PIJ-PHaHAhU7qZM3HveJJzftM"

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        time.sleep(2)  # Add delay to avoid hitting API rate limits
        response = requests.post(url, json=payload, headers=headers)
        print(response.json())
        print("Hello")
        if response.status_code == 200:
            data = response.json()

            # Extract the content text from the response
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

            # Parse the summary from the content
            summary = text.strip() if text else ""
            # print("Summary is: ", summary)
            return {
                "summary": summary,
            }
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return None


def query_gemini_ratings_reviews(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyDw-28lH3PIJ-PHaHAhU7qZM3HveJJzftM"

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        time.sleep(2)  # Add delay to avoid hitting API rate limits
        response = requests.post(url, json=payload, headers=headers)
        print(response.json())  # Debugging: Print the full API response

        if response.status_code == 200:
            data = response.json()

            # Extract the content text from the response
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

            # Parse rating and review from the text
            rating = 0.0
            review = ""

            # Parse the text for "Rating:" and review
            if "Rating:" in text:
                rating_start = text.find("Rating:") + len("Rating:")
                review_start = text.find("\n\n", rating_start)

                # Extract and clean the rating
                rating_text = text[rating_start:review_start].strip().replace("/5", "")
                try:
                    rating = float(rating_text)
                except ValueError:
                    rating = 0.0  # Default to 0.0 if parsing fails

                # Extract and clean the review
                review = text[review_start:].strip()

            return {
                "rating": rating,
                "review": review,
            }
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return None
