FROM python:3.12.9-slim-bookworm

# Install the required package
RUN pip install uv

# Set the working directory
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Run the sync command
RUN uv sync

# Define the command to run the application
CMD ["uv", "run", "main.py"]