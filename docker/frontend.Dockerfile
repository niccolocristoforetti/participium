FROM node:lts
WORKDIR /usr/src/app

COPY src/frontend/package*.json ./
RUN npm ci

COPY src/frontend/ ./

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]