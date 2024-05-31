#!/bin/bash

# Update the package list
sudo apt update

# Install dependencies
sudo apt install -y python3 python3-pip

# Install Python packages
pip3 install ply json

echo "All dependencies are installed."
