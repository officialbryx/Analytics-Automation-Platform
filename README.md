# AAP: Analytics Automation Platform

> A data extraction tool built with Django, Celery, PostgreSQL, and Redis.
> Pick companies, a financial statement and a fiscal-year range. AAP pulls the figures from the
> SEC public dataset in BigQuery, stores them in the database as JSON, and lets you download them as an `.xlsx` file.

---

## Tech Stack & Prerequisites

Ensure you have the following installed locally:
- [Python 3.11+](https://www.python.org/)
- [Conda](https://docs.conda.io/en/latest/) (optional, for virtual environments)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

---

## Getting Started

1. Create and activate a virtual environment, then install the dependencies:

```bash
# Create a Conda virtual environment
conda create --name aap-venv python=3.11 -y

# Activate the environment
conda activate aap-venv

# Install dependencies
pip install -r requirements.txt
```

## Usage
2. Put these in .env file
```
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=["localhost", "127.0.0.1"]
DJANGO_CSRF_TRUSTED_ORIGINS=["https://localhost", "[https://127.0.0.1](https://127.0.0.1)"]

POSTGRES_USER=aap
POSTGRES_PASSWORD=aap
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aap

REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=redis123
REDIS_PORT=6379

GOOGLE_OAUTH2_KEY=your_client_id_here
GOOGLE_OAUTH2_SECRET=your_client_key_here
GOOGLE_APPLICATION_CREDENTIALS=your_application_credentials_json_here
```

3. Spin up services PostgreSQL & Redis services using Docker Compose:

```
docker compose up
```

This will create a PostgreSQL and Redis databases. These should be run via Docker dashboard so press `Ctrl + C` and run it via the Docker dashboard

4. Apply database migrations and create an intial admin account:

```
# Run migrations
python app/manage.py makemigrations
python app/manage.py migrate

# Create superuser (use an @gmail.com email address)
python app/manage.py createsuperuser
```

5. Run the application locally, open two separate terminal instances with `aap-venv` environment activated:

**Run the web application**
```
python app/manage.py runserver
```

**Run the celery worker**
```
python -m celery -A aap worker -l info
```

## How a report works

1. Fill in the form: report name, companies, financial statement (Income Statement, Balance Sheet or Cash Flow), annual or quarterly, and the fiscal-year range.
2. A Celery worker queries BigQuery (`bigquery-public-data.sec_quarterly_financials`) and saves the result as JSON in the request's `result_data` column.
3. When the request is `FINISHED`, click the link on the Requests page to download the `.xlsx`. The file is built on demand from the stored JSON.

Notes:
- Output has one row per company per period, with all amounts in exact dollars (EPS is in dollars per share).
- The SEC dataset only covers fiscal years 2009 to 2021.
- Quarterly reports cover Q1 to Q3 (Q4 is part of the annual 10-K). Quarterly cash flow is year-to-date, as companies report it.
- The service account needs BigQuery access only. No Google Drive or Sheets access is used.

## Documentation

Detailed operations and architectural workflows are in progress. Refer to the internal Operations Manual for immediate guidelines.

## Contributing

We welcome contributions! Please follow these rules when submitting code:

1. Create a dedicated feature or bugfix branch.
2. Naming convention: Prefix your branch with feature/, fix/, or build/ (e.g., feature/add-extractor).
3. Push your branch and open a Merge Request (MR) against the main branch for review.
