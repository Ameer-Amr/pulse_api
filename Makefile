migrate:
	docker compose exec web alembic revision --autogenerate -m "$(msg)"
	docker compose exec web alembic upgrade head
