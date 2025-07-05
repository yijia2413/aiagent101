// models/User.js
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  username: { type: String, unique: true, trim: true },
  password: { type: String, select: false },
  wechatOpenId: { type: String, unique: true, sparse: true },
  avatar: { type: String, default: '' },
  bio: { type: String, default: '' },
  following: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
  followers: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
  likedVideos: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Video' }],
  createdAt: { type: Date, default: Date.now }
});

// 密码加密中间件
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  this.password = await bcrypt.hash(this.password, 12);
  next();
});

// 密码验证方法
userSchema.methods.correctPassword = async function(candidatePassword, userPassword) {
  return await bcrypt.compare(candidatePassword, userPassword);
};

module.exports = mongoose.model('User', userSchema);


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


