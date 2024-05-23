# Create and activate virtual environment
python -m venv venv

venv\Scripts\activate

# Install Python dependencies
cd [folder where this project's manage.py is]

pip install -r requirements.txt

# Create SQLite databse, run migrations

python manage.py migrate

# Run Django dev server

python manage.py runserver

# User Accounts
password: 123456789

usernames: admin, Rimantas, Sigitas, Lukas
