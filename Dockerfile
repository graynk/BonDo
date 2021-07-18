FROM python:3.9-buster

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y espeak ffmpeg
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY test_format_timedelta.py .
COPY format_timedelta.py .
RUN python3 -m unittest test_format_timedelta.py

COPY bot.py .
COPY shabaka.webp .
COPY baguette.mp4 .
COPY times-new-roman.ttf .
COPY ru_dict /usr/lib/x86_64-linux-gnu/espeak-data/

ENTRYPOINT [ "python", "./bot.py" ]