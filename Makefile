install:
	.\venv\Scripts\pip install -r requirements.txt

format:
	black *.py

lint:
	pylint --disable=R,C,W --ignore venv *.py

type:
	mypy --exclude venv .

all: install format lint type
