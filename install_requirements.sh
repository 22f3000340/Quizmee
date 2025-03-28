#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Installing Python..."
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip is not installed. Installing pip..."
    sudo apt update
    sudo apt install -y python3-pip
fi

echo "Installing packages from backend/requirements.txt..."
# Using --break-system-packages to override the externally-managed-environment restriction
sudo pip3 install --break-system-packages -r backend/requirements.txt

echo "Installation complete!" 