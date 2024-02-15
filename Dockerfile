FROM selenium/standalone-chrome

USER root
RUN apt-get update && apt-get install python3-distutils -y
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py

# Set the working directory in the container
WORKDIR /app

# Copy necessary files to docker
COPY . /app/

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /app/requirements.txt

# # Run script.py when the container launches
# CMD ["python3", "nayar_scraper.py"]

# Run a command that doesn't exit
CMD ["tail", "-f", "/dev/null"]