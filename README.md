# Create and activate virtual environment
virtualenv -p python3 env
. ./env/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create SQLite databse, run migrations
cd myapp
./manage.py migrate

# Run Django dev server
./manage.py runserver
