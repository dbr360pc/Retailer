FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    gnupg2 \
    curl \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libgbm1 \
    libxshmfence1 \
    libxcomposite1 \
    libxrandr2 \
    libu2f-udev \
    libvulkan1 \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-unifont \
    libgdk-pixbuf-xlib-2.0-0 \
    libjpeg62-turbo \
    libwebp-dev \
    xdg-utils \
    libappindicator3-1 && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

RUN pip install playwright && playwright install chromium firefox
