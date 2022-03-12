import os
import sys

REQUIRED_ENV_VAR = [
    # Database
    "PROJ_5_DB_HOST",
    "PROJ_5_DB_USERNAME",
    "PROJ_5_DB_PASSWORD",
    "PROJ_5_DB_NAME",
    # Storage
    "PROJ_5_STORAGE_URL",
    "PROJ_5_STORAGE_CREDENTIAL_KEY",
    # Django superuser
    "DJANGO_SUPERUSER_EMAIL",
    "DJANGO_SUPERUSER_USERNAME",
    "DJANGO_SUPERUSER_PASSWORD",
    # Django
    "PROJ_5_DJANGO_SECRET_KEY",
]


def env_var_check():
    # Check if all required env var is set
    for v in REQUIRED_ENV_VAR:
        if not os.getenv(v):
            raise ValueError(v + " is not set")


if __name__ == '__main__':
    try:
        env_var_check()
    except ValueError as e:
        print("Error:", e)
        sys.exit(1)
    print("All required environment variables are set")
