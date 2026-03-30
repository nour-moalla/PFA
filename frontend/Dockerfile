# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

RUN apk add --no-cache curl

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser:appgroup /app
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
	CMD curl -f http://localhost:3000 || exit 1
USER appuser

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
