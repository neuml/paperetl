#!/bin/bash

# Download and unpack study model
wget -N https://github.com/neuml/paperetl/releases/download/v1.2.0/study.tar.gz -P /tmp
tar -xvzf /tmp/study.tar.gz -C /tmp

# Move into the specified directory
mkdir -p $1
mv /tmp/paperetl/models/* $1
