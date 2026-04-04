FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install flask cassandra-driver flask-cors

EXPOSE 5000

CMD ["python", "app.py"]