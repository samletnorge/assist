# Base image: latest ERPNext
FROM frappe/erpnext:latest

WORKDIR /home/frappe/frappe-bench

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Entrypoint
ENTRYPOINT ["/entrypoint.sh"]
