FROM python:3.12.0a5-alpine3.17

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "wsgi:app"]