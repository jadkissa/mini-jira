# ---- Stage 1: build the static app ----
# Debian, not Alpine: the TypeScript binary in the lockfile is built for glibc.
FROM node:24-bookworm-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite bakes this into the bundle. The browser calls it, so it must be an
# address the browser can reach, not the Compose service name.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build


# ---- Stage 2: serve it ----
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
