docker exec -it postgres_db psql -U user -d hotels_db
\dt
TRUNCATE TABLE django_migrations;

docker exec -it postgres_db psql -U user -d postgres
DROP DATABASE hotels_db;
CREATE DATABASE hotels_db;

docker exec -it django_app python manage.py shell

docker exec -it django_app python manage.py makemigrations
docker exec -it django_app python manage.py migrate


docker ps -a
docker stop postgres_db
docker rm postgres_db


docker exec -it django_web python manage.py shell

docker exec -it django_web python manage.py copy_hotel_data

docker exec -it django_web python manage.py rewrite_hotels

