FROM nginx:latest

COPY ./docker/frontend/nginx.conf /etc/nginx/nginx.conf