# Stage 1: Build the frontend using Node.js
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies and build the Vue app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve the app with Nginx
FROM nginx:alpine

# Copy the built files to Nginx's default HTML directory
COPY --from=build /app/dist /usr/share/nginx/html

# Expose the default Nginx port
EXPOSE 80

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
