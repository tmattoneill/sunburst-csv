# Dockerfile.vue
# Build stage
FROM node:18-alpine AS builder

# Build args
ARG NODE_ENV=production

# Set working directory
WORKDIR /app

RUN apk --no-cache add curl

# Copy package files from frontend directory
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source code
COPY frontend/ .

# Build the application (only for production)
RUN if [ "$NODE_ENV" = "production" ]; then npm run build; fi

# For production, use nginx to serve the built files
FROM nginx:alpine AS production

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create required directories and set permissions
RUN mkdir -p /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 777 /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 777 /etc/nginx /usr/share/nginx/html

# Expose the HTTP port
EXPOSE 8080

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
    port: 8080, \
    allowedHosts: "all", \
    client: { \
      webSocketURL: "auto://0.0.0.0:0/ws" \
    } \
  } \
}' > vue.config.js

CMD npm run serve -- --port ${VUE_PORT}