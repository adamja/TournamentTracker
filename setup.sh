mkdir -p docker/tournamenttracker/app/data/db
mkdir -p docker/tournamenttracker/app/data/logs
mkdir -p docker/tournamenttracker/letsencrypt/nginx/htpasswd/
mkdir -p docker/tournamenttracker/letsencrypt/nginx/conf.d/
mkdir -p docker/tournamenttracker/letsencrypt/nginx/vhost.d/
mkdir -p docker/tournamenttracker/letsencrypt/nginx/html/
mkdir -p docker/tournamenttracker/letsencrypt/nginx/certs/

docker network create tournamenttracker

docker-compose -f docker-compose.yaml build
docker-compose -f docker-compose.yaml up -d
docker-compose -f docker-compose.yaml logs -f