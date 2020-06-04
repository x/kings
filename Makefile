.PHONY: notebook up
.DEFAULT: up

run:
	poetry run gunicorn --preload --worker-class eventlet -w 1 kings:app

deploy:
	poetry export -f requirements.txt > requirements.txt && gcloud app deploy

up: run
