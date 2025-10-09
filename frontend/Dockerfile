FROM nginx:alpine

# Copy the new config file to replace the default Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY src/ /usr/share/nginx/html
