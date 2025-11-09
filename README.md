# 隐私保护推荐系统

一个基于马尔科夫链和Walrus存储的隐私保护推荐系统，使用Python和FastAPI构建。

## 功能特性

- 🔒 **隐私保护**: 使用Walrus去中心化存储保护用户数据隐私
- 🧠 **智能推荐**: 基于马尔科夫链分析用户行为模式
- 📊 **行为分析**: 深度分析用户行为序列和偏好
- 🚀 **高性能**: 异步处理，支持高并发请求
- 🔧 **可扩展**: 模块化设计，易于扩展和维护
- 📱 **RESTful API**: 完整的API接口支持

## 技术栈

- **后端框架**: FastAPI (Python)
- **数据存储**: Walrus 去中心化存储
- **机器学习**: 马尔科夫链模型
- **数据处理**: NumPy, Pandas
- **API文档**: OpenAPI/Swagger
- **测试框架**: pytest

## 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动应用

```bash
python main.py
```

应用将在 `http://localhost:8000` 启动。

## API文档

启动应用后，可以访问以下文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API端点

### 用户管理

#### 添加用户行为
```http
POST /api/v1/users/{user_id}/behaviors
Content-Type: application/json

{
  "user_id": "user123",
  "item_id": "item456",
  "behavior_type": "VIEW",
  "timestamp": "2024-01-01T12:00:00Z",
  "metadata": {"device": "mobile"}
}
```

#### 获取用户行为历史
```http
GET /api/v1/users/{user_id}/behaviors
```

#### 获取用户档案
```http
GET /api/v1/users/{user_id}/profile
```

#### 更新用户档案
```http
PUT /api/v1/users/{user_id}/profile
Content-Type: application/json

{
  "preferences": {"electronics": 10, "books": 5},
  "privacy_level": 2
}
```

### 推荐系统

#### 生成个性化推荐
```http
POST /api/v1/recommendations/generate
Content-Type: application/json

{
  "user_id": "user123",
  "num_recommendations": 5,
  "context": {"device": "mobile", "time_of_day": "evening"}
}
```

#### 获取用户推荐
```http
GET /api/v1/recommendations/users/{user_id}
```

#### 获取热门推荐
```http
GET /api/v1/recommendations/popular
```

#### 获取分类推荐
```http
GET /api/v1/recommendations/category/{category}
```

### 数据分析

#### 获取存储统计
```http
GET /api/v1/analytics/stats
```

#### 获取用户分析
```http
GET /api/v1/analytics/users/{user_id}
```

#### 生成数据哈希
```http
POST /api/v1/analytics/hash
Content-Type: application/json

{
  "user_id": "user123",
  "behavior": "click",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 核心算法

### 马尔科夫链模型

系统使用马尔科夫链分析用户行为序列，预测用户的下一步行为：

1. **状态定义**: 用户行为类型 + 项目ID (如: "VIEW_item123")
2. **转移矩阵**: 计算状态之间的转移概率
3. **预测算法**: 基于当前状态序列预测最可能的下一个状态

### 隐私保护机制

1. **数据加密**: 用户数据在存储前进行加密处理
2. **去中心化存储**: 使用Walrus分布式存储系统
3. **差分隐私**: 在推荐算法中添加噪声保护用户隐私
4. **数据最小化**: 只收集和处理必要的数据

### 推荐算法

推荐系统结合多种因素生成个性化推荐：

1. **行为模式**: 基于马尔科夫链预测用户行为
2. **时间衰减**: 考虑行为的时效性
3. **用户偏好**: 分析用户历史偏好
4. **热门程度**: 结合项目的热门程度
5. **隐私级别**: 根据用户隐私设置调整推荐策略

## 项目结构

```
Markov/
├── app/
│   ├── core/           # 核心配置和组件
│   │   ├── config.py   # 配置管理
│   │   ├── database.py # 数据库管理
│   │   └── walrus.py   # Walrus存储集成
│   ├── models/         # 数据模型
│   │   └── schemas.py  # Pydantic模型
│   ├── services/       # 业务逻辑
│   │   ├── markov_analyzer.py  # 马尔科夫链分析
│   │   └── recommender.py      # 推荐系统
│   └── routers/        # API路由
│       ├── users.py          # 用户管理API
│       ├── recommendations.py # 推荐API
│       └── analytics.py      # 分析API
├── tests/              # 测试文件
├── main.py            # 应用入口
└── requirements.txt   # 依赖列表
```

## 测试

运行测试套件：

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_markov_analyzer.py

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 性能优化

### 缓存策略

- **内存缓存**: 热点数据缓存在内存中
- **LRU缓存**: 使用最近最少使用策略
- **异步更新**: 后台异步更新缓存

### 并发处理

- **异步IO**: 使用async/await处理并发请求
- **连接池**: 数据库连接池管理
- **限流**: API请求速率限制

## 安全考虑

### 数据保护

- **加密传输**: 使用HTTPS传输数据
- **输入验证**: 严格的输入验证和清理
- **SQL注入防护**: 使用参数化查询
- **XSS防护**: 输出编码和转义

### 访问控制

- **API认证**: 基于token的API认证
- **权限管理**: 细粒度的权限控制
- **审计日志**: 记录重要操作日志


## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

