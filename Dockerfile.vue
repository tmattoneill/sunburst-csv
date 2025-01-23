# Dockerfile.vue

### STAGE 1: BASE NODE BUILD ENVIRONMENT
FROM node:18-alpine AS builder

ARG NODE_ENV
ARG APP_PATH
ARG VUE_APP_API_BASE_URL
ARG HOST
ARG PORT

RUN echo "Build Mode: [NODE_ENV=${NODE_ENV}]"

WORKDIR ${APP_PATH}

RUN apk --no-cache add curl bash
COPY frontend/package*.json ./
RUN npm install --no-cache --verbose && \
    npm install -g @vue/cli @vue/cli-service

COPY frontend/ .

### STAGE 2: PRODUCTION STAGE
SHELL ["/bin/bash", "-c"]

RUN echo "Building with NODE_ENV=$NODE_ENV" && \
    if [[ "$NODE_ENV" = "prod" ]]; then \
        echo "Starting production build..." && \
        npm run build || (echo "Build failed with exit code $?" && exit 1) \
    fi

### STAGE 3: PRODUCTION SERVED BY NGINX
FROM nginx:alpine AS production

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.${NODE_ENV}.conf /etc/nginx/nginx.conf

# Create required directories and set permissions
RUN mkdir -p /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 777 /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 777 /etc/nginx /usr/share/nginx/html

# Expose the HTTP port
EXPOSE ${VUE_PORT}

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

### -- END STAGE - PRODUCTION -- ###

### STAGE 4: DEVELOPMENT STAGE
FROM builder AS development
ENV HOST=${HOST}
ENV PORT=${VUE_PORT}
EXPOSE ${VUE_PORT}

# Install curl for healthcheck
RUN apk --no-cache add curl

# Create vue.config.js to ensure proper dev server configuration
RUN echo 'module.exports = { \
  devServer: { \
    host: "'${HOST:-0.0.0.0}'", \
    port: parseInt(process.env.VUE_PORT || "'${PORT:-8080}'"), \
    allowedHosts: "all", \
    client: { \
      webSocketURL: "auto://'${HOST:-0.0.0.0}':0/ws" \
    } \
  } \
}' > vue.config.js

CMD npm run serve -- --port ${VUE_PORT}