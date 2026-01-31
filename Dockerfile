# Base ERPNext image
FROM frappe/erpnext:latest

WORKDIR /home/frappe/frappe-bench

# Install missing Python dependencies
RUN /home/frappe/frappe-bench/env/bin/pip install bleach

# Install assist
RUN bench get-app git clone https://github.com/samletnorge/assist.git --branch main
