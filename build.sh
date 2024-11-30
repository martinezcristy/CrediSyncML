#!/bin/bash
# Update package list and install necessary libraries
apt-get update && apt-get install -y libmysqlclient-dev

# Install Python dependencies
pip3.12 install --disable-pip-version-check --target . --upgrade -r /vercel/path1/requirements.txt
