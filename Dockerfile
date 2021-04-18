FROM python:3.9.4
COPY requirements.txt /app/requirements.txt
RUN pip install -U -r /app/requirements.txt
