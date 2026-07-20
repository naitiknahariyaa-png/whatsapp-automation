FROM node:20-alpine

WORKDIR /app

# Install system dependencies for Playwright
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    chromium \
    firefox \
    ca-certificates \
    ttf-freefont \
    && npx playwright install --with-deps chromium

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source
COPY . .

# Build TypeScript
RUN npm run build

# Create non-root user
RUN addgroup -g 1001 -S nexus && \
    adduser -S nexus -u 1001 && \
    chown -R nexus:nexus /app

USER nexus

EXPOSE 3000

CMD ["node", "dist/index.js"]
