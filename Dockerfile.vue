# Use a lightweight Node.js image for build
FROM node:18-alpine as build

# Set the working directory
WORKDIR /app

# Install dependencies and build the app
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend ./
RUN npm run build

# Serve the built files using Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80