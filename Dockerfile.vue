# Use Node.js to build the frontend
FROM node:18 as build

# Create a working directory
WORKDIR /frontend

# Copy package.json and package-lock.json
COPY ./frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY ./frontend ./

# Build the production files
RUN npm run build

# Use nginx to serve the frontend
FROM nginx:alpine

# Copy the built files to the nginx HTML folder
COPY --from=build /frontend/dist /usr/share/nginx/html

# Expose the HTTP port
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
