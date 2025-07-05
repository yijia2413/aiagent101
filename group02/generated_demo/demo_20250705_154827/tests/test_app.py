// 使用Lighthouse进行性能测试
const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

async function runAudit(url) {
  const chrome = await chromeLauncher.launch({chromeFlags: ['--headless']});
  const options = {output: 'html', port: chrome.port};
  const runnerResult = await lighthouse(url, options);
  
  // 性能评分
  console.log('Performance score:', runnerResult.lhr.categories.performance.score * 100);
  
  await chrome.kill();
  return runnerResult;
}

// 测试本地开发环境
runAudit('http://localhost:8080');


// cypress/integration/video.spec.js
describe('视频功能测试', () => {
  beforeEach(() => {
    cy.visit('http://localhost:8080');
  });

  it('应该自动播放第一个视频', () => {
    cy.get('video').first().should('have.prop', 'paused', false);
  });

  it('应该能够点赞视频', () => {
    cy.get('.action-btn[data-action="like"]').first().click();
    cy.get('.like-icon').first().should('have.class', 'liked');
  });

  it('应该能够滑动切换视频', () => {
    cy.get('.video-container')
      .trigger('touchstart', { y: 100 })
      .trigger('touchmove', { y: 300 })
      .trigger('touchend');
    
    cy.get('video').eq(1).should('be.visible');
  });
});


// backend/__tests__/video.test.js
const request = require('supertest');
const app = require('../app');
const Video = require('../models/Video');

describe('视频API测试', () => {
  let testVideo;
  let authToken;

  beforeAll(async () => {
    // 创建测试视频
    testVideo = await Video.create({
      title: '测试视频',
      videoUrl: 'test.mp4',
      coverUrl: 'test.jpg',
      author: 'testuser'
    });

    // 获取测试token
    const res = await request(app)
      .post('/api/v1/auth/login')
      .send({username: 'test', password: 'test123'});
    authToken = res.body.token;
  });

  test('获取视频流', async () => {
    const res = await request(app)
      .get('/api/v1/videos/feed')
      .set('Authorization', `Bearer ${authToken}`);
    
    expect(res.statusCode).toBe(200);
    expect(res.body.length).toBeGreaterThan(0);
  });

  test('点赞视频', async () => {
    const res = await request(app)
      .post(`/api/v1/videos/${testVideo._id}/like`)
      .set('Authorization', `Bearer ${authToken}`);
    
    expect(res.statusCode).toBe(200);
    expect(res.body.message).toMatch(/成功/);
  });
});


// 使用supertest进行安全测试
describe('安全测试', () => {
  test('应该过滤XSS攻击', async () => {
    const res = await request(app)
      .post('/api/v1/comments')
      .send({
        content: '<script>alert("xss")</script>',
        videoId: '123'
      })
      .set('Authorization', `Bearer ${authToken}`);
    
    expect(res.body.content).not.toMatch(/<script>/);
  });

  test('应该防止未授权访问', async () => {
    const res = await request(app)
      .get('/api/v1/auth/me');
    
    expect(res.statusCode).toBe(401);
  });
});


// 使用Newman进行API监控
const newman = require('newman');

newman.run({
  collection: require('./api-tests.postman_collection.json'),
  reporters: 'cli',
  iterationCount: 10
}, (err) => {
  if (err) { throw err; }
  console.log('API监控完成');
});


// backend/scripts/generateTestData.js
const mongoose = require('mongoose');
const User = require('../models/User');
const Video = require('../models/Video');
const faker = require('faker');

async function generateData() {
  // 连接数据库
  await mongoose.connect('mongodb://localhost/douyin_h5_test');
  
  // 清空测试数据
  await User.deleteMany();
  await Video.deleteMany();
  
  // 生成测试用户
  const users = [];
  for (let i = 0; i < 10; i++) {
    users.push(await User.create({
      username: faker.internet.userName(),
      avatar: faker.image.avatar()
    }));
  }
  
  // 生成测试视频
  for (let i = 0; i < 50; i++) {
    await Video.create({
      title: faker.lorem.sentence(),
      description: faker.lorem.paragraph(),
      videoUrl: 'https://example.com/video.mp4',
      coverUrl: faker.image.imageUrl(),
      author: users[Math.floor(Math.random() * users.length)]._id,
      likes: Math.floor(Math.random() * 1000)
    });
  }
  
  console.log('测试数据生成完成');
  process.exit(0);
}

generateData();


// 使用Sentry进行错误监控
const Sentry = require('@sentry/node');

Sentry.init({
  dsn: 'your_dsn_here',
  tracesSampleRate: 1.0
});

// 包装Express应用
const express = require('express');
const app = express();

app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.errorHandler());


// 使用Lighthouse进行性能测试
const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

async function runAudit(url) {
  const chrome = await chromeLauncher.launch({chromeFlags: ['--headless']});
  const options = {output: 'html', port: chrome.port};
  const runnerResult = await lighthouse(url, options);
  
  // 性能评分
  console.log('Performance score:', runnerResult.lhr.categories.performance.score * 100);
  
  await chrome.kill();
  return runnerResult;
}

// 测试本地开发环境
runAudit('http://localhost:8080');


// cypress/integration/video.spec.js
describe('视频功能测试', () => {
  beforeEach(() => {
    cy.visit('http://localhost:8080');
  });

  it('应该自动播放第一个视频', () => {
    cy.get('video').first().should('have.prop', 'paused', false);
  });

  it('应该能够点赞视频', () => {
    cy.get('.action-btn[data-action="like"]').first().click();
    cy.get('.like-icon').first().should('have.class', 'liked');
  });

  it('应该能够滑动切换视频', () => {
    cy.get('.video-container')
      .trigger('touchstart', { y: 100 })
      .trigger('touchmove', { y: 300 })
      .trigger('touchend');
    
    cy.get('video').eq(1).should('be.visible');
  });
});


// backend/__tests__/video.test.js
const request = require('supertest');
const app = require('../app');
const Video = require('../models/Video');

describe('视频API测试', () => {
  let testVideo;
  let authToken;

  beforeAll(async () => {
    // 创建测试视频
    testVideo = await Video.create({
      title: '测试视频',
      videoUrl: 'test.mp4',
      coverUrl: 'test.jpg',
      author: 'testuser'
    });

    // 获取测试token
    const res = await request(app)
      .post('/api/v1/auth/login')
      .send({username: 'test', password: 'test123'});
    authToken = res.body.token;
  });

  test('获取视频流', async () => {
    const res = await request(app)
      .get('/api/v1/videos/feed')
      .set('Authorization', `Bearer ${authToken}`);
    
    expect(res.statusCode).toBe(200);
    expect(res.body.length).toBeGreaterThan(0);
  });

  test('点赞视频', async () => {
    const res = await request(app)
      .post(`/api/v1/videos/${testVideo._id}/like`)
      .set('Authorization', `Bearer ${authToken}`);
    
    expect(res.statusCode).toBe(200);
    expect(res.body.message).toMatch(/成功/);
  });
});


// 使用supertest进行安全测试
describe('安全测试', () => {
  test('应该过滤XSS攻击', async () => {
    const res = await request(app)
      .post('/api/v1/comments')
      .send({
        content: '<script>alert("xss")</script>',
        videoId: '123'
      })
      .set('Authorization', `Bearer ${authToken}`);
    
    expect(res.body.content).not.toMatch(/<script>/);
  });

  test('应该防止未授权访问', async () => {
    const res = await request(app)
      .get('/api/v1/auth/me');
    
    expect(res.statusCode).toBe(401);
  });
});


// 使用Newman进行API监控
const newman = require('newman');

newman.run({
  collection: require('./api-tests.postman_collection.json'),
  reporters: 'cli',
  iterationCount: 10
}, (err) => {
  if (err) { throw err; }
  console.log('API监控完成');
});


// backend/scripts/generateTestData.js
const mongoose = require('mongoose');
const User = require('../models/User');
const Video = require('../models/Video');
const faker = require('faker');

async function generateData() {
  // 连接数据库
  await mongoose.connect('mongodb://localhost/douyin_h5_test');
  
  // 清空测试数据
  await User.deleteMany();
  await Video.deleteMany();
  
  // 生成测试用户
  const users = [];
  for (let i = 0; i < 10; i++) {
    users.push(await User.create({
      username: faker.internet.userName(),
      avatar: faker.image.avatar()
    }));
  }
  
  // 生成测试视频
  for (let i = 0; i < 50; i++) {
    await Video.create({
      title: faker.lorem.sentence(),
      description: faker.lorem.paragraph(),
      videoUrl: 'https://example.com/video.mp4',
      coverUrl: faker.image.imageUrl(),
      author: users[Math.floor(Math.random() * users.length)]._id,
      likes: Math.floor(Math.random() * 1000)
    });
  }
  
  console.log('测试数据生成完成');
  process.exit(0);
}

generateData();


// 使用Sentry进行错误监控
const Sentry = require('@sentry/node');

Sentry.init({
  dsn: 'your_dsn_here',
  tracesSampleRate: 1.0
});

// 包装Express应用
const express = require('express');
const app = express();

app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.errorHandler());


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


