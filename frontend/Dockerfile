FROM nginx:alpine

COPY static /usr/share/nginx/html/static
COPY templates/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
