backend/
├── config/               # 配置文件
│   └── db.js            # 数据库配置
├── controllers/         # 控制器
│   ├── auth.controller.js
│   ├── comment.controller.js
│   ├── user.controller.js
│   └── video.controller.js
├── middlewares/         # 中间件
│   ├── auth.js          # 认证中间件
│   └── upload.js        # 上传中间件
├── models/              # 数据模型
│   ├── Comment.js
│   ├── User.js
│   └── Video.js
├── routes/              # 路由
│   ├── auth.routes.js
│   ├── comment.routes.js
│   ├── user.routes.js
│   └── video.routes.js
├── services/            # 服务层
│   ├── qiniu.service.js # 七牛云存储服务
│   └── wechat.service.js # 微信服务
├── utils/               # 工具函数
│   ├── apiError.js
│   ├── apiResponse.js
│   └── logger.js
├── app.js               # 主应用文件
├── server.js            # 服务入口
└── package.json


// controllers/video.controller.js
const Video = require('../models/Video');
const User = require('../models/User');
const ApiResponse = require('../utils/apiResponse');
const ApiError = require('../utils/apiError');

// 获取推荐视频流
exports.getFeedVideos = async (req, res, next) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    // 获取用户关注列表
    const user = await User.findById(req.user.id).select('following');
    
    // 构建查询条件
    let query = { isPrivate: false };
    
    // 如果用户有关注的人，优先显示关注用户的视频
    if (user.following.length > 0) {
      query.$or = [
        { author: { $in: user.following } },
        { likes: { $gte: 1000 } } // 热门视频
      ];
    } else {
      // 新用户显示热门视频
      query.likes = { $gte: 1000 };
    }

    const videos = await Video.find(query)
      .sort('-createdAt')
      .skip(skip)
      .limit(limit)
      .populate('author', 'username avatar')
      .lean();

    // 处理视频数据
    const processedVideos = videos.map(video => {
      const isLiked = req.user.likedVideos.includes(video._id);
      return {
        ...video,
        isLiked,
        author: {
          id: video.author._id,
          name: video.author.username,
          avatar: video.author.avatar
        }
      };
    });

    res.json(new ApiResponse(processedVideos));
  } catch (err) {
    next(new ApiError(500, '获取视频流失败'));
  }
};

// 上传视频
exports.uploadVideo = async (req, res, next) => {
  try {
    if (!req.files || !req.files.video) {
      throw new ApiError(400, '请上传视频文件');
    }

    const { video, cover } = req.files;
    const { title, description, music, isPrivate } = req.body;

    // 上传视频到云存储 (这里使用七牛云示例)
    const videoUrl = await qiniuService.upload(video[0].path, 'videos');
    const coverUrl = cover ? await qiniuService.upload(cover[0].path, 'covers') : '';

    // 获取视频时长 (需要ffmpeg)
    const duration = await getVideoDuration(video[0].path);

    const newVideo = await Video.create({
      author: req.user.id,
      title,
      description,
      videoUrl,
      coverUrl: coverUrl || generateDefaultCover(),
      duration,
      music,
      isPrivate: isPrivate === 'true'
    });

    res.status(201).json(new ApiResponse(newVideo, '视频上传成功'));
  } catch (err) {
    next(err);
  }
};

// 点赞视频
exports.likeVideo = async (req, res, next) => {
  try {
    const video = await Video.findById(req.params.videoId);
    if (!video) {
      throw new ApiError(404, '视频不存在');
    }

    const user = await User.findById(req.user.id);
    
    // 检查是否已经点赞
    const isLiked = user.likedVideos.includes(video._id);
    
    if (isLiked) {
      // 取消点赞
      await User.findByIdAndUpdate(req.user.id, {
        $pull: { likedVideos: video._id }
      });
      await Video.findByIdAndUpdate(video._id, {
        $inc: { likes: -1 }
      });
    } else {
      // 点赞
      await User.findByIdAndUpdate(req.user.id, {
        $addToSet: { likedVideos: video._id }
      });
      await Video.findByIdAndUpdate(video._id, {
        $inc: { likes: 1 }
      });
    }

    res.json(new ApiResponse(null, isLiked ? '已取消点赞' : '点赞成功'));
  } catch (err) {
    next(new ApiError(500, '操作失败'));
  }
};


// controllers/auth.controller.js
const User = require('../models/User');
const ApiResponse = require('../utils/apiResponse');
const ApiError = require('../utils/apiError');
const jwt = require('jsonwebtoken');
const wechatService = require('../services/wechat.service');

// 微信登录
exports.wechatLogin = async (req, res, next) => {
  try {
    const { code } = req.body;
    
    if (!code) {
      throw new ApiError(400, '缺少code参数');
    }

    // 获取微信openid
    const wechatData = await wechatService.getWechatUserInfo(code);
    
    // 查找或创建用户
    let user = await User.findOne({ wechatOpenId: wechatData.openid });
    
    if (!user) {
      // 新用户注册
      user = await User.create({
        wechatOpenId: wechatData.openid,
        username: `wx_${wechatData.openid.slice(0, 8)}`,
        avatar: wechatData.headimgurl || ''
      });
    }

    // 生成JWT token
    const token = jwt.sign(
      { id: user._id },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN }
    );

    res.json(new ApiResponse({
      token,
      user: {
        id: user._id,
        username: user.username,
        avatar: user.avatar
      }
    }, '登录成功'));
  } catch (err) {
    next(err);
  }
};

// 获取当前用户信息
exports.getMe = async (req, res, next) => {
  try {
    const user = await User.findById(req.user.id)
      .select('-password -wechatOpenId')
      .populate('following followers', 'username avatar');

    res.json(new ApiResponse(user));
  } catch (err) {
    next(new ApiError(500, '获取用户信息失败'));
  }
};


// controllers/comment.controller.js
const Comment = require('../models/Comment');
const Video = require('../models/Video');
const ApiResponse = require('../utils/apiResponse');
const ApiError = require('../utils/apiError');

// 获取视频评论
exports.getVideoComments = async (req, res, next) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const skip = (page - 1) * limit;

    const comments = await Comment.find({ video: req.params.videoId })
      .sort('-createdAt')
      .skip(skip)
      .limit(limit)
      .populate('user', 'username avatar')
      .populate('replies.user', 'username avatar');

    res.json(new ApiResponse(comments));
  } catch (err) {
    next(new ApiError(500, '获取评论失败'));
  }
};

// 添加评论
exports.addComment = async (req, res, next) => {
  try {
    const { content } = req.body;
    
    if (!content || content.trim().length === 0) {
      throw new ApiError(400, '评论内容不能为空');
    }

    const video = await Video.findById(req.params.videoId);
    if (!video) {
      throw new ApiError(404, '视频不存在');
    }

    const newComment = await Comment.create({
      video: req.params.videoId,
      user: req.user.id,
      content
    });

    // 更新视频评论数
    await Video.findByIdAndUpdate(req.params.videoId, {
      $inc: { comments: 1 }
    });

    // 返回带用户信息的评论
    const commentWithUser = await Comment.populate(newComment, {
      path: 'user',
      select: 'username avatar'
    });

    res.status(201).json(new ApiResponse(commentWithUser, '评论成功'));
  } catch (err) {
    next(err);
  }
};


// routes/video.routes.js
const express = require('express');
const router = express.Router();
const videoController = require('../controllers/video.controller');
const authMiddleware = require('../middlewares/auth');
const uploadMiddleware = require('../middlewares/upload');

// 获取视频流
router.get('/feed', authMiddleware, videoController.getFeedVideos);

// 上传视频
router.post(
  '/upload',
  authMiddleware,
  uploadMiddleware.fields([
    { name: 'video', maxCount: 1 },
    { name: 'cover', maxCount: 1 }
  ]),
  videoController.uploadVideo
);

// 点赞视频
router.post('/:videoId/like', authMiddleware, videoController.likeVideo);

// 获取视频详情
router.get('/:videoId', authMiddleware, videoController.getVideoDetail);

module.exports = router;


// routes/auth.routes.js
const express = require('express');
const router = express.Router();
const authController = require('../controllers/auth.controller');

// 微信登录
router.post('/wechat-login', authController.wechatLogin);

// 获取当前用户信息
router.get('/me', authMiddleware, authController.getMe);

module.exports = router;


// middlewares/auth.js
const jwt = require('jsonwebtoken');
const ApiError = require('../utils/apiError');
const User = require('../models/User');

exports.auth = async (req, res, next) => {
  try {
    // 1) 获取token
    let token;
    if (
      req.headers.authorization &&
      req.headers.authorization.startsWith('Bearer')
    ) {
      token = req.headers.authorization.split(' ')[1];
    } else if (req.cookies?.token) {
      token = req.cookies.token;
    }

    if (!token) {
      throw new ApiError(401, '请先登录');
    }

    // 2) 验证token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // 3) 检查用户是否存在
    const currentUser = await User.findById(decoded.id);
    if (!currentUser) {
      throw new ApiError(401, '用户不存在');
    }

    // 4) 将用户信息添加到请求对象
    req.user = currentUser;
    next();
  } catch (err) {
    next(err);
  }
};


// middlewares/upload.js
const multer = require('multer');
const ApiError = require('../utils/apiError');

// 内存存储
const storage = multer.memoryStorage();

// 文件过滤
const fileFilter = (req, file, cb) => {
  if (file.mimetype.startsWith('image') || file.mimetype.startsWith('video')) {
    cb(null, true);
  } else {
    cb(new ApiError(400, '请上传图片或视频文件'), false);
  }
};

// 上传配置
const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 50 * 1024 * 1024 // 50MB
  }
});

module.exports = upload;


// app.js
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const morgan = require('morgan');
const cookieParser = require('cookie-parser');
const ApiError = require('./utils/apiError');
const globalErrorHandler = require('./controllers/error.controller');

// 路由
const authRoutes = require('./routes/auth.routes');
const videoRoutes = require('./routes/video.routes');
const userRoutes = require('./routes/user.routes');
const commentRoutes = require('./routes/comment.routes');

const app = express();

// 1) 全局中间件
app.use(cors({
  origin: process.env.CORS_ORIGIN,
  credentials: true
}));

// 开发环境日志
if (process.env.NODE_ENV === 'development') {
  app.use(morgan('dev'));
}

// 解析请求体
app.use(express.json({ limit: '10kb' }));
app.use(express.urlencoded({ extended: true, limit: '10kb' }));
app.use(cookieParser());

// 2) 路由
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/videos', videoRoutes);
app.use('/api/v1/users', userRoutes);
app.use('/api/v1/comments', commentRoutes);

// 3) 未匹配路由处理
app.all('*', (req, res, next) => {
  next(new ApiError(404, `找不到 ${req.originalUrl} 路由`));
});

// 4) 全局错误处理
app.use(globalErrorHandler);

module.exports = app;



## 9. API文档

### 9.1 视频相关API

| 端点 | 方法 | 描述 | 需要认证 |
|------|------|------|----------|
| `/api/v1/videos/feed` | GET | 获取推荐视频流 | 是 |
| `/api/v1/videos/upload` | POST | 上传视频 | 是 |
| `/api/v1/videos/:videoId/like` | POST | 点赞/取消点赞视频 | 是 |
| `/api/v1/videos/:videoId` | GET | 获取视频详情 | 是 |

### 9.2 用户认证API

| 端点 | 方法 | 描述 | 需要认证 |
|------|------|------|----------|
| `/api/v1/auth/wechat-login` | POST | 微信登录 | 否 |
| `/api/v1/auth/me` | GET | 获取当前用户信息 | 是 |

### 9.3 评论API

| 端点 | 方法 | 描述 | 需要认证 |
|------|------|------|----------|
| `/api/v1/comments/:videoId` | GET | 获取视频评论 | 是 |
| `/api/v1/comments/:videoId` | POST | 添加评论 | 是 |

## 10. 测试方案

### 10.1 单元测试

使用Jest + Supertest编写测试：




### 10.2 集成测试

使用Postman或Newman进行API测试，测试集合应包括：

1. 用户注册/登录流程
2. 视频上传和浏览流程
3. 点赞和评论交互
4. 错误处理测试

### 10.3 性能测试

使用Artillery进行负载测试：




## 11. 完整部署指南

### 11.1 服务器要求

- Node.js 14+
- MongoDB 4.4+
- Redis (可选，用于缓存)
- Nginx (用于生产环境反向代理)

### 11.2 生产环境部署步骤

1. **安装依赖**



## 12. 前端集成指南

前端项目可以通过以下方式与后端集成：

1. **配置API基础URL**




2. **调用视频流API示例**




## 13. 安全最佳实践

1. **API安全**
   - 始终使用HTTPS
   - 实施速率限制
   - 使用Helmet中间件
   - 验证所有输入数据

2. **数据安全**
   - 加密敏感数据
   - 使用数据库角色和权限
   - 定期备份

3. **认证安全**
   - 使用HttpOnly和Secure Cookie
   - 实施JWT过期时间
   - 使用强密码哈希

4. **CORS配置**




## 14. 扩展功能建议

1. **实时功能**
   - 使用Socket.IO实现实时评论和通知
   - 视频上传进度实时显示

2. **推荐算法**
   - 基于用户行为的协同过滤
   - 热门视频加权推荐

3. **视频处理**
   - 视频转码和水印
   - 内容审核API集成

4. **数据分析**
   - 用户观看行为分析
   - 视频表现指标

5. **管理后台**
   - 视频内容管理
   - 用户管理
   - 数据分析仪表盘

## 15. 故障排除

### 15.1 常见问题

1. **数据库连接失败**
   - 检查MongoDB服务状态
   - 验证连接字符串
   - 检查防火墙设置

2. **上传文件大小限制**
   - 调整Nginx `client_max_body_size`
   - 检查multer配置

3. **跨域问题**
   - 确保CORS配置正确
   - 检查前端请求头

4. **性能瓶颈**
   - 添加数据库索引
   - 实现缓存层
   - 优化查询

### 15.2 调试技巧

1. **启用详细日志**



/api/v1/videos/feed

/api/v1/videos/upload

/api/v1/videos/:videoId/like

/api/v1/videos/:videoId

/api/v1/auth/wechat-login

/api/v1/auth/me

/api/v1/comments/:videoId

/api/v1/comments/:videoId

/api/v1/videos/${testVideo._id}/like

douyin-h5/
├── frontend/               # 前端代码
│   └── index.html          # 前端主页面
├── backend/                # 后端代码
│   ├── app.js              # Express主应用
│   ├── server.js           # 服务入口
│   └── ...                 # 其他后端文件
├── docker-compose.yml      # Docker集成配置
└── README.md               # 项目文档


version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - MONGO_URI=mongodb://mongo:27017/douyin_h5
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

  mongo:
    image: mongo:4.4
    volumes:
      - mongo-data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongo-data:


# Node.js
curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt-get install -y nodejs

# MongoDB
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod


server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}


{
  "info": {
    "_postman_id": "a1b2c3d4-e5f6-7890",
    "name": "Douyin H5 API测试",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "用户登录",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"code\": \"wechat_auth_code\"\n}"
        },
        "url": {
          "raw": "http://localhost:3000/api/v1/auth/wechat-login",
          "protocol": "http",
          "host": ["localhost"],
          "port": "3000",
          "path": ["api","v1","auth","wechat-login"]
        }
      }
    },
    {
      "name": "获取视频流",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{auth_token}}"
          }
        ],
        "url": {
          "raw": "http://localhost:3000/api/v1/videos/feed",
          "protocol": "http",
          "host": ["localhost"],
          "port": "3000",
          "path": ["api","v1","videos","feed"]
        }
      }
    }
  ]
}


graph TD
    A[Node.js] --> B[Express]
    B --> C[API路由]
    C --> D[控制器]
    D --> E[MongoDB]
    E --> F[视频数据]
    E --> G[用户数据]


const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const videoRoutes = require('./routes/videoRoutes');
const authRoutes = require('./routes/authRoutes');

// 初始化Express应用
const app = express();

// 中间件
app.use(cors());
app.use(express.json());

// 数据库连接
mongoose.connect('mongodb://localhost/douyin_h5', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

// 路由
app.use('/api/v1/videos', videoRoutes);
app.use('/api/v1/auth', authRoutes);

// 错误处理中间件
app.use((err, req, res, next) => {
    res.status(500).json({ error: err.message });
});

module.exports = app;


version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - MONGO_URI=mongodb://mongo:27017/douyin_h5
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

  mongo:
    image: mongo:4.4
    volumes:
      - mongo-data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongo-data:


// backend/test/video.test.js
const request = require('supertest');
const app = require('../app');
const Video = require('../models/Video');

describe('视频API测试', () => {
    it('应该返回视频列表', async () => {
        const res = await request(app)
            .get('/api/v1/videos')
            .expect(200);
        
        expect(res.body).toBeInstanceOf(Array);
    });
});


server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://frontend:80;
    }

    location /api {
        proxy_pass http://backend:3000;
    }
}


/api/v1/videos

/api/v1/videos/:id/like

/api/v1/videos/upload

/api/v1/auth/wechat-login

/api/v1/auth/me

graph TD
    A[Node.js] --> B[Express]
    B --> C[API路由]
    C --> D[控制器]
    D --> E[MongoDB]
    E --> F[视频数据]
    E --> G[用户数据]


const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const videoRoutes = require('./routes/videoRoutes');
const authRoutes = require('./routes/authRoutes');

// 初始化Express应用
const app = express();

// 中间件
app.use(cors());
app.use(express.json());

// 数据库连接
mongoose.connect('mongodb://localhost/douyin_h5', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

// 路由
app.use('/api/v1/videos', videoRoutes);
app.use('/api/v1/auth', authRoutes);

// 错误处理中间件
app.use((err, req, res, next) => {
    res.status(500).json({ error: err.message });
});

module.exports = app;


version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - MONGO_URI=mongodb://mongo:27017/douyin_h5
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

  mongo:
    image: mongo:4.4
    volumes:
      - mongo-data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongo-data:


// backend/test/video.test.js
const request = require('supertest');
const app = require('../app');
const Video = require('../models/Video');

describe('视频API测试', () => {
    it('应该返回视频列表', async () => {
        const res = await request(app)
            .get('/api/v1/videos')
            .expect(200);
        
        expect(res.body).toBeInstanceOf(Array);
    });
});


server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://frontend:80;
    }

    location /api {
        proxy_pass http://backend:3000;
    }
}


/api/v1/videos

/api/v1/videos/:id/like

/api/v1/videos/upload

/api/v1/auth/wechat-login

/api/v1/auth/me

graph TD
    A[Node.js] --> B[Express]
    B --> C[API路由]
    C --> D[控制器]
    D --> E[MongoDB]
    E --> F[视频数据]
    E --> G[用户数据]


const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const videoRoutes = require('./routes/videoRoutes');
const authRoutes = require('./routes/authRoutes');

const app = express();

// 中间件
app.use(cors());
app.use(express.json());

// 数据库连接
mongoose.connect('mongodb://localhost/douyin_h5', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

// 路由
app.use('/api/v1/videos', videoRoutes);
app.use('/api/v1/auth', authRoutes);

// 错误处理中间件
app.use((err, req, res, next) => {
    res.status(500).json({ error: err.message });
});

module.exports = app;


version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - MONGO_URI=mongodb://mongo:27017/douyin_h5
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

  mongo:
    image: mongo:4.4
    volumes:
      - mongo-data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongo-data:


describe('视频功能测试', () => {
  it('应该自动播放第一个视频', () => {
    cy.get('video').first().should('have.prop', 'paused', false);
  });
});


test('获取视频流', async () => {
  const res = await request(app)
    .get('/api/v1/videos/feed')
    .set('Authorization', `Bearer ${authToken}`);
  
  expect(res.statusCode).toBe(200);
});


graph TD
    A[Node.js] --> B[Express]
    B --> C[API路由]
    C --> D[控制器]
    D --> E[MongoDB]
    E --> F[视频数据]
    E --> G[用户数据]


const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const videoRoutes = require('./routes/videoRoutes');
const authRoutes = require('./routes/authRoutes');

const app = express();

// 中间件
app.use(cors());
app.use(express.json());

// 数据库连接
mongoose.connect('mongodb://localhost/douyin_h5', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

// 路由
app.use('/api/v1/videos', videoRoutes);
app.use('/api/v1/auth', authRoutes);

// 错误处理中间件
app.use((err, req, res, next) => {
    res.status(500).json({ error: err.message });
});

module.exports = app;


version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - MONGO_URI=mongodb://mongo:27017/douyin_h5
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

  mongo:
    image: mongo:4.4
    volumes:
      - mongo-data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongo-data:


describe('视频功能测试', () => {
  it('应该自动播放第一个视频', () => {
    cy.get('video').first().should('have.prop', 'paused', false);
  });
});


test('获取视频流', async () => {
  const res = await request(app)
    .get('/api/v1/videos/feed')
    .set('Authorization', `Bearer ${authToken}`);
  
  expect(res.statusCode).toBe(200);
});


graph TD
    A[Node.js] --> B[Express]
    B --> C[API路由]
    C --> D[控制器]
    D --> E[MongoDB]
    E --> F[视频数据]
    E --> G[用户数据]


const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const videoRoutes = require('./routes/videoRoutes');
const authRoutes = require('./routes/authRoutes');

const app = express();

// 中间件
app.use(cors());
app.use(express.json());

// 数据库连接
mongoose.connect('mongodb://localhost/douyin_h5', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

// 路由
app.use('/api/v1/videos', videoRoutes);
app.use('/api/v1/auth', authRoutes);

// 错误处理中间件
app.use((err, req, res, next) => {
    res.status(500).json({ error: err.message });
});

module.exports = app;


version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - MONGO_URI=mongodb://mongo:27017/douyin_h5
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

  mongo:
    image: mongo:4.4
    volumes:
      - mongo-data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongo-data:


describe('视频功能测试', () => {
  it('应该自动播放第一个视频', () => {
    cy.get('video').first().should('have.prop', 'paused', false);
  });
});


test('获取视频流', async () => {
  const res = await request(app)
    .get('/api/v1/videos/feed')
    .set('Authorization', `Bearer ${authToken}`);
  
  expect(res.statusCode).toBe(200);
});


graph TD
    A[Node.js] --> B[Express]
    B --> C[API路由]
    C --> D[控制器]
    D --> E[MongoDB]
    E --> F[视频数据]
    E --> G[用户数据]


const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const videoRoutes = require('./routes/videoRoutes');
const authRoutes = require('./routes/authRoutes');

const app = express();

// 中间件
app.use(cors());
app.use(express.json());

// 数据库连接
mongoose.connect('mongodb://localhost/douyin_h5', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

// 路由
app.use('/api/v1/videos', videoRoutes);
app.use('/api/v1/auth', authRoutes);

// 错误处理中间件
app.use((err, req, res, next) => {
    res.status(500).json({ error: err.message });
});

module.exports = app;


version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - MONGO_URI=mongodb://mongo:27017/douyin_h5
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

  mongo:
    image: mongo:4.4
    volumes:
      - mongo-data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongo-data:


describe('视频功能测试', () => {
  it('应该自动播放第一个视频', () => {
    cy.get('video').first().should('have.prop', 'paused', false);
  });
});


test('获取视频流', async () => {
  const res = await request(app)
    .get('/api/v1/videos/feed')
    .set('Authorization', `Bearer ${authToken}`);
  
  expect(res.statusCode).toBe(200);
});


graph TD
    A[Node.js] --> B[Express]
    B --> C[API路由]
    C --> D[控制器]
    D --> E[MongoDB]
    E --> F[视频数据]
    E --> G[用户数据]


const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const videoRoutes = require('./routes/videoRoutes');
const authRoutes = require('./routes/authRoutes');

const app = express();

// 中间件
app.use(cors());
app.use(express.json());

// 数据库连接
mongoose.connect('mongodb://localhost/douyin_h5', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

// 路由
app.use('/api/v1/videos', videoRoutes);
app.use('/api/v1/auth', authRoutes);

// 错误处理中间件
app.use((err, req, res, next) => {
    res.status(500).json({ error: err.message });
});

module.exports = app;


version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - MONGO_URI=mongodb://mongo:27017/douyin_h5
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

  mongo:
    image: mongo:4.4
    volumes:
      - mongo-data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongo-data:


describe('视频功能测试', () => {
  it('应该自动播放第一个视频', () => {
    cy.get('video').first().should('have.prop', 'paused', false);
  });
});


test('获取视频流', async () => {
  const res = await request(app)
    .get('/api/v1/videos/feed')
    .set('Authorization', `Bearer ${authToken}`);
  
  expect(res.statusCode).toBe(200);
});


