FROM python:3.9.19-alpine

WORKDIR /fetcher

# Install curl and nano fur debugging
RUN apk update && apk add --no-cache curl nano

# Copy the requirements file separately to leverage Docker cache
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