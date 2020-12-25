# Pull Official Base Image.
FROM python:3.8.0-slim-buster

# Set Working Directory.
WORKDIR /usr/src/app

# Set Environment Variables.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install System Dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc postgresql \
  && apt-get clean

# Add and Install Requirements.
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Add App.
COPY . .

# Run the Server.
CMD python manage.py run -h 0.0.0.0