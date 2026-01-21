#!/bin/bash
set -e

SITE_NAME="5e5899d8398b5f7b"
ASSIST_REPO="https://github.com/minfuel/assist.git"
ASSIST_BRANCH="main"

# Clone or pull Assist
if [ -d apps/assist ]; then
    echo "Pulling latest Assist..."
    git -C apps/assist pull
else
    echo "Cloning Assist..."
    bench get-app $ASSIST_REPO --branch $ASSIST_BRANCH
fi

# Install Assist if not installed
if ! bench --site $SITE_NAME list-apps | grep -q assist; then
    echo "Installing Assist on site $SITE_NAME..."
    bench --site $SITE_NAME install-app assist
fi

# Run migrations
bench --site $SITE_NAME migrate

# Keep the container alive by running SocketIO
exec node /home/frappe/frappe-bench/apps/frappe/socketio.js
