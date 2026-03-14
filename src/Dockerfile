# ------------------- BUILD FRONTEND -------------------
FROM node:24-slim AS frontend
WORKDIR /app/frontend
COPY frontend/ .
RUN npm install
RUN npm run build

# ------------ COMBINE BACKEND AND FRONTEND ------------
FROM ubuntu:24.04
WORKDIR /app
COPY --from=frontend /app/frontend/dist /app/frontend/dist

ENV PYTHONPATH=/app/backend/src:$PYTHONPATH
ENV DISPLAY=:99
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
ENV DEBIAN_FRONTEND=noninteractive

#======================
# Locale Configuration
#======================
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata locales
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN echo "LANG=en_US.UTF-8" > /etc/locale.conf
RUN locale-gen en_US.UTF-8

#===========================
# Fingerprint Configuration
#===========================
RUN apt-get update && \
    apt install -y fonts-liberation fonts-noto-color-emoji libvulkan1 libnss3 libatk-bridge2.0-0 libcups2 libxcomposite1 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 && \
    apt install -y fonts-freefont-ttf fonts-dejavu-core fonts-ubuntu fonts-roboto fonts-droid-fallback

#======================
# Install Common Fonts
#======================
RUN apt-get update && \
    apt-get install -y \
    fonts-liberation2 \
    fonts-font-awesome \
    fonts-terminus \
    fonts-powerline \
    fonts-open-sans \
    fonts-mononoki \
    fonts-lato

#============================
# Install Linux Dependencies
#============================
RUN apt-get update && \
    apt-get install -y \
    dbus-x11 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libasound2t64 \
    libu2f-udev \
    libwayland-client0 \
    libx11-6 \
    libx11-xcb1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0

#=================================
# Install Bash Command Line Tools
#=================================
RUN apt-get update && \
    apt-get -qy --no-install-recommends install \
    curl \
    sudo \
    unzip \
    wget \
    xvfb

#================
# Install Chrome
#================
RUN apt-get update && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm ./google-chrome-stable_current_amd64.deb


#================
# Install Python
#================
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.13 python3.13-venv python3.13-dev python3.13-tk
ENV PATH="/app/backend/venv/bin:$PATH"    

#===============
# Cleanup
#===============
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#===============
# Install app dependencies
#===============
WORKDIR /app/backend
COPY backend/src /app/backend/src
COPY backend/src/user_management.py /app/backend/src/user_management.py
COPY entrypoint.sh /app/entrypoint.sh
COPY start.sh /app/start.sh

USER root
RUN sed -i 's/\r$//' /app/entrypoint.sh /app/start.sh && \
    chmod +x /app/entrypoint.sh /app/start.sh
RUN python3.13 -m venv venv
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#================
# Setup seleniumbase
#================
RUN seleniumbase get chromedriver --path

EXPOSE 7653
ENV RUN_MODE=production
VOLUME /config

HEALTHCHECK --interval=15m --timeout=30s --start-period=5s --retries=3 CMD [ "curl", "http://localhost:7653/api/health" ]
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/app/start.sh"]
