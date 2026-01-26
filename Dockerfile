# Base ERPNext image
FROM frappe/erpnext:latest

WORKDIR /home/frappe/frappe-bench

# Install assist
RUN bench get-app git clone https://github.com/samletnorge/assist.git --branch main
