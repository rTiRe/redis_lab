docker compose \
    --env-file ./consumer/config/.env \
    --env-file ./publisher/config/.env \
    logs -f $1
