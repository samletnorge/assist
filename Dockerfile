# Base ERPNext image
FROM frappe/erpnext:latest

WORKDIR /home/frappe/frappe-bench

# Install assist
RUN bench get-app https://github.com/minfuel/assist.git --branch main

