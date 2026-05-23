FROM postgres:18.4-alpine

RUN apk add --no-cache postgresql-pgvector \
    && cp /usr/share/postgresql18/extension/vector* /usr/local/share/postgresql/extension/ \
    && cp /usr/lib/postgresql18/vector.so /usr/local/lib/postgresql/
