#!/bin/bash

# Exit on error
set -e

echo "Starting Django application..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist (optional - for development/demo)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "Creating superuser..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("Superuser 'admin' created successfully")
else:
    print("Superuser 'admin' already exists")
END
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Application ready! Starting Gunicorn..."

# Execute the main command
exec "$@"
