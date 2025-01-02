.PHONY: restore-snapshot
SNAPSHOT_NAME=backend/nasa_web_pages.snapshot
QDRANT_URL=http://localhost:6333

build:
	docker compose build

start:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

restore-snapshot:
	@curl -X POST "${QDRANT_URL}/collections/nasa_web_pages/snapshots/upload?priority=snapshot" \
	-H "Content-Type: multipart/form-data" \
	-F "snapshot=@${SNAPSHOT_NAME}"