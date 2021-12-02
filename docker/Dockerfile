ARG BASE_IMAGE=ubuntu:18.04
FROM $BASE_IMAGE
LABEL maintainer="NeuML"
LABEL repository="paperetl"

# Install required packages
RUN apt-get update && \
    apt-get -y --no-install-recommends install libxml2 openjdk-8-jdk-headless openjdk-8-jre-headless python3.7 python3-pip unzip wget && \
    rm -rf /var/lib/apt/lists

# Install paperetl project and dependencies
RUN ln -sf /usr/bin/python3.7 /usr/bin/python && \
    python -m pip install --no-cache-dir -U pip wheel setuptools && \
    python -m pip install --no-cache-dir paperetl && \
    python -c "import nltk; nltk.download('punkt')"

# Install GROBID
# This method builds a trimmed down standalone service. A much simpler method is unzipping then running:
# ./gradlew install && ./gradlew run
RUN wget https://github.com/kermitt2/grobid/archive/0.6.1.zip && \
    unzip 0.6.1.zip && rm 0.6.1.zip && mv grobid-0.6.1 grobid-install && \
    cd grobid-install && ./gradlew clean assemble && \
    mkdir -p ../grobid && cd ../grobid && \
    unzip ../grobid-install/grobid-home/build/distributions/grobid-home*.zip && \
    cp ../grobid-install/grobid-service/config/config.yaml . && \
    cp ../grobid-install/grobid-service/build/libs/grobid-service*onejar.jar ./grobid-service.jar && \
    rm -rf ~/.gradle ../grobid-install grobid-home/pdf2xml/mac-64/ grobid-home/pdf2xml/win-32/ grobid-home/pdf2xml/win-64

# Cleanup build packages
RUN apt-get -y purge openjdk-8-jdk-headless && apt-get -y autoremove

# Copy paperetl scripts
RUN mkdir -p scripts
COPY scripts/ ./scripts/

# Create start script
RUN echo "#!/bin/bash" > scripts/start.sh && \
    echo "cd grobid && nohup java -jar grobid-service.jar server config.yaml > grobid.log 2>&1 &" >> scripts/start.sh && \
    echo "/bin/bash" >> scripts/start.sh && \
    chmod 755 scripts/start.sh

# Create paperetl directories
RUN mkdir -p cord19/data && \
    mkdir -p paperetl/data

# Start script
ENTRYPOINT scripts/start.sh
