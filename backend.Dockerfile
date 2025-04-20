FROM python:3.11
WORKDIR /app

RUN apt-get update && apt-get install -y 
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 8002
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]