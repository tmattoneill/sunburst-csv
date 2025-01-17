# Build stage
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files from frontend directory
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source code
COPY frontend/ .

# Build the application
RUN npm run build

# Final stage
FROM nginx:alpine

# Create required directories and set permissions
RUN mkdir -p /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 777 /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 777 /etc/nginx /usr/share/nginx/html

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose the HTTP port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]