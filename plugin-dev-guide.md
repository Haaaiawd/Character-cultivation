# 插件系统开发规范

## 插件架构设计

### 核心设计理念
插件系统采用事件驱动架构，通过定义标准化接口和事件机制，让第三方开发者能够轻松扩展游戏功能。系统确保核心功能稳定性的同时，为插件提供足够的扩展能力。

### 插件生命周期
```
加载 -> 初始化 -> 事件监听 -> 业务处理 -> 清理 -> 卸载
```

## 插件基础接口定义

### BasePlugin基类
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

class BasePlugin(ABC):
    """插件基类，所有插件必须继承此类"""
    
    # 插件基本信息 (必须重写)
    name: str = ""
    version: str = "1.0.0"
    author: str = ""
    description: str = ""
    dependencies: List[str] = []
    
    def __init__(self):
        self.logger = logging.getLogger(f"plugin.{self.name}")
        self.enabled = False
        self.config = {}
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        插件初始化方法
        
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    def handle_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理游戏事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
            
        Returns:
            Dict[str, Any]: 处理后的数据
        """
        pass
    
    def cleanup(self) -> bool:
        """
        插件清理方法
        
        Returns:
            bool: 清理是否成功
        """
        return True
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证插件配置
        
        Args:
            config: 配置数据
            
        Returns:
            bool: 配置是否有效
        """
        return True
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            Dict[str, Any]: 默认配置
        """
        return {}
```

## 事件系统规范

### 核心事件类型
```python
CORE_EVENTS = {
    # 用户相关事件
    "user_registered": {
        "description": "用户注册完成",
        "data": {"user_id": int, "username": str, "email": str}
    },
    "user_login": {
        "description": "用户登录",
        "data": {"user_id": int, "username": str}
    },
    
    # 角色相关事件
    "character_created": {
        "description": "角色创建完成",
        "data": {
            "character_id": int,
            "user_id": int,
            "character": Dict,
            "initial_attributes": Dict
        }
    },
    "character_level_up": {
        "description": "角色升级",
        "data": {
            "character_id": int,
            "old_level": int,
            "new_level": int,
            "character": Dict
        }
    },
    
    # 游戏流程事件
    "game_started": {
        "description": "游戏开始",
        "data": {
            "game_session_id": str,
            "character_id": int,
            "character": Dict,
            "initial_scene": Dict
        }
    },
    "scene_generated": {
        "description": "新场景生成",
        "data": {
            "game_session_id": str,
            "scene": Dict,
            "character": Dict,
            "context": Dict
        }
    },
    "choice_made": {
        "description": "玩家做出选择",
        "data": {
            "game_session_id": str,
            "choice_id": str,
            "choice": Dict,
            "character": Dict,
            "game_state": Dict
        }
    },
    "choice_processed": {
        "description": "选择处理完成",
        "data": {
            "game_session_id": str,
            "choice_result": Dict,
            "character_changes": Dict,
            "next_scene": Dict
        }
    },
    
    # 修炼相关事件
    "cultivation_progress": {
        "description": "修炼进度更新",
        "data": {
            "character_id": int,
            "cultivation_data": Dict,
            "progress_gain": int
        }
    },
    "breakthrough_attempt": {
        "description": "尝试突破境界",
        "data": {
            "character_id": int,
            "current_stage": str,
            "target_stage": str,
            "success_chance": float
        }
    },
    "breakthrough_success": {
        "description": "境界突破成功",
        "data": {
            "character_id": int,
            "old_stage": str,
            "new_stage": str,
            "benefits": Dict
        }
    },
    
    # 存档相关事件
    "game_saved": {
        "description": "游戏保存",
        "data": {
            "save_id": int,
            "user_id": int,
            "character_id": int,
            "save_name": str
        }
    }
}
```

### 事件处理优先级
```python
EVENT_PRIORITY = {
    "high": 1,      # 系统关键事件，优先处理
    "normal": 2,    # 常规游戏事件
    "low": 3        # 非关键事件，如日志记录
}
```

## 插件配置系统

### 配置文件格式
```json
{
    "name": "basic_cultivation",
    "enabled": true,
    "config": {
        "cultivation_speed_multiplier": 1.0,
        "breakthrough_base_chance": 0.5,
        "max_cultivation_level": 100,
        "spiritual_power_per_level": 10,
        "custom_stages": [
            {
                "name": "炼气期一层",
                "level": 1,
                "requirements": {"experience": 0}
            }
        ]
    },
    "permissions": [
        "modify_character_attributes",
        "generate_story_content",
        "access_game_state"
    ]
}
```

### 权限系统
```python
PLUGIN_PERMISSIONS = {
    # 角色相关权限
    "read_character_data": "读取角色数据",
    "modify_character_attributes": "修改角色属性",
    "modify_character_level": "修改角色等级",
    "access_character_inventory": "访问角色物品",
    
    # 游戏状态权限
    "read_game_state": "读取游戏状态",
    "modify_game_state": "修改游戏状态",
    "access_story_history": "访问剧情历史",
    
    # 内容生成权限
    "generate_story_content": "生成剧情内容",
    "modify_scene_data": "修改场景数据",
    "create_custom_choices": "创建自定义选择",
    
    # 系统权限
    "access_database": "访问数据库",
    "emit_custom_events": "发送自定义事件",
    "register_api_endpoints": "注册API端点"
}
```

## 插件开发示例

### 基础修仙插件实现
```python
from plugins.base_plugin import BasePlugin
from typing import Dict, Any, List
import random

class BasicCultivationPlugin(BasePlugin):
    """基础修仙插件 - 提供修炼境界和突破机制"""
    
    name = "basic_cultivation"
    version = "1.0.0"
    author = "XiuXian Games"
    description = "提供基础的修炼境界系统和突破机制"
    dependencies = []
    
    # 修炼境界定义
    CULTIVATION_STAGES = [
        {"name": "炼气期一层", "level": 1, "spiritual_power": 50},
        {"name": "炼气期二层", "level": 2, "spiritual_power": 60},
        {"name": "炼气期三层", "level": 3, "spiritual_power": 75},
        {"name": "炼气期四层", "level": 4, "spiritual_power": 90},
        {"name": "炼气期五层", "level": 5, "spiritual_power": 110},
        {"name": "炼气期六层", "level": 6, "spiritual_power": 130},
        {"name": "炼气期七层", "level": 7, "spiritual_power": 155},
        {"name": "炼气期八层", "level": 8, "spiritual_power": 180},
        {"name": "炼气期九层", "level": 9, "spiritual_power": 210},
        {"name": "筑基期初期", "level": 10, "spiritual_power": 300},
        {"name": "筑基期中期", "level": 11, "spiritual_power": 400},
        {"name": "筑基期后期", "level": 12, "spiritual_power": 500}
    ]
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            self.logger.info(f"初始化{self.name}插件")
            
            # 加载配置
            default_config = self.get_default_config()
            self.config = {**default_config, **self.config}
            
            # 验证境界数据
            if not self._validate_stages():
                self.logger.error("境界数据验证失败")
                return False
            
            self.enabled = True
            self.logger.info(f"{self.name}插件初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"插件初始化失败: {str(e)}")
            return False
    
    def handle_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理游戏事件"""
        try:
            if event_type == "character_created":
                return self._handle_character_created(data)
            elif event_type == "choice_made":
                return self._handle_choice_made(data)
            elif event_type == "scene_generated":
                return self._handle_scene_generated(data)
            else:
                return data
                
        except Exception as e:
            self.logger.error(f"事件处理错误 ({event_type}): {str(e)}")
            return data
    
    def _handle_character_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理角色创建事件"""
        character = data.get("character", {})
        
        # 初始化修炼数据
        initial_stage = self.CULTIVATION_STAGES[0]
        cultivation_data = {
            "stage": initial_stage["name"],
            "level": initial_stage["level"],
            "progress": 0,
            "spiritual_power": initial_stage["spiritual_power"],
            "cultivation_points": 0,
            "breakthrough_attempts": 0
        }
        
        # 添加到角色数据
        character["cultivation"] = cultivation_data
        data["character"] = character
        
        # 添加系统消息
        if "messages" not in data:
            data["messages"] = []
        data["messages"].append(f"踏入修仙之路，当前境界：{cultivation_data['stage']}")
        
        self.logger.info(f"角色 {character.get('name')} 初始化修炼数据完成")
        return data
    
    def _handle_choice_made(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理选择事件"""
        choice = data.get("choice", {})
        character = data.get("character", {})
        
        # 检查选择是否包含修炼相关效果
        choice_effects = choice.get("effects", {})
        
        if "cultivation_gain" in choice_effects:
            cultivation_gain = choice_effects["cultivation_gain"]
            data = self._apply_cultivation_progress(data, cultivation_gain)
        
        if "spiritual_power_gain" in choice_effects:
            sp_gain = choice_effects["spiritual_power_gain"]
            data = self._apply_spiritual_power_gain(data, sp_gain)
        
        # 检查是否触发随机修炼机会
        if self._should_trigger_cultivation_event(choice, character):
            data = self._trigger_random_cultivation_event(data)
        
        return data
    
    def _handle_scene_generated(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理场景生成事件"""
        scene = data.get("scene", {})
        character = data.get("character", {})
        cultivation_data = character.get("cultivation", {})
        
        # 根据修炼境界调整场景选择项
        choices = scene.get("choices", [])
        modified_choices = []
        
        for choice in choices:
            # 检查选择项的境界要求
            requirements = choice.get("requirements", {})
            if "min_cultivation_level" in requirements:
                min_level = requirements["min_cultivation_level"]
                current_level = cultivation_data.get("level", 1)
                
                if current_level < min_level:
                    # 境界不足，禁用选择项
                    choice["disabled"] = True
                    choice["disabled_reason"] = f"需要修炼境界达到{min_level}级"
            
            # 添加修炼相关的选择项
            if choice.get("type") == "cultivation":
                choice = self._enhance_cultivation_choice(choice, cultivation_data)
            
            modified_choices.append(choice)
        
        # 可能添加修炼相关的额外选择项
        if self._should_add_cultivation_choices(scene, character):
            extra_choices = self._generate_cultivation_choices(cultivation_data)
            modified_choices.extend(extra_choices)
        
        scene["choices"] = modified_choices
        data["scene"] = scene
        
        return data
    
    def _apply_cultivation_progress(self, data: Dict[str, Any], progress_gain: int) -> Dict[str, Any]:
        """应用修炼进度"""
        character = data["character"]
        cultivation_data = character.get("cultivation", {})
        
        # 应用配置中的修炼速度倍数
        speed_multiplier = self.config.get("cultivation_speed_multiplier", 1.0)
        actual_gain = int(progress_gain * speed_multiplier)
        
        old_progress = cultivation_data.get("progress", 0)
        cultivation_data["progress"] = old_progress + actual_gain
        cultivation_data["cultivation_points"] = cultivation_data.get("cultivation_points", 0) + actual_gain
        
        # 检查是否可以突破
        if cultivation_data["progress"] >= 100:
            data = self._attempt_breakthrough(data)
        
        # 添加消息
        if "messages" not in data:
            data["messages"] = []
        data["messages"].append(f"修炼进度增加 {actual_gain} 点")
        
        character["cultivation"] = cultivation_data
        data["character"] = character
        
        return data
    
    def _attempt_breakthrough(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """尝试突破境界"""
        character = data["character"]
        cultivation_data = character["cultivation"]
        
        current_level = cultivation_data.get("level", 1)
        current_stage = cultivation_data.get("stage", "")
        
        # 检查是否已达到最高境界
        if current_level >= len(self.CULTIVATION_STAGES):
            return data
        
        # 计算突破成功率
        base_chance = self.config.get("breakthrough_base_chance", 0.5)
        attempts = cultivation_data.get("breakthrough_attempts", 0)
        # 每次失败后增加成功率
        success_chance = min(base_chance + (attempts * 0.1), 0.95)
        
        cultivation_data["breakthrough_attempts"] = attempts + 1
        
        # 进行突破判定
        if random.random() < success_chance:
            # 突破成功
            new_stage_data = self.CULTIVATION_STAGES[current_level]
            cultivation_data["stage"] = new_stage_data["name"]
            cultivation_data["level"] = new_stage_data["level"]
            cultivation_data["spiritual_power"] = new_stage_data["spiritual_power"]
            cultivation_data["progress"] = 0
            cultivation_data["breakthrough_attempts"] = 0
            
            # 添加成功消息
            if "messages" not in data:
                data["messages"] = []
            data["messages"].append(f"🎉 恭喜！成功突破到 {new_stage_data['name']}")
            
            # 发送突破成功事件
            breakthrough_data = {
                "character_id": character.get("id"),
                "old_stage": current_stage,
                "new_stage": new_stage_data["name"],
                "benefits": {
                    "spiritual_power_increase": new_stage_data["spiritual_power"] - cultivation_data.get("spiritual_power", 0)
                }
            }
            # 这里应该通过事件总线发送事件，简化版暂时省略
            
        else:
            # 突破失败
            cultivation_data["progress"] = max(cultivation_data["progress"] - 20, 0)
            
            if "messages" not in data:
                data["messages"] = []
            data["messages"].append(f"💥 突破失败！修炼进度减少20点。再接再厉！")
        
        character["cultivation"] = cultivation_data
        data["character"] = character
        
        return data
    
    def _should_trigger_cultivation_event(self, choice: Dict, character: Dict) -> bool:
        """判断是否应该触发修炼事件"""
        # 某些选择有一定概率触发修炼感悟
        choice_type = choice.get("type", "")
        if choice_type in ["exploration", "meditation", "learning"]:
            return random.random() < 0.3  # 30%概率
        return False
    
    def _trigger_random_cultivation_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """触发随机修炼事件"""
        events = [
            {"type": "insight", "gain": 15, "message": "🌟 突然领悟了修炼要诀"},
            {"type": "spiritual_encounter", "gain": 10, "message": "🍃 感受到天地灵气的流动"},
            {"type": "ancient_wisdom", "gain": 20, "message": "📜 从古籍中得到启发"}
        ]
        
        event = random.choice(events)
        return self._apply_cultivation_progress(data, event["gain"])
    
    def _generate_cultivation_choices(self, cultivation_data: Dict) -> List[Dict]:
        """生成修炼相关的选择项"""
        choices = []
        
        # 基础修炼选择
        choices.append({
            "id": "cultivation_meditate",
            "text": "静心修炼",
            "description": "专心致志地修炼，提升修炼进度",
            "effects": {"cultivation_gain": 25},
            "type": "cultivation"
        })
        
        # 根据境界提供不同的选择
        current_level = cultivation_data.get("level", 1)
        
        if current_level >= 3:
            choices.append({
                "id": "cultivation_explore",
                "text": "寻找修炼资源",
                "description": "外出寻找有助于修炼的天材地宝",
                "effects": {"cultivation_gain": 35, "risk": 0.2},
                "type": "cultivation"
            })
        
        if current_level >= 5:
            choices.append({
                "id": "cultivation_challenge",
                "text": "挑战高阶修士",
                "description": "通过战斗磨练修为",
                "effects": {"cultivation_gain": 50, "risk": 0.4},
                "requirements": {"min_cultivation_level": 5},
                "type": "cultivation"
            })
        
        return choices
    
    def _should_add_cultivation_choices(self, scene: Dict, character: Dict) -> bool:
        """判断是否应该添加修炼选择项"""
        # 在某些场景类型中添加修炼选择
        scene_type = scene.get("type", "")
        return scene_type in ["peaceful", "training", "exploration"]
    
    def _enhance_cultivation_choice(self, choice: Dict, cultivation_data: Dict) -> Dict:
        """增强修炼相关选择项"""
        # 根据当前境界调整效果
        base_gain = choice.get("effects", {}).get("cultivation_gain", 0)
        level_multiplier = 1 + (cultivation_data.get("level", 1) - 1) * 0.1
        
        enhanced_choice = choice.copy()
        enhanced_choice["effects"] = choice.get("effects", {}).copy()
        enhanced_choice["effects"]["cultivation_gain"] = int(base_gain * level_multiplier)
        
        return enhanced_choice
    
    def _validate_stages(self) -> bool:
        """验证境界数据的有效性"""
        try:
            for i, stage in enumerate(self.CULTIVATION_STAGES):
                if not all(key in stage for key in ["name", "level", "spiritual_power"]):
                    return False
                if stage["level"] != i + 1:
                    return False
            return True
        except Exception:
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "cultivation_speed_multiplier": 1.0,
            "breakthrough_base_chance": 0.5,
            "max_cultivation_level": len(self.CULTIVATION_STAGES),
            "spiritual_power_per_level": 10,
            "enable_random_events": True,
            "random_event_chance": 0.3
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证插件配置"""
        required_keys = ["cultivation_speed_multiplier", "breakthrough_base_chance"]
        
        for key in required_keys:
            if key not in config:
                return False
        
        # 验证数值范围
        if not (0.1 <= config["cultivation_speed_multiplier"] <= 5.0):
            return False
        
        if not (0.0 <= config["breakthrough_base_chance"] <= 1.0):
            return False
        
        return True
    
    def cleanup(self) -> bool:
        """清理插件资源"""
        try:
            self.logger.info(f"清理{self.name}插件")
            self.enabled = False
            return True
        except Exception as e:
            self.logger.error(f"插件清理失败: {str(e)}")
            return False
```

## 插件安全机制

### 资源限制
```python
PLUGIN_RESOURCE_LIMITS = {
    "max_memory_mb": 100,           # 最大内存使用
    "max_cpu_time_seconds": 5,      # 最大CPU时间
    "max_file_operations": 50,      # 最大文件操作次数
    "max_network_requests": 10,     # 最大网络请求次数
    "max_database_queries": 20      # 最大数据库查询次数
}
```

### 沙箱隔离
```python
class PluginSandbox:
    """插件沙箱环境"""
    
    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        self.resource_monitor = ResourceMonitor(plugin_name)
        self.permission_checker = PermissionChecker(plugin_name)
    
    def execute_plugin_method(self, method, *args, **kwargs):
        """在沙箱环境中执行插件方法"""
        with self.resource_monitor:
            # 检查权限
            if not self.permission_checker.check_method_permission(method.__name__):
                raise PermissionError(f"Plugin {self.plugin_name} lacks permission for {method.__name__}")
            
            # 执行方法
            return method(*args, **kwargs)
```

## 插件测试规范

### 插件单元测试
```python
import unittest
from plugins.basic_cultivation import BasicCultivationPlugin

class TestBasicCultivationPlugin(unittest.TestCase):
    
    def setUp(self):
        self.plugin = BasicCultivationPlugin()
        self.plugin.initialize()
    
    def test_character_creation(self):
        """测试角色创建事件处理"""
        data = {
            "character": {
                "id": 1,
                "name": "测试角色"
            }
        }
        
        result = self.plugin.handle_event("character_created", data)
        
        self.assertIn("cultivation", result["character"])
        self.assertEqual(result["character"]["cultivation"]["stage"], "炼气期一层")
    
    def test_cultivation_progress(self):
        """测试修炼进度应用"""
        data = {
            "character": {
                "cultivation": {
                    "stage": "炼气期一层",
                    "level": 1,
                    "progress": 50
                }
            },
            "choice": {
                "effects": {"cultivation_gain": 30}
            }
        }
        
        result = self.plugin.handle_event("choice_made", data)
        
        self.assertEqual(result["character"]["cultivation"]["progress"], 80)
    
    def tearDown(self):
        self.plugin.cleanup()
```

## 插件部署与管理

### 插件目录结构
```
plugins/
├── basic_cultivation/
│   ├── __init__.py
│   ├── plugin.py              # 主插件文件
│   ├── config.json            # 插件配置
│   ├── data/                  # 插件数据文件
│   │   ├── stages.json
│   │   └── techniques.json
│   ├── tests/                 # 插件测试
│   │   └── test_plugin.py
│   └── README.md              # 插件说明
└── equipment_system/
    ├── __init__.py
    ├── plugin.py
    ├── config.json
    └── ...
```

### 插件描述文件 (plugin.json)
```json
{
    "name": "basic_cultivation",
    "display_name": "基础修仙系统",
    "version": "1.0.0",
    "author": "XiuXian Games",
    "description": "提供基础的修炼境界和突破机制",
    "main_file": "plugin.py",
    "main_class": "BasicCultivationPlugin",
    "dependencies": [],
    "min_game_version": "1.0.0",
    "max_game_version": "2.0.0",
    "permissions": [
        "read_character_data",
        "modify_character_attributes",
        "generate_story_content"
    ],
    "config_schema": {
        "cultivation_speed_multiplier": {
            "type": "float",
            "default": 1.0,
            "min": 0.1,
            "max": 5.0,
            "description": "修炼速度倍数"
        }
    }
}
```

这个插件系统开发规范为AI开发团队提供了完整的插件架构指导，确保插件系统的扩展性、安全性和易用性。