FROM node
MAINTAINER Dockerfiles
WORKDIR /front/
COPY . .
RUN npm install
RUN npm run build

FROM nginx
MAINTAINER Dockerfiles
WORKDIR /etc/static
COPY --from=0 /front/dist/index.html /etc/nginx/html/index.html
COPY --from=0 /front/dist /etc/nginx/dist/static
COPY  ./nginx/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80