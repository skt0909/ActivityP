# Stage 1: Build the Vite/React app
FROM node:20-alpine AS builder

WORKDIR /app

# Vite reads VITE_* env vars at BUILD time, not runtime.
# Pass via Docker build-arg (Railway exposes service variables to build args).
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve static files with nginx
FROM nginx:alpine

# Remove default nginx site
RUN rm /etc/nginx/conf.d/default.conf

# Copy our nginx template (uses $PORT) and built assets
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=builder /app/dist /usr/share/nginx/html

# Railway assigns PORT dynamically; nginx:alpine's entrypoint runs envsubst
# on /etc/nginx/templates/*.template into /etc/nginx/conf.d/ at startup.
ENV PORT=8080
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
