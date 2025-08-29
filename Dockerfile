FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

WORKDIR /app
COPY . .

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y wget gnupg unzip

RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main"     > /etc/apt/sources.list.d/google-chrome.list

RUN apt-get update && apt-get install -y google-chrome-stable

RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

RUN playwright install && playwright install-deps