# MuzBot

## Download music from Youtube music to Telegram

### Description

The bot was created to download music to Telegram. The initial idea was to blur the lines between different music listening platforms.

### Deploying

At first create file `.env` in project's root folder or just add envs into your system vars. An example of an `.env` file can be found in `.env.example`.

**Caveat**: Bot won't fail to start if you haven't specified `LOKI_URL`. In other case it will be stopped with `critical` error if `loki` is unhealthy

Then create a `data/` folder and a `docker-compose.yaml`  file. Here is an example with deploying `grafana/loki` log system:

### ⚠️ EXPERIMENTAL

Some features in `alpha` and `beta` versions are marked as **experimental** and won't launch without explicit configuration in `.env` or system vars.

```yaml
services:
  bot:
    image: ghcr.io/upcomer2077/muzbot:latest
    container_name: MuzBot
    restart: unless-stopped

    env_file:
      - ./.env
    init: true
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - DB_NAME=${DB_NAME}
      - TRACKS_PER_LIMIT=${TRACKS_PER_LIMIT}
      - QUERY_DOWNLOAD_LIMIT_SECS=${QUERY_DOWNLOAD_LIMIT_SECS}
      - CPU_COUNT=${CPU_COUNT}
      - EXPERIMENTAL=${EXPERIMENTAL}
      - BACKUP_EVERY_N_DAYS=${BACKUP_EVERY_N_DAYS}

    volumes:
       - type: bind
         source: ./data
         target: /muzbot/data
    networks:
      - bot
    # REMOVE IF YOU DON'T NEED LOKI 
    depends_on:
      loki:
        condition: service_healthy
        required: false
    healthcheck:
      test: ["CMD-SHELL", "python healthcheck.py > /proc/1/fd/1 2>&1 || exit 1"]
      interval: 5m    
      timeout: 8s      
      retries: 3       
      start_period: 1s 

  loki:
    image: grafana/loki:3.0.0
    container_name: loki_service
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - bot
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:3100/ready | grep -q 'ready' || exit 1"]
      interval: 3s    
      timeout: 2s      
      retries: 5      
      start_period: 2s 

  grafana:
    image: grafana/grafana:11.0.0
    container_name: grafana_service
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - bot
    depends_on:
      - loki
    
networks:
  bot:
    driver: bridge
```

### Technologies

- `python` - main coding language
- `ffmpeg` - audio conversion
- `aiogram` - framework upon telegram API
- `yt-dlp` & `ytmusicapi` - searching and downloading music
- `Sqlite` & `peewee` - portable lightweight database and ORM manager
- `Loki/grafana` - logger
- `Docker` - containerization system
- `Github Actions` - runs CI/CD pipelines

Also bot uses a `Dual logging` pattern which means you are always able to see logs in your STD output.

## Good luck
