# Dockerfile.vue
# Build stage
FROM node:18-alpine AS builder

# Build args
ARG NODE_ENV=production

# Set working directory
WORKDIR /app

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
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

# For development, use the builder stage directly
FROM builder AS development
CMD ["npm", "run", "serve"]