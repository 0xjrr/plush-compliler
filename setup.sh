#!/bin/bash

# Update the package list
sudo apt update

# Install dependencies
sudo apt install -y python3 python3-pip

# Install LLVM and Clang
sudo apt install -y llvm clang

# Install Python packages
pip3 install -r requirements.txt

echo "All dependencies are installed."
