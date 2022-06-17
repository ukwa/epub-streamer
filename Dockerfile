FROM python:3.9

WORKDIR /usr/src/access

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Override this to mount the service at a prefix, e.g. /api/v1/
ENV ROOT_PATH="/"

# Override the worker count:
ENV WORKERS=2

# Run command with sh so env vars are substituted:
CMD ["sh", "-c", "uvicorn streamer:app --host 0.0.0.0 --port 8000 --root-path ${ROOT_PATH} --workers ${WORKERS}"]


