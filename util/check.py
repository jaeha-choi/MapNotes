import os
import sys

REQUIRED_ENV_VAR = ["PROJ_5_DB_HOST", "PROJ_5_DB_USERNAME", "PROJ_5_DB_PASSWORD", "PROJ_5_DB_NAME",
                    "PROJ_5_DJANGO_SECRET_KEY", "PROJ_5_TAKEOUT_DIRECTORY", "PROJ_5_STORAGE_URL",
                    "PROJ_5_STORAGE_CREDENTIAL_KEY", "PROJ_5_STORAGE_CONTAINER_NAME", "DJANGO_SUPERUSER_EMAIL"]


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
