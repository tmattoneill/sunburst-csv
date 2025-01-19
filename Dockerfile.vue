# Dockerfile.vue
# Build stage
FROM node:18-alpine AS builder

# Build args
ARG NODE_ENV
ENV NODE_ENV=${NODE_ENV}
ARG VUE_APP_API_BASE_URL
ENV VUE_APP_API_BASE_URL=${VUE_APP_API_BASE_URL}

# Set working directory
WORKDIR /app

RUN apk --no-cache add curl bash

# Copy package files from frontend directory
COPY frontend/package*.json ./

# Install dependencies including Vue CLI globally
RUN npm install --no-cache --verbose && \
    npm install -g @vue/cli @vue/cli-service

# Copy frontend source code
COPY frontend/ .

# Build the application (only for production) with debug output
SHELL ["/bin/bash", "-c"]
RUN echo "Building with NODE_ENV=$NODE_ENV" && \
    if [[ "$NODE_ENV" = "prod" ]]; then \
        echo "Starting production build..." && \
        npm run build || (echo "Build failed with exit code $?" && exit 1) \
    fi


# For production, use nginx to serve the built files
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

# For development, use the builder stage directly
# Development stage modifications
FROM builder AS development
ENV HOST=0.0.0.0
ENV PORT=${VUE_PORT}
EXPOSE ${VUE_PORT}

# Install curl for healthcheck
RUN apk --no-cache add curl

# Create vue.config.js to ensure proper dev server configuration
RUN echo 'module.exports = { \
  devServer: { \
    host: "0.0.0.0", \
    port: parseInt(process.env.VUE_PORT || "8080"), \
    allowedHosts: "all", \
    client: { \
      webSocketURL: "auto://0.0.0.0:0/ws" \
    } \
  } \
}' > vue.config.js

CMD npm run serve -- --port ${VUE_PORT}