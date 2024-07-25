FROM ubuntu:latest

# Install required dependencies
RUN apt-get update && \
    apt-get install -y psmisc bsdmainutils cron && \
    apt-get install -y bash sudo python3 python3-pip && \
    apt-get install -y imagemagick dnsutils git tree && \
    apt-get install -y net-tools iputils-ping coreutils && \
    apt-get install -y curl cpio jq vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install libreoffice
RUN apt-get update && \
    apt-get install -y libreoffice && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Tessaract
RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    apt-get install -y libtesseract-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY ./docker/requirements.txt /
COPY ./docker/setup_py.sh /
RUN chmod +x /setup_py.sh
RUN sh ./setup_py.sh
RUN rm /setup_py.sh /requirements.txt

# Create custom file structure
COPY ./openai_key.txt /

# Commit custom file system to determine diffs
COPY ./docker/docker.gitignore /
RUN mv docker.gitignore .gitignore
RUN git config --global user.email "office_agent_bench@universityofcalifornia.edu"
RUN git config --global user.name "office_agent_bench@universityofcalifornia.edu"
RUN git init
RUN git add -A
RUN git commit -m 'initial commit'

WORKDIR /
