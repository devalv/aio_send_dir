install:
	poetry install --no-root
	poetry run pre-commit install

format:
	poetry run pre-commit run

run:
	poetry run python main.py

build:
	poetry build

publish: build
	poetry publish -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD}

# TODO: tests
