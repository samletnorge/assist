# Base ERPNext image
FROM frappe/erpnext:latest

WORKDIR /home/frappe/frappe-bench

# Install assist
RUN bench get-app https://github.com/minfuel/assist.git --branch main


USER root
# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# Switch back to frappe user
USER frappe
# Entrypoint
ENTRYPOINT ["/entrypoint.sh"]
