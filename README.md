<img alt="enterr logo" src=".github/images/logo.png" width="350"/>

# Website Auto-Login Tool
[![Enterr license](https://img.shields.io/github/license/JonBunator/Enterr?color=8dbf9f)](https://github.com/JonBunator/Enterr/blob/main/LICENSE)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/JonBunator/Enterr?color=8dbf9f)](https://github.com/JonBunator/Enterr/releases)
[![Docker Image](https://img.shields.io/badge/Docker-GitHub%20Container%20Registry-8dbf9f?logo=docker)](https://github.com/JonBunator/Enterr/pkgs/container/enterr)
[![Made with Love](https://img.shields.io/badge/Made%20with%20%E2%9D%A4%20by-JonBunator-8dbf9f)](https://github.com/JonBunator)

Some websites delete your account after a period of inactivity. Enterr helps manage your logins by automatically logging into your accounts, ensuring they remain active.

> [!WARNING]
> This tool is still at an early stage of development. Expect breaking changes.

> [!CAUTION]
> Disclaimer: **Use of this tool may violate the Terms of Service (TOS) of the websites it interacts with.** Users are solely responsible for any consequences. The developers are not liable for misuse or damages.

<img alt="enterr screenshot" src=".github/images/screenshot.png"/>

## Docker compose
Create a `docker-compose.yml` and add the following. You can change the port if you want. Replace `MY_RANDOM_SECRET` with a random secret.
```yml
services:
  enterr:
    container_name: enterr
    image: ghcr.io/jonbunator/enterr:latest
    environment:
      - SECRET_KEY=MY_RANDOM_SECRET
    volumes:
      - ./config:/config
    ports:
      - "7653:7653"
    restart: unless-stopped
```
Then start the container:
```bash
docker compose up -d
```
You can access the ui via `http://localhost:7653`

## User Management
The following commands are intended for use with Docker Compose. If you are not using Docker Compose, or are managing containers through tools like [Portainer](https://portainer.io) or [Unraid](https://unraid.net), please follow this guide instead: [User Management without Docker Compose](https://github.com/JonBunator/Enterr/wiki/User-Management-without-Docker-Compose)

### Create a user
```bash
docker compose run --rm enterr create_user <USERNAME> <PASSWORD>
```
```bash
docker compose run --rm enterr create_user my_username 123456
```

### Delete a user
```bash
docker compose run --rm enterr delete_user <USERNAME>
```
```bash
docker compose run --rm enterr delete_user my_username
```

### Set a different password
```bash
docker compose run --rm enterr set_password <USERNAME> <NEW_PASSWORD>
```
```bash
docker compose run --rm enterr set_password my_username 456789
```