# 1. Use an official Python runtime as a parent image
# python:3.12-slim is a good choice as it's lightweight.
FROM python:3.12-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the requirements file into the container at /app
# This is done first to leverage Docker's layer caching. If requirements.txt
# doesn't change, this layer won't be rebuilt, speeding up future builds.
COPY requirements.txt .

# 4. Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the pip cache, which reduces the image size.
# --upgrade pip: Ensures we have the latest version of pip.
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 5. Copy the backend application code into the container at /app
# This copies your 'backend' directory into the container.
COPY ./backend ./backend

# 6. Make port 8000 available to the world outside this container
# This documents that the container listens on this port.
EXPOSE 8000

# 7. Define the command to run the application
# Use 0.0.0.0 to make the app accessible from outside the container.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]