.PHONY: start stop restart clean logs up down

start:
	docker-compose up -d

stop:
	docker-compose down

restart: stop start

clean:
	docker-compose down -v --rmi local

logs:
	docker-compose logs -f

logs-service:
	@if [ -z "$(SERVICE)" ]; then \
		echo "Ошибка: укажите SERVICE, например: make logs-service SERVICE=auth_service"; \
		exit 1; \
	fi
	docker-compose logs -f "$(SERVICE)"

rebuild: stop
	docker-compose up -d --build
