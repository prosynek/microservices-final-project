FROM python:3.12.1
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["gunicorn",  "-c",  "gunicorn_config.py", "app:app"]