install:
	poetry install --no-root
	poetry run pre-commit install

format:
	poetry run pre-commit run

run:
	poetry run python main.py

build:
	poetry build

# TODO: tests
# TODO: publish
