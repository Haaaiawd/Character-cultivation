# 项目架构设计文档

## 系统整体架构

### 分层架构设计
```
┌─────────────────────────────────────────┐
│                前端层                    │
│  Web界面 | 管理后台 | API文档            │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│                API层                     │
│  REST API | WebSocket | 插件API         │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│              业务逻辑层                  │
│  游戏引擎 | 角色系统 | 剧情系统 | 插件管理 │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│               数据访问层                 │
│  Repository | ORM | 缓存管理             │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│                AI服务层                  │
│  RAG引擎 | LLM服务 | 知识库管理          │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│               基础设施层                 │
│  PostgreSQL | Redis | MongoDB | Vector DB│
└─────────────────────────────────────────┘
```

## 项目目录结构

```
xiuxian-game/
├── app/                          # 主应用目录
│   ├── __init__.py
│   ├── main.py                   # FastAPI应用入口
│   ├── config/                   # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py           # 应用配置
│   │   └── database.py           # 数据库配置
│   ├── api/                      # API路由
│   │   ├── __init__.py
│   │   ├── deps.py               # 依赖注入
│   │   ├── v1/                   # API版本1
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # 认证相关API
│   │   │   ├── character.py      # 角色相关API
│   │   │   ├── game.py           # 游戏核心API
│   │   │   └── plugin.py         # 插件管理API
│   ├── core/                     # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── game_engine.py        # 游戏引擎
│   │   ├── character_system.py   # 角色系统
│   │   ├── story_system.py       # 剧情系统
│   │   ├── plugin_system.py      # 插件系统
│   │   └── rag_system.py         # RAG系统
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py               # 基础模型
│   │   ├── user.py               # 用户模型
│   │   ├── character.py          # 角色模型
│   │   ├── game_state.py         # 游戏状态模型
│   │   └── plugin.py             # 插件模型
│   ├── schemas/                  # Pydantic模式
│   │   ├── __init__.py
│   │   ├── base.py               # 基础模式
│   │   ├── user.py               # 用户模式
│   │   ├── character.py          # 角色模式
│   │   ├── game.py               # 游戏模式
│   │   └── plugin.py             # 插件模式
│   ├── repositories/             # 数据访问层
│   │   ├── __init__.py
│   │   ├── base.py               # 基础仓库
│   │   ├── user.py               # 用户仓库
│   │   ├── character.py          # 角色仓库
│   │   └── game_state.py         # 游戏状态仓库
│   ├── services/                 # 业务服务层
│   │   ├── __init__.py
│   │   ├── auth_service.py       # 认证服务
│   │   ├── character_service.py  # 角色服务
│   │   ├── game_service.py       # 游戏服务
│   │   └── plugin_service.py     # 插件服务
│   └── utils/                    # 工具类
│       ├── __init__.py
│       ├── security.py           # 安全工具
│       ├── logger.py             # 日志工具
│       └── exceptions.py         # 异常定义
├── plugins/                      # 插件目录
│   ├── __init__.py
│   ├── base_plugin.py            # 插件基类
│   └── examples/                 # 示例插件
│       ├── xiuxian_basic/        # 基础修仙插件
│       └── equipment_system/     # 装备系统插件
├── knowledge_base/               # 知识库
│   ├── xiuxian_lore/            # 修仙世界观
│   ├── character_backgrounds/    # 角色背景
│   └── cultivation_methods/      # 修炼功法
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── conftest.py              # 测试配置
│   ├── unit/                    # 单元测试
│   ├── integration/             # 集成测试
│   └── e2e/                     # 端到端测试
├── scripts/                      # 脚本目录
│   ├── init_db.py               # 数据库初始化
│   ├── migrate.py               # 数据迁移
│   └── seed_data.py             # 种子数据
├── docker/                       # Docker配置
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
├── docs/                         # 文档目录
│   ├── api/                     # API文档
│   ├── architecture/            # 架构文档
│   └── plugins/                 # 插件开发文档
├── pyproject.toml               # Poetry配置
├── poetry.lock                  # 依赖锁定文件
├── .env.example                 # 环境变量示例
├── .gitignore                   # Git忽略文件
└── README.md                    # 项目说明
```

## 核心模块设计

### 1. 游戏引擎 (game_engine.py)
```python
class GameEngine:
    """游戏引擎核心类"""
    
    def __init__(self):
        self.character_system = CharacterSystem()
        self.story_system = StorySystem()
        self.plugin_manager = PluginManager()
        self.rag_system = RAGSystem()
    
    async def create_character(self, user_id: int, character_data: dict) -> Character:
        """创建角色"""
        pass
    
    async def process_choice(self, user_id: int, choice_id: int) -> GameState:
        """处理玩家选择"""
        pass
    
    async def generate_story(self, game_state: GameState) -> StoryResponse:
        """生成剧情"""
        pass
    
    async def save_game(self, user_id: int, game_state: GameState) -> bool:
        """保存游戏"""
        pass
```

### 2. 角色系统 (character_system.py)
```python
class CharacterSystem:
    """角色系统"""
    
    async def create_character(self, creation_data: CharacterCreationData) -> Character:
        """创建角色"""
        pass
    
    async def allocate_points(self, character: Character, allocation: dict) -> Character:
        """分配属性点"""
        pass
    
    async def choose_identity(self, character: Character, identity_id: int) -> Character:
        """选择身份"""
        pass
    
    async def level_up(self, character: Character) -> Character:
        """角色升级"""
        pass
```

### 3. 剧情系统 (story_system.py)
```python
class StorySystem:
    """剧情系统"""
    
    async def generate_scene(self, game_state: GameState) -> Scene:
        """生成场景"""
        pass
    
    async def generate_choices(self, scene: Scene, character: Character) -> List[Choice]:
        """生成选择项"""
        pass
    
    async def apply_choice_effect(self, character: Character, choice: Choice) -> ChoiceEffect:
        """应用选择效果"""
        pass
```

### 4. 插件系统 (plugin_system.py)
```python
class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.event_bus = EventBus()
    
    async def load_plugin(self, plugin_path: str) -> bool:
        """加载插件"""
        pass
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        pass
    
    async def emit_event(self, event_type: str, data: dict) -> dict:
        """发送事件"""
        pass
```

### 5. RAG系统 (rag_system.py)
```python
class RAGSystem:
    """RAG系统"""
    
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.llm_client = LLMClient()
        self.vector_store = VectorStore()
    
    async def generate_story_content(self, context: dict) -> str:
        """生成剧情内容"""
        pass
    
    async def generate_choices(self, context: dict) -> List[dict]:
        """生成选择项"""
        pass
    
    async def search_knowledge(self, query: str) -> List[KnowledgeItem]:
        """搜索知识库"""
        pass
```

## 数据模型设计

### 核心实体关系图
```
User (用户)
  ├── Characters (角色) [1:N]
  └── GameSaves (存档) [1:N]

Character (角色)
  ├── Attributes (属性)
  ├── Identity (身份)
  ├── Cultivation (修为)
  └── Items (物品) [1:N]

GameState (游戏状态)
  ├── CurrentScene (当前场景)
  ├── StoryHistory (剧情历史)
  └── Choices (选择项) [1:N]

Plugin (插件)
  ├── PluginConfig (配置)
  └── PluginData (数据)
```

## 接口设计标准

### REST API设计规范
```
基础路径: /api/v1

用户相关:
POST   /auth/register        # 用户注册
POST   /auth/login          # 用户登录
POST   /auth/logout         # 用户登出

角色相关:
POST   /characters          # 创建角色
GET    /characters/{id}     # 获取角色信息
PUT    /characters/{id}     # 更新角色信息
DELETE /characters/{id}     # 删除角色

游戏相关:
POST   /game/start          # 开始游戏
GET    /game/state          # 获取游戏状态
POST   /game/choice         # 提交选择
POST   /game/save           # 保存游戏
GET    /game/saves          # 获取存档列表

插件相关:
GET    /plugins             # 获取插件列表
POST   /plugins/install     # 安装插件
DELETE /plugins/{name}      # 卸载插件
```

### WebSocket接口
```
连接路径: /ws/game/{user_id}

消息类型:
- game_state_update      # 游戏状态更新
- story_generated        # 剧情生成完成
- choice_result          # 选择结果
- plugin_event           # 插件事件
```

## 性能设计考虑

### 1. 缓存策略
```python
# Redis缓存层级
CACHE_LEVELS = {
    "user_session": 3600,      # 用户会话 1小时
    "character_data": 1800,    # 角色数据 30分钟
    "game_state": 900,         # 游戏状态 15分钟
    "story_content": 86400,    # 剧情内容 24小时
}
```

### 2. 数据库优化
- 角色数据使用PostgreSQL确保一致性
- 游戏状态使用Redis实现快速读写
- 剧情内容使用MongoDB支持灵活结构
- RAG知识库使用Vector DB优化检索

### 3. 异步处理
- 所有数据库操作使用异步IO
- RAG生成使用后台任务队列
- 插件事件使用异步事件总线

## 安全架构设计

### 1. 认证授权
```python
# JWT Token认证
AUTH_CONFIG = {
    "algorithm": "HS256",
    "expire_minutes": 60,
    "refresh_expire_days": 7
}

# 权限控制
PERMISSIONS = {
    "user": ["read_character", "write_character", "play_game"],
    "admin": ["manage_plugins", "view_logs", "manage_users"],
    "plugin": ["emit_events", "read_game_state"]
}
```

### 2. 插件沙箱
```python
# 插件资源限制
PLUGIN_LIMITS = {
    "memory_mb": 100,          # 内存限制100MB
    "cpu_percent": 10,         # CPU使用率10%
    "execution_time": 5,       # 执行时间5秒
    "file_access": "readonly"  # 文件访问权限
}
```

## 扩展性设计

### 1. 插件扩展点
```python
PLUGIN_HOOKS = {
    "character_creation": "角色创建时触发",
    "choice_before": "选择前触发", 
    "choice_after": "选择后触发",
    "story_generation": "剧情生成时触发",
    "level_up": "升级时触发",
    "save_game": "保存游戏时触发"
}
```

### 2. 配置驱动
- 游戏规则通过配置文件定义
- 修仙体系通过插件扩展
- UI界面支持主题定制
- API接口支持版本控制

### 3. 水平扩展
- 无状态API服务器支持负载均衡
- 数据库读写分离
- 缓存集群部署
- 容器化部署支持K8s

## 监控与运维

### 1. 日志系统
```python
LOG_CONFIG = {
    "format": "structured",    # 结构化日志
    "level": "INFO",          # 日志级别
    "rotation": "daily",      # 日志轮转
    "retention": 30           # 保留天数
}
```

### 2. 监控指标
- API响应时间和错误率
- 数据库连接池状态
- 内存和CPU使用率
- 用户在线数量
- 插件性能指标

### 3. 健康检查
```python
HEALTH_CHECKS = {
    "database": "检查数据库连接",
    "redis": "检查Redis连接",
    "rag_service": "检查RAG服务",
    "plugins": "检查插件状态"
}
```

这个架构设计为AI开发提供了清晰的模块划分和接口定义，确保系统的可扩展性和可维护性。