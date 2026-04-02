FROM node:20-alpine

WORKDIR /app

# Copy package files first
COPY package*.json ./

# Install dependencies INSIDE the container (Linux binaries)
# Delete any existing node_modules from Windows first
RUN rm -rf node_modules && npm install

# Copy the rest of the source code
COPY . .

# Remove node_modules again in case COPY brought Windows ones
RUN rm -rf node_modules && npm install

# Add non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser:appgroup /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:3000 || exit 1

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]