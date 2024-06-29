#cd to where you want to install the app
# Create a virtual environment in that directory
python -m venv .venv
# Get into the virtual directory
.venv/Scripts/activate.ps1
#.venv/bin/activate
python -m pip install --upgrade pip
# Install our application and its dependencies via the wheel file
python -m pip install ".\yale-1.0.0-py2.py3-none-any.whl"
# Install some dependencies
python -m pip install waitress
python -m pip install xlwt
python -m pip install requests
python -m pip install entrezpy
# First time you must initialize the database used for user authorization
flask --app yale init-db
# First time you must create the config file:
#cat "SECRET_KEY = dev'" > .venv/var/yale-instance/config.py
