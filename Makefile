.PHONY: restore-snapshot
SNAPSHOT_NAME=nasa_web_pages-7327035907417914-2024-10-27-10-49-07.snapshot
QDRANT_URL=http://localhost:6333

build:
	docker-compose --env-file .env build

start:
	docker-compose --env-file .env up -d

down:
	docker-compose --env-file .env down

restart:
	docker-compose --env-file .env restart

restore-snapshot:
	@curl -X POST "${QDRANT_URL}/collections/nasa_web_pages/snapshots/upload?priority=snapshot" \
	-H "Content-Type: multipart/form-data" \
	-F "snapshot=@${SNAPSHOT_NAME}"

