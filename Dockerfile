# Base ERPNext image
FROM frappe/erpnext:latest

WORKDIR /home/frappe/frappe-bench

# Clone assist if not already present
RUN git clone --branch main https://github.com/minfuel/assist.git apps/assist

# Install assist
RUN bench get-app apps/assist . 


# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Entrypoint
ENTRYPOINT ["/entrypoint.sh"]
