# Get into the virtual directory
.venv/Scripts/activate.ps1
#
# Start the application
waitress-serve --port 8082 --call "yale:create_app"
# Now the user can run the application in a browser at http://localhost:8082/