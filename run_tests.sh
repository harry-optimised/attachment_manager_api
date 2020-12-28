docker-compose -f docker-compose.testing.yml up -d --build
docker-compose -f docker-compose.testing.yml exec api python -m pytest "src/tests" -p no:warnings --cov="src" --cov-report term-missing
docker-compose -f docker-compose.testing.yml exec api black src
docker-compose -f docker-compose.testing.yml exec api isort src
docker-compose -f docker-compose.testing.yml exec api flake8 src
docker-compose -f docker-compose.testing.yml down