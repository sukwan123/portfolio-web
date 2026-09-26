FROM caddy:2-alpine

COPY Caddyfile /etc/caddy/Caddyfile
COPY *.html /srv/
COPY robots.txt /srv/robots.txt
COPY assets /srv/assets
COPY img /srv/img
COPY vid /srv/vid
COPY doc /srv/doc

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
