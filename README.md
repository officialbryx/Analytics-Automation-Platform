# AAP: Analytics Automation Platform

> A data extraction tool built with Django, Celery, PostgreSQL, and Redis.

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
python -m celery -a aap worker -l info
```

## Documentation

Detailed operations and architectural workflows are in progress. Refer to the internal Operations Manual for immediate guidelines.

## Contributing

We welcome contributions! Please follow these rules when submitting code:

1. Create a dedicated feature or bugfix branch.
2. Naming convention: Prefix your branch with feature/, fix/, or build/ (e.g., feature/add-extractor).
3. Push your branch and open a Merge Request (MR) against the main branch for review.
