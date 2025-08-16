ARG PYTHON_IMAGE_VERSION=3.12.11-slim-bookworm

# Stage 1: Build dependency wheels (wheelhouse)
FROM python:${PYTHON_IMAGE_VERSION} AS deps

COPY requirements.txt /wheels/requirements.txt
RUN pip wheel --wheel-dir=/wheels -r /wheels/requirements.txt

# Stage 2: Final runtime image
FROM python:${PYTHON_IMAGE_VERSION}

ARG ENV=dev
ENV ENV=${ENV}
ARG UID=1000

# Set project directory
ENV HOME=/home/${UID}
ENV PROJECT_ROOT=/app
ENV PYTHONPATH=${PROJECT_ROOT}
WORKDIR ${PROJECT_ROOT}
RUN mkdir -p ${HOME} && chown -R ${UID} ${HOME}

# Set the timezone to Asia/Seoul
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

# Install system dependencies
RUN apt-get update -qqy && \
    apt-get install -y --no-install-recommends \
        git build-essential && \
    apt-get autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf ~/.cache

# Install Python dependencies from prebuilt wheels (offline)
COPY --from=deps /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r /wheels/requirements.txt && \
    rm -rf /wheels

# Copy the project files
COPY src ${PROJECT_ROOT}/src
COPY config/__init__.py ${PROJECT_ROOT}/config/__init__.py
COPY config/config.${ENV}.yaml ${PROJECT_ROOT}/config/config.yaml
COPY mappings ${PROJECT_ROOT}/mappings
RUN chown -R ${UID} ${PROJECT_ROOT}