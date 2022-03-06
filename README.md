CSS 436 Cloud Computing Final Project 
Members: Jay, Jaeha, Mehak, Duncan

README created by: Jay Lin

# Summary
What: This is a Django (Python-based framework) application that provides a map view of 
notes saved around the world. Users can write and save notes, then select whichever location
on the world map they would like the note to be attached to.

# Quickstart
Prerequisites: Python 3.9, Django (check with python -m django --version)

Run ``virtualenv ~/virt`` to create a python virtual environment.
To run the application locally, enter ``source ~/virt/bin/activate`` to activate a virtual
environment. Then, type: ``python3 manage.py runserver``. 
- Type CTRL+C when you want to stop the local web server.
- To change the server port, pass the number as cmdline arg: ``python3 manage.py runserver 8080``

# Project Structure
Below is a tree of the current project. Files of note have comments in parentheses next to their names.
Files without comments you don't need to worry about on a basic level.

frontend/
|--mapnotes/ (houses our actual application)
|   |--migrations/ (for migrating the data)
|       |--__init__.py
|   |--templates/
|       |--feed.html (list of all notes)
|       |--index.html (main page showing the map)
|       |--user.html (shows 1 specific user)
|   |--__init__.py (declares mapnotes as a module)
|   |--admin.py
|   |--apps.py
|   |--models.py (where we setup the database schema)
|   |--tests.py
|   |--urls.py (specify app-specific URL locations)
|   |--views.py (how the pages' UI look)
|--mysite/ (configure project-wide settings)
|   |--__init__.py
|   |--asgi.py
|   |--wsgi.py
|   |--settings.py (application settings, modules, databases...etc)
|   |--urls.py (specify project-wide URL locations)
|   |--wsgi.py
|--.gitignore
|--manage.py (command-line utility for administrative tasks)
|--requirements.txt (specifies dependencies)
|--staticfiles/

# Database
This application will be using PostgresQL (SQL or relational database).
- If models have changed:
  - Run ``python3 manage.py makemigrations mapnotes`` to tell Django that we changed up 
our models in mapnotes/models.py (ex: need to create new tables).
  - ``python3 manage.py migrate`` to apply those changes.
  - Open interactive shell: ``python3 manage.py shell``
  - See https://docs.djangoproject.com/en/4.0/intro/tutorial02/ for more details.

**Admin access:**
Email - jialn166@gmail.com
Username - jlin
Password - 1
With the server started, navigate to .../admin/ to view admin login page.

# Heroku 
- ``heroku pg:psql`` to connect to heroku postgres locally via CLI. You must have
the heroku CLI installed. 
- ``heroku run python manage.py shell`` run python interactive on the live heroku server
- ``heroku run python manage.py createsuperuser`` create a super user on live heroku server
- ``git push heroku local-branch-name:main `` to push and deploy changes
