# Use the Alpine Linux base image
FROM alpine:latest

# Set the working directory
WORKDIR /app

# Install necessary system packages
RUN apk update && \
    apk add --no-cache gcc musl-dev python3-dev libffi-dev py3-pip && \
    apk search --no-cache sdl2 && \
    apk add --no-cache sdl2 sdl2-dev sdl2_image-dev sdl2_mixer-dev sdl2_ttf-dev

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies using pip
RUN pip3 install --upgrade pip setuptools && \
    pip3 install -r requirements.txt

# Copy the rest of the project files
COPY . .

# Set the entry point
CMD ["python3", "main.py"]
