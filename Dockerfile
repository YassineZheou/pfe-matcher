FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY pfe_matcher ./pfe_matcher
ENV PFE_DB=/data/pfe.db
VOLUME /data
EXPOSE 8000
CMD ["uvicorn", "pfe_matcher.api:app", "--host", "0.0.0.0", "--port", "8000"]
