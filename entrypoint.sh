#!/bin/bash
set -e

SITE_NAME="5b832ac7859aa86c"
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


# shellcheck disable=SC2016
envsubst '${BACKEND}
  ${SOCKETIO}
  ${UPSTREAM_REAL_IP_ADDRESS}
  ${UPSTREAM_REAL_IP_HEADER}
  ${UPSTREAM_REAL_IP_RECURSIVE}
  ${FRAPPE_SITE_NAME_HEADER}
  ${PROXY_READ_TIMEOUT}
	${CLIENT_MAX_BODY_SIZE}' \
  </templates/nginx/frappe.conf.template >/etc/nginx/conf.d/frappe.conf

nginx -g 'daemon off;'

