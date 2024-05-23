# Create and activate virtual environment
python -m venv venv

venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Create SQLite databse, run migrations
cd myapp
python manage.py migrate

# Run Django dev server
cd myapp
python manage.py runserver
