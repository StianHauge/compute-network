# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package.json and install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build using the production environment variables
COPY frontend/ ./
RUN npm run build -- --mode production 

# Production serve stage using Nginx
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# We expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
