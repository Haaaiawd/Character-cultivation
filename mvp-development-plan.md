# 修仙文字游戏MVP开发计划

## MVP开发思路

MVP (最小可行产品) 版本旨在以最小的工作量实现游戏核心功能，确保基本游戏流程可以运行，同时为后续扩展奠定基础。

### MVP核心目标
1. 实现基础角色创建系统
2. 实现基本的选择-结果游戏循环
3. 集成简单的RAG系统生成剧情
4. 设计插件接口但仅实现基础插件
5. 构建最小化数据存储和管理系统

## MVP功能范围

### 包含功能
- 用户注册和登录
- 基础角色创建 (属性分配、身份选择)
- 简单的修仙境界系统 (炼气、筑基阶段)
- 基本游戏循环 (剧情-选择-结果)
- 简单的RAG知识库和剧情生成
- 基本存档功能
- 核心插件接口定义

### 暂不包含
- 复杂的战斗系统
- 详细的物品和装备系统
- 高级修仙功法系统
- 复杂的世界地图和场景探索
- 多人互动功能
- 图形用户界面 (仅API接口)

## MVP技术实现简化

### 数据库简化
- 仅使用PostgreSQL单数据库
- 简化的数据模型和关系
- 暂不使用Redis缓存和MongoDB

### RAG系统简化
- 使用预设的小型知识库
- 简化的LLM调用流程
- 基础的上下文管理

### 插件系统简化
- 定义核心接口但功能有限
- 仅支持简单的事件挂钩
- 内置一个基础修仙插件

## MVP开发阶段划分

### 阶段1: 项目框架搭建 (1周)
- 建立基础项目结构
- 配置FastAPI框架
- 设置数据库连接
- 创建基础用户模型和API

### 阶段2: 角色系统实现 (1周)
- 角色数据模型设计
- 属性系统实现
- 身份选择机制
- 角色基础API

### 阶段3: 游戏核心循环 (2周)
- 游戏状态管理
- 选择-结果机制
- 存档系统
- 游戏会话API

### 阶段4: RAG系统集成 (2周)
- 基础知识库构建
- LangChain简单集成
- 剧情生成器实现
- 选择项生成

### 阶段5: 插件接口与示例 (1周)
- 插件接口定义
- 事件系统实现
- 基础修仙插件开发
- 插件管理API

### 阶段6: 测试与优化 (1周)
- 单元测试编写
- 集成测试
- 性能优化
- 文档完善

## MVP技术栈精简版

```
# 框架
FastAPI (异步Web框架)
SQLAlchemy (ORM)
Pydantic (数据验证)

# 数据库
PostgreSQL (关系型数据库)

# AI/RAG
LangChain (精简版)
OpenAI API (GPT模型)
FAISS (向量存储)

# 开发工具
Poetry (依赖管理)
pytest (测试框架)
Docker (容器化)
```

## MVP数据模型精简版

```python
# 用户模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    characters = relationship("Character", back_populates="user")
    game_saves = relationship("GameSave", back_populates="user")

# 角色模型
class Character(Base):
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    identity_id = Column(Integer, ForeignKey("identities.id"))
    level = Column(Integer, default=1)
    cultivation_stage = Column(String, default="炼气期一层")
    experience = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="characters")
    identity = relationship("Identity")
    attributes = relationship("CharacterAttribute", back_populates="character", uselist=False)
    game_states = relationship("GameState", back_populates="character")

# 角色属性
class CharacterAttribute(Base):
    __tablename__ = "character_attributes"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), unique=True)
    strength = Column(Integer, default=10)      # 力量
    agility = Column(Integer, default=10)       # 敏捷
    intelligence = Column(Integer, default=10)  # 智力
    constitution = Column(Integer, default=10)  # 体质
    perception = Column(Integer, default=10)    # 悟性
    luck = Column(Integer, default=10)          # 气运
    
    character = relationship("Character", back_populates="attributes")

# 身份模型
class Identity(Base):
    __tablename__ = "identities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    starting_benefits = Column(JSON)

# 游戏状态
class GameState(Base):
    __tablename__ = "game_states"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    current_scene_id = Column(String)
    story_history = Column(JSON, default=list)
    game_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    character = relationship("Character", back_populates="game_states")

# 游戏存档
class GameSave(Base):
    __tablename__ = "game_saves"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    character_id = Column(Integer, ForeignKey("characters.id"))
    game_state_id = Column(Integer, ForeignKey("game_states.id"))
    save_name = Column(String)
    save_slot = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="game_saves")
```

## MVP API端点精简版

```
# 认证API
POST /api/v1/auth/register
POST /api/v1/auth/login

# 角色API
POST /api/v1/characters
GET /api/v1/characters
GET /api/v1/characters/{id}

# 游戏API
POST /api/v1/game/start
POST /api/v1/game/choice
GET /api/v1/game/state/{game_session_id}
POST /api/v1/game/save
GET /api/v1/game/saves
POST /api/v1/game/load
```

## MVP的RAG系统简化设计

### 知识库结构
```
knowledge_base/
├── cultivation/             # 修炼体系
│   ├── stages.md           # 境界描述
│   └── methods.md          # 功法描述
├── world/                   # 世界观
│   ├── geography.md        # 地理
│   └── factions.md         # 门派和势力
└── characters/              # 角色背景
    ├── identities.md       # 身份描述
    └── npcs.md             # NPC角色
```

### RAG流程简化
1. 用简单的向量存储预处理知识库
2. 根据当前游戏状态构建检索查询
3. 获取最相关的知识库片段
4. 使用简单提示模板生成剧情和选择项
5. 处理玩家选择并更新游戏状态

## MVP插件系统简化设计

### 基础插件接口
```python
class BasePlugin:
    """基础插件接口"""
    
    name: str
    version: str
    author: str
    
    def initialize(self) -> bool:
        """插件初始化"""
        pass
    
    def handle_event(self, event_type: str, data: dict) -> dict:
        """处理游戏事件"""
        pass
```

### 简化的事件类型
```python
PLUGIN_EVENTS = {
    "character_created": "角色创建后触发",
    "game_started": "游戏开始时触发",
    "choice_made": "玩家做出选择后触发",
    "scene_generated": "新场景生成后触发"
}
```

## MVP示例插件: 基础修仙

```python
class BasicCultivationPlugin(BasePlugin):
    """基础修仙插件"""
    
    name = "basic_cultivation"
    version = "0.1.0"
    author = "XiuXian Games"
    
    # 修仙境界定义
    CULTIVATION_STAGES = [
        "炼气期一层", "炼气期二层", "炼气期三层", 
        "炼气期四层", "炼气期五层", "炼气期六层",
        "炼气期七层", "炼气期八层", "炼气期九层",
        "筑基期初期", "筑基期中期", "筑基期后期"
    ]
    
    def handle_event(self, event_type: str, data: dict) -> dict:
        if event_type == "character_created":
            # 初始化角色修炼属性
            data["character"]["cultivation"] = {
                "stage": self.CULTIVATION_STAGES[0],
                "progress": 0,
                "spiritual_power": 50
            }
            
        elif event_type == "choice_made":
            # 根据选择可能增加修炼进度
            if "cultivation_gain" in data["choice"]["effects"]:
                cultivation_data = data["character"]["cultivation"]
                current_stage_index = self.CULTIVATION_STAGES.index(cultivation_data["stage"])
                
                # 增加修炼进度
                cultivation_data["progress"] += data["choice"]["effects"]["cultivation_gain"]
                
                # 检查是否突破
                if cultivation_data["progress"] >= 100:
                    if current_stage_index < len(self.CULTIVATION_STAGES) - 1:
                        cultivation_data["stage"] = self.CULTIVATION_STAGES[current_stage_index + 1]
                        cultivation_data["progress"] = 0
                        data["messages"].append(f"恭喜！你成功突破到了{cultivation_data['stage']}")
        
        return data
```

## MVP实现路径

### 1. 建立项目基础框架
```bash
# 创建项目目录
mkdir -p xiuxian-game
cd xiuxian-game

# 初始化Poetry项目
poetry init

# 添加依赖
poetry add fastapi uvicorn sqlalchemy pydantic python-jose python-multipart alembic langchain openai faiss-cpu

# 创建基础目录结构
mkdir -p app/{api,core,models,schemas,repositories,services,utils} tests knowledge_base plugins
```

### 2. 设置数据库和配置
```python
# app/config/settings.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "修仙文字游戏"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "xiuxian_game")
    SQLALCHEMY_DATABASE_URI: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    class Config:
        case_sensitive = True

settings = Settings()
```

### 3. 实现基础数据模型和API
从上面定义的模型开始，实现基础API。

### 4. 实现简单的RAG系统
```python
# app/core/rag_system.py
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
from pathlib import Path

class RAGSystem:
    """简化的RAG系统"""
    
    def __init__(self):
        self.knowledge_base = None
        self.llm = OpenAI(temperature=0.7)
        self.embeddings = OpenAIEmbeddings()
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """加载知识库"""
        kb_dir = Path("knowledge_base")
        documents = []
        
        # 简单处理：直接读取文本文件
        for file_path in kb_dir.glob("**/*.md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # 这里可以根据文件路径添加元数据，简化版先不处理
                documents.append(content)
        
        # 创建向量存储
        self.knowledge_base = FAISS.from_texts(documents, self.embeddings)
    
    def generate_story(self, game_state, character):
        """生成剧情内容"""
        # 构建查询上下文
        query = f"角色：{character['name']}，境界：{character['cultivation_stage']}，当前场景：{game_state['current_scene_id']}"
        
        # 检索相关信息
        relevant_docs = self.knowledge_base.similarity_search(query, k=3)
        context = "\n".join([doc.page_content for doc in relevant_docs])
        
        # 构建提示
        prompt = PromptTemplate(
            template="""
            你是一个修仙文字游戏的AI讲述者。根据以下信息，生成一段引人入胜的剧情描述，并提供3个选择项。
            
            角色信息：{character}
            
            游戏历史：{history}
            
            相关背景知识：{context}
            
            请生成一段剧情描述（100-200字）和三个选择项（每个20-30字）。
            剧情：
            
            选择1：
            
            选择2：
            
            选择3：
            """,
            input_variables=["character", "history", "context"]
        )
        
        # 生成内容
        inputs = {
            "character": str(character),
            "history": str(game_state["story_history"][-3:] if game_state["story_history"] else "游戏开始"),
            "context": context
        }
        
        result = self.llm(prompt.format(**inputs))
        
        # 解析结果（简化版，实际需要更严格的解析）
        parts = result.split("选择")
        story = parts[0].strip().replace("剧情：", "").strip()
        choices = []
        
        for i in range(1, min(4, len(parts))):
            choice_text = parts[i].strip()
            if "：" in choice_text:
                choice_text = choice_text.split("：", 1)[1].strip()
            choices.append({
                "id": f"choice_{i}",
                "text": choice_text
            })
        
        return {
            "description": story,
            "choices": choices
        }
```

### 5. 实现基础插件系统
```python
# app/core/plugin_system.py
import importlib
import inspect
import os
from pathlib import Path
from typing import Dict, List, Any

class PluginManager:
    """简化的插件管理器"""
    
    def __init__(self):
        self.plugins = {}
        self.load_plugins()
    
    def load_plugins(self):
        """加载所有插件"""
        plugins_dir = Path("plugins")
        
        # 检查内置插件
        basic_plugin_path = plugins_dir / "basic_cultivation.py"
        if basic_plugin_path.exists():
            self._load_plugin_from_file(basic_plugin_path)
    
    def _load_plugin_from_file(self, file_path: Path):
        """从文件加载插件"""
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 查找插件类
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and hasattr(obj, "name") and hasattr(obj, "handle_event"):
                plugin = obj()
                self.plugins[plugin.name] = plugin
                print(f"Loaded plugin: {plugin.name} v{plugin.version}")
                break
    
    def emit_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送事件到所有插件"""
        result = data.copy()
        
        # 确保messages字段存在
        if "messages" not in result:
            result["messages"] = []
        
        # 发送到每个插件
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin_result = plugin.handle_event(event_type, result)
                if plugin_result:
                    result = plugin_result
            except Exception as e:
                print(f"Plugin {plugin_name} error on {event_type}: {str(e)}")
        
        return result
```

## MVP开发迭代策略

### 增量功能开发路径
1. **基础功能阶段**: 实现用户、角色创建和简单选择机制
2. **游戏循环阶段**: 完善游戏状态管理和存档功能
3. **RAG集成阶段**: 添加知识库和剧情生成能力
4. **插件系统阶段**: 实现插件接口和基础修仙插件

### 增量测试计划
每个阶段添加相应的测试，确保基本功能正常工作：
1. 单元测试: 测试各个组件的独立功能
2. 集成测试: 测试组件间的交互
3. API测试: 测试API端点的功能
4. 端到端测试: 测试完整游戏流程

## 成功标准

MVP版本成功的标准是：
1. 玩家能够创建角色并选择身份
2. 游戏能够生成基本的修仙剧情和选择项
3. 玩家能够做出选择并获得相应结果
4. 系统能够保存游戏进度
5. 基础的修仙境界系统能够正常工作
6. 插件接口设计合理并能支持基础插件

## 后续扩展计划

MVP完成后的扩展路径：
1. 完善RAG系统，提升剧情生成质量
2. 添加更多修仙功法和境界系统
3. 实现装备和物品系统
4. 扩展战斗系统
5. 增加NPC互动系统
6. 开发更多插件
7. 构建Web界面

这个MVP开发计划为AI开发团队提供了清晰的路径，确保能够快速实现一个基础功能完整的修仙文字游戏框架。