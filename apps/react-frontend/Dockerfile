FROM node:12.22
WORKDIR /home/src/electricitymap/contrib/web

# Install dependencies
RUN apt-get update && apt-get install -y jq unzip
ADD react-frontend/package.json ./package.json
ADD react-frontend/yarn.lock ./yarn.lock
RUN yarn install --frozen-lockfile


ADD react-frontend/src/world.json ./src/world.json 
ARG ELECTRICITYMAP_PUBLIC_TOKEN

# Build
# (note: this will override the world.json that was previously created)
ADD react-frontend/config /home/src/electricitymap/contrib/config
ADD react-frontend ./
RUN yarn build-release

EXPOSE 8000
ENV PORT 8000
CMD node server.js

HEALTHCHECK CMD curl --fail http://localhost:${PORT}/ || exit 1
