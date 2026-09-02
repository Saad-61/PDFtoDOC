# Stage 1: Build static assets with Node.js
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package manifests and install dependencies
COPY package.json package-lock.json* ./
RUN npm ci || npm install

# Copy source code and build production bundle
COPY . .
RUN npm run build

# Stage 2: Lightweight Nginx Alpine Runtime
FROM nginx:alpine

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy production assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
