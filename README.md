CSS 436 Cloud Computing Final Project 
Members: Jay, Jaeha, Mehak, Duncan

# Summary
What: Django (Python-based framework) application that provides a map view of 
notes saved around the world. Users can write and save notes, then select whichever location
on the world map they would like the note to be attached to.

# Quickstart
Prerequisites: Python 3.9, Django (check with python -m django --version)

Run ``virtualenv ~/virt`` to create a python virtual environment.
To run the application locally, enter ``source ~/virt/bin/activate`` to activate a virtual
environment. Then, type: ``python3 manage.py runserver``. 
- Type CTRL+C when you want to stop the local web server.
- To change the server port, pass the number as cmdline arg: ``python3 manage.py runserver 8080``
- How to deploy with Elastic Beanstalk: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html 

# Project Structure
Below is a tree of the current project. Files of note have comments in parentheses next to their names.

frontend/
|--.ebextensions/
|   |--django.config (Elastic Beanstalk config, where to start application)
|--mapnotes/ (houses our actual application)
|   |--migrations/
|       |--__init__.py
|   |--__init__.py
|   |--admin.py
|   |--app.py
|   |--models.py
|   |--tests.py
|   |--views.py
|--mysite/ (configure project-wide settings)
|   |--__init__.py
|   |--asgi.py
|   |--wsgi.py
|   |--settings.py
|   |--urls.py
|   |--wsgi.py
|--.gitignore
|--db.sqlite3
|--manage.py (command-line utility for administrative tasks)
|--requirements.txt (specifies dependencies)

# Database
This application will be using PostgresQL (SQL or relational database).
- If models have changed:
  - Run ``python3 manage.py makemigrations mysite`` to tell Django that we changed up 
our models in mapnotes/models.py (ex: need to create new tables).
  - ``python3 manage.py migrate`` to apply those changes.
  - Open interactive shell: ``python3 manage.py shell``
  - See https://docs.djangoproject.com/en/4.0/intro/tutorial02/ for more details.

**Admin access:**
Email - jialn166@gmail.com
Username - jlin
Password - 1
With the server started, navigate to .../admin/ to view admin login page.

