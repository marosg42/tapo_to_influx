FROM python:3.10

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src/ .

ENTRYPOINT [ "python", "tapo_to_influx.py" ]
