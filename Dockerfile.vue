# Dockerfile.vue
# Production use only; No conditional builds

### STAGE 1: BASE NODE BUILD ENVIRONMENT
FROM node:18-alpine AS builder

ARG NODE_ENV
ARG APP_PATH
ARG VUE_PORT
ARG VUE_APP_API_BASE_URL
ARG VUE_APP_API_ROOT_PATH
ARG VUE_APP_API_PORT

RUN echo "Build Mode: [NODE_ENV=${NODE_ENV}]"

ENV APP_PATH=${APP_PATH}
RUN echo "DEBUG: Adding WORKDIR ${APP_PATH}"
WORKDIR ${APP_PATH}

RUN apk --no-cache add curl bash

COPY frontend/package*.json ./

RUN npm install --no-cache && \
    npm install -g @vue/cli @vue/cli-service

COPY frontend/ .

### STAGE 2: PRODUCTION STAGE
SHELL ["/bin/bash", "-c"]

RUN echo "Building with NODE_ENV=$NODE_ENV" && \
    if [[ "$NODE_ENV" = "build" ]]; then \
        echo "Starting production build..." && \
        npm run build || (echo "Build failed with exit code $?" && exit 1) \
    fi

### STAGE 3: PRODUCTION SERVED BY NGINX
FROM nginx:alpine AS production

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.build.conf /etc/nginx/nginx.conf

# Set up directories and permissions
RUN mkdir -p /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 777 /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 777 /etc/nginx /usr/share/nginx/html

EXPOSE ${VUE_PORT}

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

### -- END STAGE - PRODUCTION -- ###