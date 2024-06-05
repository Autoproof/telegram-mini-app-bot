FROM --platform=linux/amd64 python:3.11
WORKDIR /opt
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .