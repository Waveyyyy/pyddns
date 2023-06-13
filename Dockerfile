# syntax=docker/dockerfile:1
FROM alpine:latest

WORKDIR /app

# Copy contents of current directory to image
COPY ddns/ .

# Install python and pip
RUN apk add --no-cache python3 py3-pip 

# Install requirements to build minupnpc
RUN apk add --no-cache g++ make python3-dev

# Copy requirements.txt over
COPY requirements.txt requirements.txt

# Install requirements
RUN pip3 install -r requirements.txt

# Run the main script
CMD [ "python3", "main.py" ]
