FROM node:20-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

# Create public directory and copy if it exists in builder
RUN mkdir -p ./public
COPY --chown=node:node --from=builder /app/public ./public || trueFROM node:20-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

# Create public directory
RUN mkdir -p ./public

# Only copy public if it exists in the builder
RUN if [ -d /app/public ]; then cp -r /app/public/* ./public/ || true; fi