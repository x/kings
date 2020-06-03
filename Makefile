.PHONY: notebook up
.DEFAULT: up

run:
	poetry run gunicorn --preload --worker-class eventlet -w 1 kings:app

up: run
