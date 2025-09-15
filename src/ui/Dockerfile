FROM elilillyco-lilly-docker.jfrog.io/node:lts-alpine

# ENV NODE_ENV development

WORKDIR /app
COPY package.json package-lock.json ./ 
RUN npm ci

# COPY package*.json ./

# RUN npm ci

COPY . .

RUN npm run build

EXPOSE 3000

# ENV PORT 3000

CMD npm run start