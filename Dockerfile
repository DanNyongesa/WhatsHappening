FROM mcr.microsoft.com/azure-functions/python:3.0-python3.7

# Adding trusting keys to apt and Google Chrome to the repositories
# then Updating apt and install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get -y update \
    && apt-get install -y google-chrome-stable curl \
    && apt-get install -yqq unzip \
    && pip install --upgrade pip


# Download and install the Chrome Driver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
# Set display port as an environment variable
ENV DISPLAY=:99
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app/src
ENV AzureWebJobsScriptRoot=/app/src \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY ./prod.requirements.txt /requirements.txt

RUN pip install -r /requirements.txt


WORKDIR /app/src


#Copy source code
COPY . /app/src



