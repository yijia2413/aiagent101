graph TD
    A[用户] --> B[Nginx]
    B --> C[前端静态文件]
    B --> D[后端API]
    D --> E[MongoDB]
    D --> F[Redis缓存]


FROM node:14 as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


# 构建并启动所有服务
docker-compose up -d --build

# 查看运行状态
docker-compose ps

# 停止服务
docker-compose down


# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Node.js
curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt install -y nodejs

# 安装MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# 安装Nginx
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx


# 构建前端
cd frontend
npm install
npm run build

# 配置Nginx
sudo cp -r dist/* /var/www/html/
sudo cp nginx.conf /etc/nginx/sites-available/douyin
sudo ln -s /etc/nginx/sites-available/douyin /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx


name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Install SSH Key
      uses: shimataro/ssh-key-action@v2
      with:
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        known_hosts: ${{ secrets.KNOWN_HOSTS }}
    
    - name: Deploy to Server
      run: |
        ssh -o StrictHostKeyChecking=no root@${{ secrets.SERVER_IP }} << 'ENDSSH'
        cd /var/www/douyin-h5
        git pull origin main
        cd backend
        npm install --production
        pm2 restart douyin-backend
        cd ../frontend
        npm install
        npm run build
        sudo cp -r dist/* /var/www/html/
        sudo systemctl restart nginx
        exit
        ENDSSH


# 查看Nginx访问日志
sudo tail -f /var/log/nginx/access.log

# 查看后端日志
pm2 logs douyin-backend

# 查看MongoDB日志
sudo tail -f /var/log/mongodb/mongod.log


# 使用Certbot获取免费SSL证书
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com


# 检查端口占用
sudo netstat -tulnp

# 检查服务状态
systemctl status nginx
systemctl status mongod
pm2 list

# 测试API端点
curl -v http://localhost:3000/api/v1/videos/feed


# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/douyin-backend:latest
        ports:
        - containerPort: 3000
        envFrom:
        - configMapRef:
            name: backend-config

# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  selector:
    app: backend
  ports:
    - protocol: TCP
      port: 3000
      targetPort: 3000


# serverless.yml
service: douyin-backend

provider:
  name: aws
  runtime: nodejs14.x
  region: ap-east-1

functions:
  api:
    handler: server.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY


graph TD
    A[准备服务器] --> B[安装依赖]
    B --> C[部署前端]
    B --> D[部署后端]
    C --> E[配置Nginx]
    D --> F[启动服务]
    E --> G[验证部署]
    F --> G
    G --> H[监控维护]


.github/workflows/deploy.yml

   /deploy
     ├── docker-compose.yml
     ├── nginx/
     │   └── nginx.conf
     ├── backend/
     │   └── Dockerfile
     └── frontend/
         └── Dockerfile
   

version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    restart: always
    depends_on:
      - backend
    networks:
      - app-network

  backend:
    build: ./backend
    environment:
      - NODE_ENV=production
      - MONGO_URI=mongodb://mongo:27017/douyin_h5
      - REDIS_URL=redis://redis:6379
    restart: always
    depends_on:
      - mongo
      - redis
    networks:
      - app-network

  mongo:
    image: mongo:4.4
    volumes:
      - mongo-data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password
    networks:
      - app-network

  redis:
    image: redis:6-alpine
    volumes:
      - redis-data:/data
    networks:
      - app-network

  nginx:
    image: nginx:1.21-alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - frontend
      - backend
    networks:
      - app-network

volumes:
  mongo-data:
  redis-data:

networks:
  app-network:
    driver: bridge


FROM node:14 as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.21-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


server {
    listen 80;
    server_name localhost;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://backend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 365d;
        add_header Cache-Control "public, no-transform";
    }
}


# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down


# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Node.js
curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt install -y nodejs

# 安装MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt update
sudo apt install -y mongodb-org

# 启动MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# 安装Redis
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 安装Nginx
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 安装PM2进程管理器
sudo npm install -g pm2


# 克隆项目
git clone https://github.com/your-repo/douyin-h5.git
cd douyin-h5/frontend

# 安装依赖并构建
npm install
npm run build

# 复制到Nginx目录
sudo cp -r dist/* /var/www/html/

# 配置Nginx
sudo cp deploy/nginx/nginx.conf /etc/nginx/sites-available/douyin
sudo ln -s /etc/nginx/sites-available/douyin /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx


# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com

# 测试自动续订
sudo certbot renew --dry-run


# 查看Nginx访问日志
tail -f /var/log/nginx/access.log

# 查看Nginx错误日志
tail -f /var/log/nginx/error.log

# 查看MongoDB日志
tail -f /var/log/mongodb/mongod.log

# 日志轮转配置
sudo nano /etc/logrotate.d/nginx
sudo nano /etc/logrotate.d/mongodb


# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/douyin-backend:latest
        ports:
        - containerPort: 3000
        envFrom:
        - configMapRef:
            name: backend-config
        resources:
          requests:
            cpu: "100m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "1Gi"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5


# 检查服务状态
systemctl status nginx
systemctl status mongod
pm2 list

# 检查端口监听
sudo netstat -tulnp

# 检查网络连接
ping yourdomain.com
curl -v http://localhost/api/v1/health

# 检查磁盘空间
df -h
du -sh /var/lib/mongodb/


