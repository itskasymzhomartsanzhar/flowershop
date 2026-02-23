FROM node:18-alpine as build

# #AB0=>2:0 @01>G59 48@5:B>@88
WORKDIR /app

# >?8@>20=85 package.json 8 package-lock.json
COPY package*.json ./

# #AB0=>2:0 7028A8<>AB59
RUN npm ci

# >?8@>20=85 2A53> ?@>5:B0
COPY . .

# !1>@:0 ?@>5:B0
RUN npm run build

# $8=0;L=0O AB048O - B>;L:> A>1@0==K5 D09;K
FROM nginx:1.25-alpine

# >?8@>20=85 A>1@0==KE D09;>2 87 ?@54K4CI59 AB0488
COPY --from=build /app/dist /usr/share/nginx/html

# >?8@>20=85 :>=D83C@0F88 nginx (5A;8 =C6=0 :0AB><=0O)
# COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
