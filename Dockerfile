FROM python:3.7

COPY . /app
WORKDIR /app

EXPOSE 5000

VOLUME "/app/data/db"
VOLUME "/app/data/logs"

# Set the timezone for the container to local time
ENV TZ=Australia/Perth
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install the python dependencies
RUN pip install -r requirements.txt

# Start the app
ENTRYPOINT [ "python3", "run.py" ]
