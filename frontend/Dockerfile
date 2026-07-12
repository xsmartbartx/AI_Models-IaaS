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

# Only copy public directory if it exists
RUN mkdir -p ./public
COPY --from=builder /app/public ./public || true

EXPOSE 3000
CMD ["npm", "start"]