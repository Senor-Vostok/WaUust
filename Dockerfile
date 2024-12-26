FROM python:3.10-slim

WORKDIR /app

COPY app/requirements.txt /app/app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python", "app/main.py"]
