# Stage 1: Build
FROM node:18-alpine AS builder

# Arguments
ARG APP_PATH="/app"

# Environment Variables
ENV NODE_ENV=production
ENV DEBUG=webpack:*
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Set the working directory inside the container
WORKDIR ${APP_PATH}

# Install dependencies for Alpine
RUN apk --no-cache add curl bash

# Copy package.json and install dependencies INSIDE the container
COPY frontend/package*.json ./

# Ensure dependencies are installed INSIDE the container
RUN npm install --no-cache && npm install -g @vue/cli @vue/cli-service

# Copy the rest of the frontend source code
COPY frontend/ .

# Expose Vue dev server port
EXPOSE 8080

# Run Vue CLI server (binds to all interfaces)
CMD ["npm", "run", "serve"]
