FROM python:3.10-slim

# #AB0=>2:0 A8AB5<=KE 7028A8<>AB59
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# #AB0=>2:0 @01>G59 48@5:B>@88
WORKDIR /app

# >?8@>20=85 requirements.txt 8 CAB0=>2:0 7028A8<>AB59
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary

# >?8@>20=85 2A53> ?@>5:B0
COPY . .

# !>740=85 48@5:B>@89 4;O AB0B8:8 8 <5480
RUN mkdir -p /app/staticfiles /app/media

# !1>@ AB0B8:8 1C45B 2K?>;=OBLAO 2 docker-compose command
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

EXPOSE 8000
