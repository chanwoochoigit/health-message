import reflex as rx
import os

# Read API_URL from environment, with fallback for local development
# When running in Docker Compose, this will be set to http://localhost:8000
# which allows the browser to connect to the backend running on the host
api_url = os.environ.get("API_URL", "http://localhost:8000")

config = rx.Config(
    app_name="hmsg",
    api_url=api_url,
    plugins=[rx.plugins.TailwindV3Plugin()],
    show_built_with_reflex=False
)