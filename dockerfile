FROM python:3.10.13-slim-bullseye
LABEL Maintainer="Grant"
WORKDIR /app

RUN pip install --upgrade pip
RUN python3 -m pip install -U python-dotenv
RUN python3 -m pip install -U discord.py

RUN mkdir ./Databases
RUN mkdir ./cogs
RUN mkdir ./item_data
COPY *.py ./
COPY cogs/*.py ./cogs/
COPY item_data/* ./item_data

CMD  python ./main.py
