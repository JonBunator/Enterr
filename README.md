# Enterr
Some websites delete your account after a period of inactivity. This tool helps manage your logins by automatically logging into your accounts, ensuring they remain active.

> [!WARNING]
> This tool is still at an early stage of development. Expect breaking changes.

> [!CAUTION]
> Disclaimer: **Use of this tool may violate the Terms of Service (TOS) of the websites it interacts with.** Users are solely responsible for any consequences. The developers are not liable for misuse or damages.

<img alt="enterr logo" src=".github/images/screenshot.png"/>

## Docker compose
Create a `docker-compose.yml` and add the following. You can change the port if you want. Replace the `SECRET_KEY` with a random secret.
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
# Create a user
```bash
docker compose run enterr create_user <USERNAME> <PASSWORD>
```
```bash
docker compose run enterr create_user my_username 123456
```

# Delete a user
```bash
docker compose run enterr delete_user <USERNAME>
```
```bash
docker compose run enterr delete_user my_username
```

# Set a different password
```bash
docker compose run enterr set_password <USERNAME> <NEW_PASSWORD>
```
```bash
docker compose run enterr delete_user my_username 456789
```