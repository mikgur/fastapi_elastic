FROM nginx
RUN rm /etc/nginx/conf.d/default.conf

COPY conf /etc/nginx
COPY ssl  /etc/ssl
COPY .htpasswd /etc/nginx
