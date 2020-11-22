FROM python:3.9-buster

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y espeak ffmpeg
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .
COPY shabaka.webp .
COPY baguette.mp4 .
COPY times-new-roman.ttf .
COPY ru_dict /usr/lib/x86_64-linux-gnu/espeak-data/

CMD [ "python", "./bot.py" ]