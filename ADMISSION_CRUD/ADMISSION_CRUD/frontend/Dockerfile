FROM nginx:alpine

# Copy HTML file to nginx web root
COPY index.html /usr/share/nginx/html/index.html

# Copy custom nginx config (with API proxy)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
