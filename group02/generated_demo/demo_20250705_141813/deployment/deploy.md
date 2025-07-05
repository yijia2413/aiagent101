# 使用轻量级Nginx镜像
FROM nginx:alpine

# 复制游戏文件到容器
COPY snake-game.html /usr/share/nginx/html/index.html

# 暴露80端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]


docker-compose up -d


   docker-compose up -d
   

COPY nginx.conf /etc/nginx/conf.d/default.conf


snake-game/
├── snake-game.html          # 主游戏文件
├── run-local.sh             # 本地运行脚本
├── deploy.sh                # 生产部署脚本
├── Dockerfile               # Docker构建文件
├── docker-compose.yml       # Docker Compose配置
├── README.md                # 使用说明
└── .github/workflows/       # GitHub Actions配置
    └── deploy.yml


Dockerfile

docker-compose.yml

.github/workflows/deploy.yml

nginx.conf

