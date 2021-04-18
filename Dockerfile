FROM python:3.9
COPY requirements.txt /app/requirements.txt
RUN pip install -U -r /app/requirements.txt
