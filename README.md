# Property Management System (Django CLI and LLM)

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Setup Instructions](#setup-instructions)
5. [Usage](#usage)
6. [Project Structure](#project-structure)
7. [Testing](#testing)
8. [API Integration](#api-integration)
9. [Known Issues and Troubleshooting](#known-issues-and-troubleshooting)

---

## Overview
This project is a **Property Management System** designed to manage hotels, their summaries, ratings, and reviews. The project integrates **Django** for backend management and uses the **Gemini API** from Google AI Studio for generating hotel descriptions, summaries, and reviews. It also uses another repository to scrape data from the [Trip.com](https://uk.trip.com/hotels/?locale=en-GB&curr=GBP) website. It is built with the following features:

- Management of hotels and their details.
- AI-generated summaries, ratings, and reviews.
- PostgreSQL as the database backend.
- Docker for containerization and deployment.
- PgAdmin and Django Admin for user-friendly management.

---

## Features
- **CRUD Operations**: Manage hotels and related entities.
- **PostgreSQL with Django Network**: Database from another project is used with Django Network.
- **Integration with Google AI Studio API**:
  - Generate descriptions and summaries for hotels.
  - Create ratings and reviews for hotels.
- **Django Admin**: Manage all entities with a web interface.
- **Test Suite**: Includes unit tests for models, admin configuration, and management commands.

---

## Requirements

### **System Requirements**
- Python 3.10+
- Docker and Docker Compose
- PostgreSQL

### **Python Packages**
The key dependencies are managed in `requirements.txt`:

- Django
- psycopg2-binary
- requests
- coverage

---

## Setup Instructions

### **1. Clone the Scrapy Repository**
```bash
git clone https://github.com/srsaurav0/Hotel-Retrieval-Scrapy.git
cd Hotel-Retrieval-Scrapy
```

### **2. Create and activate a Virtual Environment for this Project**
On Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
```

### **3. Build and Start Docker Containers**
- Ensure Docker is installed and running on your system. 
- The next instruction will automatically fetch **3 cities and 5 hotels (If available)** for each of these cities. So, it may take up some time.
- If you want to to change the number of hotels to be fetched:
  - It can be accessed in the file ***Hotel-Retrieval-Scrapy/hotel_scraper/spiders/city_hotels.py***
  - Go to **line 119** and change the value accordingly.

- Then, run the following command:

```bash
docker-compose up --build
```

### **4. Clone the LLM Repository**
- Open another terminal in the parent directory and run the following command:
```bash
git clone https://github.com/srsaurav0/LLM.git
cd LLM
```

### **5. Create and Activate a Virtual Environment for this Project**
On Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
```

### **6. Build and Start Docker Containers**
- Run the following command:
  ```bash
  docker-compose up --build
  ```
- This will automatically complete the migrations and create 3 tables.
  - new_hotels
  - hotel_summaries
  - hotel_ratings_reviews

- After running this command, the system includes the following services:
  - **Django Web App**: Exposed on `http://localhost:8000`.
  - **PostgreSQL Database**: Accessible internally as `postgres_db:5432`.
  - **pgAdmin**: Available at `http://localhost:5050` (credentials: `admin@admin.com` / `admin`).

---

## Usage

### **1. Generate Data using AI with Custom Commands**
A custom delay of 2 seconds is set before each query to avoid violating the quota of the Gemini API. The delays are available inside file ***LLM/management_app/utils.py*** in lines ***22***, ***75***, and ***116***.

- **Copy the current hotels data into new table new_hotels:**
  ```bash
  docker exec -it django_web python manage.py copy_hotel_data
  ```
- **Generate Name and Description for the hotels in new_hotels table:**
  ```bash
  docker exec -it django_web python manage.py rewrite_hotels
  ```
  - Executing this command will also print the respons.json() fetched from the API call in the terminal. To stop this, go to file ***LLM/management_app/utils.py*** and comment ***line 24*** `print(response.json())`.
- **Generate Summary of hotels in hotel_summaries table:**
  ```bash
  docker exec -it django_web python manage.py generate_summaries
  ```
  - Executing this command will also print the respons.json() fetched from the API call in the terminal. To stop this, go to file ***LLM/management_app/utils.py*** and comment ***line 77*** `print(response.json())`.
- **Generate Ratings and Reviews of the hotels in new_hotels table:**
  ```bash
  docker exec -it django_web python manage.py generate_ratings_reviews
  ```
  - Executing this command will also print the respons.json() fetched from the API call in the terminal. To stop this, go to file ***LLM/management_app/utils.py*** and comment ***line 116*** `print(response.json())`.

### **2. Analyze the Data**
- **Using Django Admin**:
  - In a terminal, execute these commands:
  ```bash
  docker exec -it django_web python manage.py createsuperuser
  ```
  - Register these credentials:
    - `Username`: `admin`
    - `Email Address`: `admin@admin.com`
    - `Password`: `admin`
    - Bypass password validation and create user anyway? [y/N]: y
  - Go to http://localhost:8000/admin/
  - Enter these credentials and log in:
    - `Username`: `admin`
    - `Password`: `admin`
  - Click on **New hotels** to view the updated name and description of hotels.
  - Click on **Hotel summarys** to view the updated summary of hotels.
  - Click on **Hotel ratings reviews** to view the updated ratings and reviews of hotels.

- **Using PgAdmin**:
  - Go to http://localhost:5050/
  - Enter these credentials and press the `Login` button:
    - `Email Address / Username`: `admin@admin.com`
    - `Password`: `admin`
  - Right click on `Servers` and then `Register` > `Server`
  - In `General` tab, enter `Name`: `LLM`
  - In `Connection` tab, enter these details and click `Save`
    - `Host name/address`: `postgres_db`
    - `Username`: `user`
    - `Password`: `password`
  - Then go to ***Servers > LLM > Databases > hotels_db > Schemas > public > Tables***
  - To view the AI generated names and description of hotels, right click on the **new_hotels** table and click on `View/Edit Data` > `All Rows`
  - To view the AI generated summary of hotels, right click on the **hotel_summaries** table and click on `View/Edit Data` > `All Rows`
  - To view the AI generated ratings and reviews of hotels, right click on the **hotel_ratings_reviews** table and click on `View/Edit Data` > `All Rows`

---

## Project Structure
```
.
├── management_app
│   ├── admin.py          # Django admin configurations
│   ├── models.py         # Database models
│   ├── management
│   │   └── commands
│   │       ├── copy_hotel_data.py
│   │       ├── generate_ratings_reviews.py
│   │       ├── generate_summaries.py
│   │       └── rewrite_hotels.py
│   ├── migrations         # Migration files
│   ├── tests.py           # Tests
│   └── utils.py           # API query utility functions
│
├── property_management    # Main project
│   ├── asgi.py            # Communication between web servers
│   ├── settings.py        # Database models
│   ├── urls.py            # URL configuration project
│   └── wsgi.py            # Communication between web applications
│
├── .coveragerc            # Files to avoid when calculating coverage
├── .gitignore             # Gitignore file
├── Dockerfile             # Docker build configuration
├── docker-compose.yml     # Docker Compose setup
├── requirements.txt       # Python dependencies
├── manage.py              # Django management script
└── README.md              # Project documentation
```

---

## Testing
Run the test suite to ensure all features work as expected:
```bash
docker exec -it django_web python manage.py test
```
Run the tests with coverage:
```bash
docker exec -it django_web coverage run manage.py test
docker exec -it django_web coverage report
```

### **Test Coverage**
- Models: Validates database schema and relationships.
- Utilities: Ensures utility functions work correctly.
- Management Commands: Ensures data processing commands work correctly.

---

## API Integration

### **Utility Functions**
- **query_gemini_api**: Generates names and descriptions.
- **query_gemini_summary**: Generates hotel summaries.
- **query_gemini_ratings_reviews**: Generates ratings and reviews.

These are defined in `management_app/utils.py`.

---

## Known Issues and Troubleshooting

1. **Django Admin Not Accessible**:
   - Ensure the `django_web` container is running.
   - Check if port `8000` is exposed in `docker-compose.yml`. Use command `docker ps` to list all the running containers and their respective ports.

2. **API Rate Limits**:
   - Add delays between API calls in management commands to avoid hitting rate limits.

3. **Database Connectivity Issues**:
   - Ensure the `postgres_db` container is running.

3. **PgAdmin Connectivity Issues**:
   - Ensure the `pgadmin` container is running.