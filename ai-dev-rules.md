# AI开发规范与指导文档

## 项目概述
修仙文字游戏 - 基于RAG技术的沉浸式修仙文字游戏，支持MOD扩展

## 核心开发原则

### 1. 迭代开发原则
- **渐进式开发**: 先实现核心功能，再逐步完善
- **最小可行产品(MVP)**: 第一版只需要基本的游戏流程能跑通
- **接口先行**: 所有功能模块必须先定义接口，再实现具体功能

### 2. 代码组织原则
- **模块化设计**: 每个功能模块独立，便于AI分别开发
- **接口标准化**: 所有模块间通信必须通过定义好的接口
- **插件友好**: 核心系统必须为后续插件扩展预留接口

## 技术栈规定

### 后端技术栈
```
主框架: FastAPI (Python 3.9+)
数据库: PostgreSQL + Redis + MongoDB
RAG框架: LangChain + OpenAI API
依赖管理: Poetry
容器化: Docker + Docker Compose
```

### 核心依赖库
```
fastapi==0.104.1
langchain==0.0.350
openai==1.3.0
sqlalchemy==2.0.23
redis==5.0.1
pymongo==4.6.0
pydantic==2.5.0
uvicorn==0.24.0
pytest==7.4.3
```

### 开发工具
```
代码格式化: black, isort
类型检查: mypy
测试框架: pytest
API文档: FastAPI自动生成
```

## AI开发任务流程

### 阶段1: 核心框架搭建
1. **项目结构初始化**
   - 创建标准Python项目结构
   - 配置poetry依赖管理
   - 设置Docker开发环境

2. **基础API框架**
   - 实现FastAPI基础应用
   - 配置数据库连接
   - 实现基础中间件

3. **核心数据模型**
   - 定义用户、角色、游戏状态数据模型
   - 实现基础CRUD操作
   - 配置数据库迁移

### 阶段2: 游戏核心逻辑
1. **角色系统**
   - 实现角色创建API
   - 属性点分配系统
   - 身份选择机制

2. **基础游戏循环**
   - 游戏状态管理
   - 简单的选择-结果机制
   - 存档系统

3. **RAG集成**
   - 基础知识库构建
   - 简单的剧情生成
   - 选择项生成

### 阶段3: 插件系统
1. **插件接口定义**
   - 插件基类设计
   - 事件系统
   - 插件管理器

2. **示例插件开发**
   - 简单的修仙功法插件
   - 装备系统插件

## 接口设计规范

### API接口规范
```python
# 所有API接口必须遵循以下规范：
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class BaseRequest(BaseModel):
    # 基础请求模型
    pass
```

### 数据库接口规范
```python
# 所有数据访问必须通过Repository模式
class BaseRepository:
    async def create(self, entity: BaseModel) -> int:
        pass
    
    async def get_by_id(self, id: int) -> Optional[BaseModel]:
        pass
    
    async def update(self, id: int, updates: Dict[str, Any]) -> bool:
        pass
    
    async def delete(self, id: int) -> bool:
        pass
```

### 插件接口规范
```python
class BasePlugin:
    name: str
    version: str
    author: str
    
    def initialize(self) -> bool:
        """插件初始化"""
        pass
    
    def handle_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理游戏事件"""
        pass
    
    def cleanup(self) -> bool:
        """插件清理"""
        pass
```

## 代码质量要求

### 1. 代码风格
- 使用black进行代码格式化
- 使用isort进行import排序
- 遵循PEP 8规范
- 所有函数必须有类型注解

### 2. 测试要求
- 每个功能模块必须有对应的单元测试
- API接口必须有集成测试
- 测试覆盖率不低于80%

### 3. 文档要求
- 所有类和函数必须有docstring
- API接口自动生成OpenAPI文档
- 重要业务逻辑必须有注释说明

## 错误处理规范

### 统一异常处理
```python
class GameException(Exception):
    def __init__(self, message: str, error_code: int = 500):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(GameException):
    def __init__(self, message: str):
        super().__init__(message, 400)

class NotFoundError(GameException):
    def __init__(self, message: str):
        super().__init__(message, 404)
```

## 日志规范
```python
import logging
import structlog

# 使用结构化日志
logger = structlog.get_logger(__name__)

# 日志级别：
# DEBUG: 调试信息
# INFO: 一般信息
# WARNING: 警告信息
# ERROR: 错误信息
# CRITICAL: 严重错误
```

## 安全规范

### 1. 输入验证
- 所有用户输入必须使用Pydantic进行验证
- 防止SQL注入、XSS攻击
- 输入长度限制和格式检查

### 2. 插件安全
- 插件运行在沙箱环境中
- 限制插件的系统资源访问
- 插件代码审查机制

## 性能要求

### 1. 响应时间
- API接口响应时间 < 500ms
- RAG生成响应时间 < 2s
- 数据库查询 < 100ms

### 2. 并发处理
- 支持至少100并发用户
- 使用异步编程提高性能
- 合理使用缓存减少数据库压力

## AI开发注意事项

### 1. 任务分解
- 每个开发任务必须足够小，能在一次AI对话中完成
- 任务之间依赖关系要清晰
- 提供详细的需求描述和验收标准

### 2. 代码审查
- AI生成的代码必须符合上述规范
- 重点检查接口实现是否正确
- 确保扩展性和插件兼容性

### 3. 测试验证
- 每个功能完成后必须有对应的测试用例
- 集成测试确保模块间协作正常
- 性能测试验证系统指标

## 版本管理

### Git工作流
```
main分支: 生产环境代码
develop分支: 开发环境代码
feature/*: 功能开发分支
hotfix/*: 紧急修复分支
```

### 版本号规范
遵循语义化版本控制(SemVer)
- 主版本号：不兼容的API修改
- 次版本号：向下兼容的功能新增
- 修订号：向下兼容的问题修正

## 部署规范

### Docker配置
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 环境变量配置
```bash
# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost/gamedb
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017/gamedb

# AI服务配置
OPENAI_API_KEY=your_openai_api_key
RAG_MODEL=gpt-3.5-turbo

# 应用配置
DEBUG=False
SECRET_KEY=your_secret_key
LOG_LEVEL=INFO
```

这是AI开发团队必须严格遵循的开发规范，确保项目的可维护性和扩展性。