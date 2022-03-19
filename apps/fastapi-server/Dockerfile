FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim
WORKDIR /app
RUN apt update && apt install -y xxd
COPY requirements.txt .
RUN pip install --no-cache-dir -v -r requirements.txt
ENV PORT=3001
EXPOSE 3001
CMD ["/start-reload.sh"]
