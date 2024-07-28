# frontend/Dockerfile
FROM node:20

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

RUN npm run build

CMD ["npm", "run", "preview", "--" ,"--port", "3000","--host","0.0.0.0"]
