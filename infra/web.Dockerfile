# MindKeep Web — build context = repo root (dev-mode skeleton)
FROM node:20-alpine

WORKDIR /srv

COPY frontend/package.json ./package.json
RUN npm install

COPY frontend/ ./

EXPOSE 3000
CMD ["npm", "run", "dev"]
