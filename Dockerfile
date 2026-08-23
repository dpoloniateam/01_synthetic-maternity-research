# Synthetic Design Laboratory 2 — container image (development 9, 23 Aug 2026)
FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
COPY requirements.lock /app/requirements.lock
RUN pip install -r /app/requirements.lock
COPY . /app
# Secrets come from the platform (Key Vault / Secrets Manager / Secret Manager) as environment variables; no .env in the image
ENV EXPERIMENT_CONFIG=config/experiment.yaml SDL_RUN_DIR=/data/runs/current SDL_COST_HALT_USD=50
VOLUME ["/data"]
ENTRYPOINT ["python", "run_experiment.py"]
CMD ["--arm", "P", "--limit", "30", "--repetitions", "1"]
