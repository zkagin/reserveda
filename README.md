# Reserveda

Reserveda is simple reservation system that allows users to create objects that can
then be "checked out" so that only one person is using it at a time.

# Installation

The easiest way to set up Reserveda is through Pipenv, which will handle the virtual
environment and dependencies.

```
pip install pipenv
```

Once pipenv is installed, you can install all of the other project dependencies.

```
pipenv install
```

# Environment Variables

In order for Reserveda to work correctly, it will require a `.env` file containing:

```
DATABASE_URL=
SECRET_KEY=
```

# Running the app

To run the app locally using the Flask development server...

Configure the flask environment variables

```
export FLASK_APP=reserveda
export FLASK_ENV=development
```

Run the development server

```
pipenv run flask run
```

To run it with a more robust web server:

```
pipenv run gunicorn reserveda:app
```
