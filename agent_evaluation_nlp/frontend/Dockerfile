# Stage 1: Build the React app
FROM node:18 as build

WORKDIR /app

COPY . .

RUN npm install && npm run build

# Stage 2: Serve using Nginx
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]