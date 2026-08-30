FROM node:22-alpine
WORKDIR /app
COPY server.mjs /app/server.mjs
RUN addgroup -S app && adduser -S -G app app && mkdir -p /data && chown -R app:app /data /app
USER app
ENV NODE_ENV=production PORT=8787 HOST=0.0.0.0
EXPOSE 8787
CMD ["node","/app/server.mjs"]
