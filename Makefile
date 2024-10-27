.PHONY: restore-snapshot
SNAPSHOT_NAME=nasa_web_pages-7327035907417914-2024-10-27-10-49-07.snapshot

build:
	docker-compose build

start:
	docker-compose up -d

down:
	docker-compose down

restore-snapshot:
	@curl -X POST "http://localhost:6333/collections/nasa_web_pages/snapshots/upload?priority=snapshot" \
	-H "Content-Type: multipart/form-data" \
	-F "snapshot=@${SNAPSHOT_NAME}"
