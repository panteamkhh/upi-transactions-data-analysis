# UPI Transactions Data Analysis - developer shortcuts
# Usage: make <target>

.PHONY: help install install-dev run dashboard notebook test lint format check clean

help:
	@echo "install      Install runtime dependencies"
	@echo "install-dev  Install runtime + development dependencies"
	@echo "run          Run the full analysis pipeline"
	@echo "dashboard    Launch the Streamlit dashboard"
	@echo "notebook     Open the analysis notebook in Jupyter"
	@echo "test         Run the test suite"
	@echo "lint         Lint with ruff"
	@echo "format       Format with black"
	@echo "check        Lint + format check + tests"
	@echo "clean        Remove generated artefacts"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	python -m src.run_analysis

dashboard:
	streamlit run dashboard/app.py

notebook:
	jupyter notebook notebooks/UPI_Transactions_Analysis.ipynb

test:
	pytest

lint:
	ruff check .

format:
	black .

check:
	ruff check .
	black --check .
	pytest

clean:
	rm -rf data/processed reports powerbi/*.csv screenshots/*.png
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
