FROM python:3.12-slim
COPY --from=hashicorp/terraform:1.9 /bin/terraform /usr/local/bin/terraform
RUN apt-get update && apt-get install -y --no-install-recommends openssh-client && rm -rf /var/lib/apt/lists/*
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app app
COPY docs docs
COPY terraform terraform
RUN useradd -m -u 1000 appuser && mkdir /srv/data && chown appuser /srv/data
USER appuser
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--chdir", "app", "--timeout", "120", "main:app"]
