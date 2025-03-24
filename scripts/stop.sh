docker compose \
    --env-file ./consumer/config/.env \
    --env-file ./publisher/config/.env \
    stop $1