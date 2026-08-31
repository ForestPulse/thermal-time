# using latest as it is the only one with 3.12 support
FROM ghcr.io/osgeo/gdal:ubuntu-small-latest AS builder

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install pip and venv
RUN apt-get update && apt-get install -y python3-pip python3-venv python3-gdal curl wget tar \
 && rm -rf /var/lib/apt/lists/*

# Force real GNU coreutils - this base image ships uutils coreutils by default,
# whose `date` doesn't correctly truncate %N to milliseconds (%3N), which breaks
# Nextflow's .command.run timestamp parsing (nxf_date) under the k8s executor.
RUN apt-get update \
 && apt-get remove -y --allow-remove-essential coreutils-from-uutils \
 && apt-get install -y --reinstall coreutils-from-gnu \
 && rm -rf /var/lib/apt/lists/* \
 && date --version | head -1 \
 && date +%s%3N

# Create and activate virtual environment
RUN python3 -m venv --system-site-packages /venv
ENV PATH="/venv/bin:/app/src:$PATH"

# Upgrade pip inside the venv and install requirements
COPY requirements.txt .
RUN /venv/bin/python --version && \
    /venv/bin/pip --version && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip debug --verbose && \
    /venv/bin/pip install --only-binary=:all: --no-cache-dir -r requirements.txt

COPY . .

# Make all Python scripts executable
RUN find . -name "*.py" -exec chmod +x {} \;

# Entry point executes whatever command is passed
# ENTRYPOINT ["/bin/bash"]
