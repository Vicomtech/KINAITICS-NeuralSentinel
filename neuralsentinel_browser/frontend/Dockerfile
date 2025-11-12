FROM node:20 as build-stage
WORKDIR /app
RUN npm update
COPY package.json ./package.json

RUN npm install
COPY ./ ./
RUN npm run build

# production stage
FROM nginx:latest AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./resources/ /etc/nginx/certs
EXPOSE 80:80
EXPOSE 443:443
CMD ["nginx", "-g", "daemon off;"]