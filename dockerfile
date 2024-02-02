FROM python:3.9.18-alpine

WORKDIR /fetcher

COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a directory for data
RUN mkdir -p /data

COPY crontab /etc/crontabs/root
RUN chmod 0644 /etc/crontabs/root
RUN touch /var/log/cron.log
COPY start.sh /start.sh
RUN chmod +x /start.sh


# Run the start.sh script
CMD ["/start.sh"]


