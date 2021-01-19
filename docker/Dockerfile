FROM ubuntu:18.04
LABEL maintainer="NeuML"
LABEL repository="paperetl"

# Install required packages
RUN apt-get update && \
    apt-get -y --no-install-recommends install libxml2 openjdk-8-jdk python3.7 python3-pip unzip wget && \
    rm -rf /var/lib/apt/lists

# Install paperetl project and dependencies
RUN ln -s /usr/bin/python3.7 /usr/bin/python && \
    python -m pip install --no-cache-dir -U pip wheel setuptools && \
    python -m pip install --no-cache-dir https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.2.5/en_core_sci_md-0.2.5.tar.gz

# Install GROBID
RUN wget https://github.com/kermitt2/grobid/archive/0.6.1.zip && \
    unzip 0.6.1.zip && rm 0.6.1.zip && \
    cd grobid-0.6.1 && ./gradlew install

# Copy paperetl scripts
RUN mkdir scripts
COPY scripts/ ./scripts/

# Create start script
RUN echo "#!/bin/bash" > scripts/start.sh && \
    echo "cd grobid-0.6.1 && nohup ./gradlew run > grobid.log 2>&1 &" >> scripts/start.sh && \
    echo "/bin/bash" >> scripts/start.sh && \
    chmod 755 scripts/start.sh

# Create paperetl directories
RUN mkdir -p cord19/data && \
    mkdir -p paperetl/data

# Install study models
RUN scripts/getstudy.sh cord19/models && \
    scripts/getstudy.sh paperetl/models

COPY . /code/paperetl/
RUN python -m pip install --no-cache-dir /code/paperetl scikit-learn==0.23.1 && \
    python -c "import nltk; nltk.download('punkt')"

# Start script
ENTRYPOINT scripts/start.sh
