# To update the application
#
# Stop the current instance of the application, with control-C
#
# cd rabies-report
# Get into the virtual directory
.venv/Scripts/activate.ps1
#.venv/bin/activate
# Install the application and its dependencies via the wheel file
python -m pip install "./dist/yale-1.0.0-py2.py3-none-any.whl"
