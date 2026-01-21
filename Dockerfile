# Base ERPNext image
FROM frappe/erpnext:latest

WORKDIR /home/frappe/frappe-bench

# Install assist
RUN bench get-app https://github.com/minfuel/assist.git --branch main



# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
# Entrypoint
ENTRYPOINT ["/entrypoint.sh"]
