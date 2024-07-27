FROM python:3.10-slim-bullseye

WORKDIR /usr/src/

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "app.main"]
