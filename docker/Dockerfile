ARG BASE_IMAGE=python:3.9-slim
FROM $BASE_IMAGE
LABEL maintainer="NeuML"
LABEL repository="paperetl"

# Set Python version (i.e. 3, 3.9)
ARG PYTHON_VERSION=3

# Locale environment variables
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install required packages
RUN apt-get update && \
    apt-get -y --no-install-recommends install libxml2 default-jdk-headless default-jre-headless python${PYTHON_VERSION} python3-pip unzip wget && \
    rm -rf /var/lib/apt/lists

# Install paperetl project and dependencies
RUN ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python && \
    python -m pip install --no-cache-dir -U pip wheel setuptools && \
    python -m pip install --no-cache-dir paperetl && \
    python -c "import nltk; nltk.download(['punkt', 'punkt_tab', 'averaged_perceptron_tagger_eng'])"

# Install GROBID
# This method builds a trimmed down standalone service. A much simpler method is unzipping then running:
# ./gradlew install && ./gradlew run
RUN wget https://github.com/kermitt2/grobid/archive/0.8.1.zip && \
    unzip 0.8.1.zip && rm 0.8.1.zip && mv grobid-0.8.1 grobid-install && \
    cd grobid-install && ./gradlew clean assemble && \
    mkdir -p ../grobid && cd ../grobid && \
    unzip ../grobid-install/grobid-home/build/distributions/grobid-home*.zip && \
    cp ../grobid-install/grobid-home/config/grobid.yaml config.yaml && \
    cp ../grobid-install/grobid-service/build/libs/grobid-service*onejar.jar ./grobid-service.jar && \
    rm -rf ~/.gradle ../grobid-install grobid-home/pdf2xml/mac-64/ grobid-home/pdf2xml/win-32/ grobid-home/pdf2xml/win-64

# Cleanup build packages
RUN apt-get -y purge default-jdk-headless && apt-get -y autoremove

# Create scripts directory for start.sh
RUN mkdir -p scripts

# Create start script
RUN echo "#!/bin/bash" > scripts/start.sh && \
    echo "cd grobid && nohup java -jar grobid-service.jar server config.yaml > grobid.log 2>&1 &" >> scripts/start.sh && \
    echo "/bin/bash" >> scripts/start.sh && \
    chmod 755 scripts/start.sh

# Create paperetl directories
RUN mkdir -p paperetl/data

# Start script
ENTRYPOINT ["scripts/start.sh"]
