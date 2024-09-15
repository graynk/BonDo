FROM python:3.12-bullseye

WORKDIR /usr/app

RUN apt-get update && apt-get install -y espeak ffmpeg
RUN curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain stable -y
ENV PATH=/root/.cargo/bin:$PATH
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN rustup self uninstall -y

COPY test_format_timedelta.py .
COPY format_timedelta.py .
RUN python3 -m unittest test_format_timedelta.py

COPY bot.py .
COPY draw.py .
COPY ffmpeg.py .
COPY response.py .
COPY neural.py .
COPY shabaka.webp .
COPY baguette.mp4 .
COPY lebowski.jpg .
COPY font.ttf .
COPY ru_dict /usr/lib/x86_64-linux-gnu/espeak-data/

ENTRYPOINT [ "python", "-u", "bot.py" ]