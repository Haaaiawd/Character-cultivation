# API接口规范文档

## 接口设计原则

### 1. RESTful设计规范
- 使用HTTP动词表示操作类型 (GET, POST, PUT, DELETE)
- URL资源命名使用复数形式
- 使用HTTP状态码表示操作结果
- 支持分页、排序、过滤查询参数

### 2. 统一响应格式
```python
# 成功响应格式
{
    "success": true,
    "message": "操作成功",
    "data": {
        # 具体数据内容
    },
    "timestamp": "2025-06-17T14:21:00Z"
}

# 错误响应格式
{
    "success": false,
    "message": "错误描述",
    "error_code": "VALIDATION_ERROR",
    "details": {
        "field": "具体错误信息"
    },
    "timestamp": "2025-06-17T14:21:00Z"
}
```

## 认证授权API

### 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "username": "player001",
    "email": "player@example.com",
    "password": "securepassword123"
}
```

**响应示例:**
```json
{
    "success": true,
    "message": "注册成功",
    "data": {
        "user_id": 1,
        "username": "player001",
        "email": "player@example.com",
        "created_at": "2025-06-17T14:21:00Z"
    }
}
```

### 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "player001",
    "password": "securepassword123"
}
```

**响应示例:**
```json
{
    "success": true,
    "message": "登录成功",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "expires_in": 3600
    }
}
```

## 角色管理API

### 创建角色
```http
POST /api/v1/characters
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "name": "逍遥子",
    "attributes": {
        "strength": 10,      // 力量
        "agility": 15,       // 敏捷
        "intelligence": 20,  // 智力
        "constitution": 12,  // 体质
        "perception": 18,    // 悟性
        "luck": 8           // 气运
    },
    "identity_id": 1,       // 身份ID (1: 散修, 2: 宗门弟子, 3: 世家子弟)
    "background": "一个寻求长生不老的凡人修士"
}
```

**响应示例:**
```json
{
    "success": true,
    "message": "角色创建成功",
    "data": {
        "character_id": 123,
        "name": "逍遥子",
        "level": 1,
        "cultivation_stage": "炼气初期",
        "attributes": {
            "strength": 10,
            "agility": 15,
            "intelligence": 20,
            "constitution": 12,
            "perception": 18,
            "luck": 8
        },
        "identity": {
            "id": 1,
            "name": "散修",
            "description": "独自修炼，不依附任何门派"
        },
        "health": 100,
        "spiritual_power": 50,
        "created_at": "2025-06-17T14:21:00Z"
    }
}
```

### 获取角色信息
```http
GET /api/v1/characters/{character_id}
Authorization: Bearer {access_token}
```

### 更新角色属性
```http
PUT /api/v1/characters/{character_id}/attributes
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "attribute_points": {
        "strength": 2,
        "intelligence": 3
    }
}
```

## 游戏核心API

### 开始游戏
```http
POST /api/v1/game/start
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "character_id": 123,
    "save_slot": 1  // 存档槽位 (可选)
}
```

**响应示例:**
```json
{
    "success": true,
    "message": "游戏开始",
    "data": {
        "game_session_id": "sess_abc123",
        "initial_scene": {
            "id": "scene_001",
            "title": "修仙之路的起点",
            "description": "你站在一座古老的仙山脚下，山峰云雾缭绕，隐约传来阵阵灵气波动。作为一名刚刚踏入修仙界的散修，你需要做出第一个重要选择。",
            "choices": [
                {
                    "id": "choice_001",
                    "text": "直接上山寻找修炼机缘",
                    "requirements": {
                        "min_perception": 15
                    }
                },
                {
                    "id": "choice_002", 
                    "text": "先在山脚村庄打听消息",
                    "requirements": {}
                },
                {
                    "id": "choice_003",
                    "text": "寻找其他散修结伴而行",
                    "requirements": {
                        "min_charisma": 10
                    }
                }
            ]
        }
    }
}
```

### 提交选择
```http
POST /api/v1/game/choice
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "game_session_id": "sess_abc123",
    "choice_id": "choice_002",
    "additional_data": {
        // 插件可能需要的额外数据
    }
}
```

**响应示例:**
```json
{
    "success": true,
    "message": "选择已处理",
    "data": {
        "choice_result": {
            "description": "你走进山脚下的小村庄，村民们对修仙者既敬畏又好奇。通过与村长的交谈，你了解到这座山被称为'青云峰'，山上确实有一处古老的洞府...",
            "effects": {
                "experience": 10,
                "reputation": 5,
                "items_gained": ["村民的祝福符"],
                "knowledge_gained": ["青云峰的传说"]
            }
        },
        "next_scene": {
            "id": "scene_002",
            "title": "村庄中的发现",
            "description": "在村庄中，你发现了一些有趣的线索...",
            "choices": [
                // 下一轮的选择项
            ]
        },
        "character_update": {
            "experience": 110,
            "level": 1,
            "new_skills": []
        }
    }
}
```

### 获取游戏状态
```http
GET /api/v1/game/state/{game_session_id}
Authorization: Bearer {access_token}
```

### 保存游戏
```http
POST /api/v1/game/save
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "game_session_id": "sess_abc123",
    "save_name": "青云峰探索",
    "save_slot": 1
}
```

### 加载存档
```http
POST /api/v1/game/load
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "save_id": 456
}
```

## 插件系统API

### 获取可用插件列表
```http
GET /api/v1/plugins
Authorization: Bearer {access_token}
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "plugins": [
            {
                "name": "xiuxian_basic",
                "version": "1.0.0",
                "display_name": "基础修仙系统",
                "description": "提供基础的修仙功法和境界系统",
                "author": "XiuXian Games",
                "enabled": true,
                "dependencies": []
            },
            {
                "name": "equipment_system",
                "version": "0.8.0",
                "display_name": "装备系统",
                "description": "提供武器、防具等装备系统",
                "author": "Community",
                "enabled": false,
                "dependencies": ["xiuxian_basic"]
            }
        ]
    }
}
```

### 启用/禁用插件
```http
PUT /api/v1/plugins/{plugin_name}/toggle
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "enabled": true
}
```

### 获取插件配置
```http
GET /api/v1/plugins/{plugin_name}/config
Authorization: Bearer {access_token}
```

### 更新插件配置
```http
PUT /api/v1/plugins/{plugin_name}/config
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "config": {
        "cultivation_speed_multiplier": 1.5,
        "max_cultivation_level": 100
    }
}
```

## WebSocket实时API

### 连接游戏WebSocket
```
ws://localhost:8000/ws/game/{game_session_id}
Authorization: Bearer {access_token}
```

### WebSocket消息格式

#### 客户端发送消息
```json
{
    "type": "make_choice",
    "data": {
        "choice_id": "choice_003",
        "timestamp": "2025-06-17T14:21:00Z"
    }
}
```

#### 服务端推送消息
```json
{
    "type": "story_update",
    "data": {
        "scene": {
            "description": "新的剧情内容...",
            "choices": [...]
        },
        "character_update": {
            "health": 95,
            "spiritual_power": 45
        }
    },
    "timestamp": "2025-06-17T14:21:00Z"
}
```

#### 实时事件类型
- `story_update`: 剧情更新
- `character_update`: 角色状态更新
- `choice_result`: 选择结果
- `plugin_event`: 插件事件
- `system_notification`: 系统通知
- `cultivation_progress`: 修炼进度更新

## 数据模型规范

### 角色属性模型
```python
class CharacterAttributes(BaseModel):
    strength: int = Field(ge=1, le=100, description="力量")
    agility: int = Field(ge=1, le=100, description="敏捷") 
    intelligence: int = Field(ge=1, le=100, description="智力")
    constitution: int = Field(ge=1, le=100, description="体质")
    perception: int = Field(ge=1, le=100, description="悟性")
    luck: int = Field(ge=1, le=100, description="气运")
    charisma: int = Field(ge=1, le=100, description="魅力")
```

### 游戏状态模型
```python
class GameState(BaseModel):
    session_id: str
    character_id: int
    current_scene_id: str
    story_history: List[StoryEvent]
    character_state: CharacterState
    inventory: List[Item]
    cultivation_progress: CultivationProgress
    active_effects: List[Effect]
    plugin_data: Dict[str, Any]
```

### 选择项模型
```python
class Choice(BaseModel):
    id: str
    text: str
    description: Optional[str] = None
    requirements: Dict[str, Any] = {}
    effects: Dict[str, Any] = {}
    unlock_conditions: Optional[Dict[str, Any]] = None
    plugin_source: Optional[str] = None
```

## 错误处理规范

### 错误代码定义
```python
ERROR_CODES = {
    # 认证相关 (1000-1099)
    "AUTH_TOKEN_INVALID": 1001,
    "AUTH_TOKEN_EXPIRED": 1002,
    "AUTH_PERMISSION_DENIED": 1003,
    
    # 用户相关 (1100-1199)
    "USER_NOT_FOUND": 1101,
    "USER_ALREADY_EXISTS": 1102,
    "USER_INVALID_CREDENTIALS": 1103,
    
    # 角色相关 (1200-1299)
    "CHARACTER_NOT_FOUND": 1201,
    "CHARACTER_CREATION_FAILED": 1202,
    "CHARACTER_INVALID_ATTRIBUTES": 1203,
    
    # 游戏相关 (1300-1399)
    "GAME_SESSION_NOT_FOUND": 1301,
    "GAME_INVALID_CHOICE": 1302,
    "GAME_SAVE_FAILED": 1303,
    
    # 插件相关 (1400-1499)
    "PLUGIN_NOT_FOUND": 1401,
    "PLUGIN_LOAD_FAILED": 1402,
    "PLUGIN_DEPENDENCY_MISSING": 1403,
    
    # 系统相关 (1500-1599)
    "SYSTEM_INTERNAL_ERROR": 1501,
    "SYSTEM_SERVICE_UNAVAILABLE": 1502,
    "SYSTEM_RATE_LIMIT_EXCEEDED": 1503
}
```

### 错误响应示例
```json
{
    "success": false,
    "message": "角色属性分配无效",
    "error_code": "CHARACTER_INVALID_ATTRIBUTES",
    "details": {
        "total_points": "属性点总和不能超过100",
        "negative_values": "属性值不能为负数"
    },
    "timestamp": "2025-06-17T14:21:00Z"
}
```

## 分页与查询规范

### 分页参数
```http
GET /api/v1/characters?page=1&size=20&sort=created_at&order=desc
```

### 分页响应格式
```json
{
    "success": true,
    "data": {
        "items": [...],
        "pagination": {
            "page": 1,
            "size": 20,
            "total": 150,
            "pages": 8,
            "has_next": true,
            "has_prev": false
        }
    }
}
```

## 版本控制

### API版本策略
- URL路径版本控制: `/api/v1/`, `/api/v2/`
- 向下兼容原则: v2版本必须兼容v1的核心功能
- 废弃通知: 在响应头中包含废弃警告

### 版本升级路径
```http
# v1 API (当前)
GET /api/v1/characters/{id}

# v2 API (未来)
GET /api/v2/characters/{id}
# 添加新字段，保持旧字段兼容
```

## 安全规范

### 请求限制
- 认证接口: 每分钟最多10次尝试
- 游戏接口: 每秒最多5次请求
- 插件接口: 每分钟最多30次请求

### 输入验证
- 所有输入参数必须经过Pydantic验证
- 字符串长度限制
- 数值范围检查
- SQL注入防护

### 数据脱敏
- 用户密码不得在任何响应中返回
- 敏感配置信息需要脱敏处理
- 日志中避免记录敏感数据

这个API接口规范为AI开发提供了详细的接口定义和使用指南，确保系统各模块间的标准化通信。