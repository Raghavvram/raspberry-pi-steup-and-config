# Komodo Setup using Docker

This guide provides the steps to set up Komodo using Docker.

## 1. Create .env file

Create a `.env` file by copying the `compose.env` file.

```bash
cp compose.env .env
```

## 2. Updated mongo.compose.yaml

Here is the updated `mongo.compose.yaml` file that matches your filenames.

```yaml
services:
  mongo:
    image: mongo:latest
    restart: unless-stopped
    volumes:
      - mongo-data:/data/db
      - mongo-config:/data/configdb
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: admin@007

  core:
    image: ghcr.io/moghtech/komodo-core:latest
    restart: unless-stopped
    depends_on:
      - mongo
    ports:
      - "9120:9120"
    env_file: compose.env  # Matches your existing file
    environment:
      KOMODO_DATABASE_ADDRESS: mongo:27017
      KOMODO_DATABASE_USERNAME: admin
      KOMODO_DATABASE_PASSWORD: admin@007
    volumes:
      - repo-cache:/repo-cache
      - /etc/komodo/backups:/backups

  periphery:
    image: ghcr.io/moghtech/komodo-periphery:latest
    restart: unless-stopped
    env_file: compose.env  # Matches your existing file
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /proc:/proc
      - /etc/komodo:/etc/komodo

volumes:
  mongo-data:
  mongo-config:
  repo-cache:
```

## 3. Update compose.env with all values

Update the `compose.env` file with the following values.

```env
COMPOSE_KOMODO_IMAGE_TAG=latest
COMPOSE_KOMODO_BACKUPS_PATH=/etc/komodo/backups
KOMODO_DB_USERNAME=admin
KOMODO_DB_PASSWORD=admin@007
KOMODO_PASSKEY=komodo_secure_passkey_2025_admin007
KOMODO_HOST=http://localhost:9120
KOMODO_TITLE=Komodo-Server
KOMODO_FIRST_SERVER=https://periphery:8120
KOMODO_FIRST_SERVER_NAME=Local-Server
KOMODO_LOCAL_AUTH=true
KOMODO_INIT_ADMIN_USERNAME=admin
KOMODO_INIT_ADMIN_PASSWORD=admin@007
KOMODO_WEBHOOK_SECRET=webhook_admin007_komodo_2025
KOMODO_JWT_SECRET=jwt_admin007_komodo_secure_2025
KOMODO_MONITORING_INTERVAL=15-sec
KOMODO_RESOURCE_POLL_INTERVAL=1-hr
KOMODO_JWT_TTL=1-day
TZ=Asia/Kolkata
PERIPHERY_ROOT_DIRECTORY=/etc/komodo
PERIPHERY_PASSKEYS=komodo_secure_passkey_2025_admin007
PERIPHERY_SSL_ENABLED=true
PERIPHERY_DISABLE_TERMINALS=false
```

## 4. Deploy

Run the following commands to deploy Komodo.

```bash
sudo mkdir -p /etc/komodo/{backups,}

docker-compose -p komodo -f mongo.compose.yaml --env-file compose.env up -d
```

Now it matches your existing filenames exactly. Access: `http://localhost:9120` (admin/admin@007).

## References

[1] [https://raw.githubusercontent.com/moghtech/komodo/main/compose/mongo.compose.yaml](https://raw.githubusercontent.com/moghtech/komodo/main/compose/mongo.compose.yaml)
[2] [https://komo.do/docs/setup](https://komo.do/docs/setup)
