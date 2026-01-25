# Base ERPNext image
FROM frappe/erpnext:latest

WORKDIR /home/frappe/frappe-bench

# Install assist
RUN bench get-app git clone https://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@github.com/samletnorge/assist.git --branch main

