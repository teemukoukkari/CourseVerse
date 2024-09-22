FROM postgres:14
COPY ./schema.sql /docker-entrypoint-initdb.d/schema.sql
RUN chown postgres:postgres /docker-entrypoint-initdb.d/schema.sql
CMD ["docker-entrypoint.sh", "postgres"]