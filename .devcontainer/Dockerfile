FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    xmlsec1 \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    pkg-config \
    default-libmysqlclient-dev \
    gnupg \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and Yarn
RUN curl -sL https://deb.nodesource.com/setup_lts.x | bash - \
    && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y nodejs yarn \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
WORKDIR /workspace

# Install Python packages
RUN pip install --upgrade pip \
    && pip install pylint black pytest flask-migrate
