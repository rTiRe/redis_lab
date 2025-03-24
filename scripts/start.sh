docker compose \
    --env-file ./consumer/config/.env \
    --env-file ./publisher/config/.env \
    up -d $1