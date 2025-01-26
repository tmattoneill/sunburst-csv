FROM node:18-alpine AS builder

ARG NODE_ENV
ARG APP_PATH
ARG VUE_PORT
ARG VUE_APP_API_ROOT_PATH

ENV NODE_ENV=production
ENV DEBUG=webpack:*
ENV NODE_OPTIONS="--max-old-space-size=4096"

ENV APP_PATH=${APP_PATH}
WORKDIR ${APP_PATH}

RUN apk --no-cache add curl bash

COPY frontend/package*.json ./
RUN npm install --no-cache && \
    npm install -g @vue/cli @vue/cli-service

COPY frontend/ .

RUN echo "Current directory: $PWD" && \
    ls -la && \
    echo "Building with NODE_ENV=$NODE_ENV" && \
    npm run build --verbose

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.build.conf /etc/nginx/nginx.conf

RUN mkdir -p /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 777 /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 777 /etc/nginx /usr/share/nginx/html

EXPOSE ${VUE_PORT}
CMD ["nginx", "-g", "daemon off;"]