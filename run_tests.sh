docker-compose up -d --build
docker-compose exec api python -m pytest "src/tests" -p no:warnings --cov="src" --cov-report term-missing
docker-compose exec api black src
docker-compose exec api isort src
docker-compose exec api flake8 src
docker-compose down