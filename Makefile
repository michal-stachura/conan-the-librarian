migrations:
	docker-compose -p ctl -f docker-compose.local.yml run --rm django python manage.py makemigrations

migrate:
	docker-compose -p ctl -f docker-compose.local.yml run --rm django python manage.py migrate

makemessages:
	docker-compose -p ctl -f docker-compose.local.yml run --rm django python manage.py makemessages -a

compilemessages:
	docker-compose -p ctl -f docker-compose.local.yml run --rm django python manage.py compilemessages

superuser:
	docker-compose -p ctl -f docker-compose.local.yml run --rm django python manage.py createsuperuser

run:
	docker-compose -p ctl -f docker-compose.local.yml up

build:
	docker-compose -p ctl -f docker-compose.local.yml build

down:
	docker-compose -p ctl -f docker-compose.local.yml down

test:
	docker-compose -p ctl -f docker-compose.local.yml run --rm \
	-e DJANGO_SETTINGS_MODULE=config.settings.test \
	django pytest -n 4 -x --create-db

test-app:
	docker-compose -p ctl -f docker-compose.local.yml run --rm \
	-e DJANGO_SETTINGS_MODULE=config.settings.test \
	django pytest -x conan_the_librarian/$(app) --create-db --nomigrations

test-specific:
	docker-compose -p ctl -f docker-compose.local.yml run --rm \
    -e PYTHONBREAKPOINT=ipdb.set_trace \
    -e DJANGO_SETTINGS_MODULE=config.settings.test \
    django pytest -x -k "$(test)" --create-db --nomigrations -s

shell:
	docker-compose -p ctl -f docker-compose.local.yml run --rm django python manage.py shell

cleardocker:
	docker-compose -p ctl -f docker-compose.local.yml down --remove-orphans --rmi all

cleardockerandvolumes:
	docker-compose -p ctl -f docker-compose.local.yml down --volumes --remove-orphans --rmi all

pgbash:
	docker exec -it conan_the_librarian_local_postgres /bin/bash

bash:
	docker exec -it conan_the_librarian_local_django /bin/bash

logscelerybeat:
	docker-compose -p ctl -f docker-compose.local.yml logs -f celerybeat
