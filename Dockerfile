# Single-Stage Dockerfile for Production
# This builds a larger image but is simpler and more reliable,
# as it keeps the full project context needed by the reflex build process.

FROM python:3.12-alpine

# Install all necessary OS dependencies for both build and runtime.
# This includes C build tools and Node.js.
RUN apk add --no-cache gcc musl-dev linux-headers bash curl nodejs npm

WORKDIR /app

# Install all Python dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application source code.
COPY . .

# The command to run the application in production mode.
# This compiles and runs the app on the server when the container starts.
CMD ["reflex", "run", "--env", "prod"]
