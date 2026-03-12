FROM node:20-alpine AS build

WORKDIR /app/site

COPY site/package.json site/package-lock.json ./
RUN npm ci

COPY site/ ./
RUN npm run build

FROM node:20-alpine AS runtime

WORKDIR /app/site

COPY site/package.json site/package-lock.json ./
RUN npm ci --omit=dev

COPY --from=build /app/site/dist ./dist

ENV NODE_ENV=production
ENV PORT=3000

CMD ["sh", "-c", "./node_modules/.bin/serve -s dist -l ${PORT}"]
