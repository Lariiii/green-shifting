FROM python:3.9-slim
WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -v -r requirements.txt
COPY ./app /app
ENV PYTHONUNBUFFERED=1
CMD ["python", "./main.py"]
