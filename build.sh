#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files (needed for admin panel CSS)
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate
