FROM python:3.12.1
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD ["gunicorn",  "-c",  "gunicorn_config.py", "spotify_service:app"]