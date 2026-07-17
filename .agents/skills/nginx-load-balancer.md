# Nginx Load Balancer Skill

## Purpose
Scale WhatsApp bot with Nginx load balancing.

## What is Nginx?
Web server + reverse proxy + load balancer.

## Setup

### 1. Install Nginx
```bash
# Ubuntu/Debian
sudo apt install nginx

# Start
sudo systemctl start nginx
```

### 2. Configure Load Balancer
```nginx
# /etc/nginx/sites-available/whatsapp-bot

upstream whatsapp_backend {
    # Least connections - routes to least busy server
    least_conn;
    
    # Backend servers (run multiple bot instances)
    server 127.0.0.1:8001 weight=5;  # Bot instance 1
    server 127.0.0.1:8002 weight=5;  # Bot instance 2
    server 127.0.0.1:8003 weight=5;  # Bot instance 3
    
    # Keep alive connections
    keepalive 32;
}

server {
    listen 80;
    server_name whatsapp-bot.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name whatsapp-bot.example.com;

    ssl_certificate /etc/ssl/certs/bot.crt;
    ssl_certificate_key /etc/ssl/private/bot.key;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20;

    location / {
        proxy_pass http://whatsapp_backend;
        
        # Headers for WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://whatsapp_backend/health;
        access_log off;
    }
}
```

### 3. Run Multiple Bot Instances
```bash
# Instance 1
PORT=8001 python main.py &

# Instance 2  
PORT=8002 python main.py &

# Instance 3
PORT=8003 python main.py &
```

### 4. Update Bot to Use Port
```python
# In webhook.py
import os

PORT = int(os.getenv("PORT", 8000))

# Update FastAPI
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok", "instance": PORT}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
```

## Load Balancing Methods

### 1. Round Robin (Default)
```nginx
upstream backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}
```

### 2. Least Connections
```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

### 3. IP Hash (Sticky Sessions)
```nginx
upstream backend {
    ip_hash;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

## Scaling Architecture

```
                    ┌─────────────┐
                    │   Nginx     │
                    │ Load Balancer│
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │ Bot     │       │ Bot     │       │ Bot     │
   │ Instance│       │ Instance│       │ Instance│
   │ :8001   │       │ :8002   │       │ :8003   │
   └────┬────┘       └────┬────┘       └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Redis     │
                    │  (Session)  │
                    └─────────────┘
```

## Features

| Feature | Description |
|---------|-------------|
| Load Balance | Distribute traffic |
| SSL Termination | HTTPS handling |
| Rate Limiting | Prevent DDoS |
| Caching | Speed up responses |
| Gzip | Compress responses |

## Environment Variables
```
NGINX_HOST=0.0.0.0
NGINX_PORT=80
BACKEND_PORTS=8001,8002,8003
```

## Health Checks
```nginx
upstream backend {
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8002 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8003 max_fails=3 fail_timeout=30s;
}
```

## More Info
- Website: https://nginx.org
- GitHub: https://github.com/nginx/nginx
