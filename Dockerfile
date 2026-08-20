FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt
COPY..
ENV PORT=8080
ENV TZ=America/Sao_Paulo
EXPOSE 8080
CMD ["python", "main.py"]
