makemigrate:
	docker compose exec web alembic revision --autogenerate -m "$(msg)"

downgrade:
	docker compose exec web alembic downgrade -1
	
migrate:
	docker compose exec web alembic upgrade head
