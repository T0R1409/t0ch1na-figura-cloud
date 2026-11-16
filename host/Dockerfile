FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home figura && mkdir /data && chown figura:figura /data
COPY --chown=figura:figura --chmod=644 server.py .
USER figura
EXPOSE 8080
CMD ["python", "server.py"]
