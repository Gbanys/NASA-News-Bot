#!/bin/bash

if [ -z "$QDRANT_URL" ]; then
  echo "Error: QDRANT_URL environment variable is not set."
  exit 1
fi

if [ -z "$SNAPSHOT_NAME" ]; then
  echo "Error: SNAPSHOT_NAME environment variable is not set."
  exit 1
fi

curl -X POST "${QDRANT_HOST}/collections/nasa_web_pages/snapshots/upload?priority=snapshot" \
     -H "Content-Type: multipart/form-data" \
     -F "snapshot=@${SNAPSHOT_NAME}"
