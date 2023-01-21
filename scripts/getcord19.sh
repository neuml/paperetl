#!/bin/bash

# Get target date, default to latest file
DATE=${2:-"2022-06-02"}

# Create CORD-19 directory
mkdir -p $1 && cd $1

# Get dataset file
wget -N https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases/cord-19_$DATE.tar.gz

# Unpack dataset file
tar -xvzf cord-19_$DATE.tar.gz

# Move content to current directory
tar -xvzf $DATE/document_parses.tar.gz -C .
mv $DATE/metadata.csv .
