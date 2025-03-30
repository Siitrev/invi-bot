FROM python:3.11-alpine3.18

COPY requirements.txt /app/

WORKDIR /app

EXPOSE 10000

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]