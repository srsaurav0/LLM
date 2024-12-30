import requests
from django.core.management.base import BaseCommand
from management_app.models import NewHotel

class Command(BaseCommand):
    help = 'Rewrite name and description using Ollama'

    def handle(self, *args, **kwargs):
        new_hotels = NewHotel.objects.all()
        for hotel in new_hotels:
            prompt = f"Rewrite the name and generate a description for a hotel named '{hotel.name}' located at '{hotel.location}'."
            response = self.query_ollama(prompt)
            
            if response:
                hotel.name = response.get('name', hotel.name)
                hotel.description = response.get('description', hotel.description)
                hotel.save()
        self.stdout.write(self.style.SUCCESS("Hotel names and descriptions updated!"))

    def query_ollama(self, prompt):
        # Replace with the actual Ollama endpoint and headers
        url = "http://localhost:11434"
        headers = {"Content-Type": "application/json"}
        data = {"prompt": prompt}

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                return response.json()  # Assume the response contains 'name' and 'description'
            else:
                self.stderr.write(f"Error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            self.stderr.write(f"Request failed: {e}")
        return None
