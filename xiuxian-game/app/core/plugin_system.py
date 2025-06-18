# app/core/plugin_system.py
import importlib.util
import inspect
import os
from pathlib import Path
from typing import Dict, List, Any, Type, Optional

# --- Base Plugin Interface ---
class BasePlugin:
    """基础插件接口"""

    name: str = "Unknown Plugin"
    version: str = "0.0.0"
    author: str = "Unknown Author"
    description: str = "No description provided." # Added description

    def __init__(self, plugin_manager: 'PluginManager'): # Pass manager for potential access
        self.plugin_manager = plugin_manager

    def initialize(self) -> bool:
        """插件初始化. 返回True表示成功, False表示失败."""
        print(f"Initializing plugin: {self.name} v{self.version}")
        return True

    def handle_event(self, event_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理游戏事件.
        插件可以修改data字典. 如果返回None, 表示不修改data.
        如果返回一个字典, 该字典将替换原始data进行后续处理.
        """
        # Base implementation can be empty or log the event
        # print(f"Plugin {self.name} received event '{event_type}' with data: {data}")
        return None # Default is to not modify data

    def cleanup(self) -> bool:
        """插件清理. 返回True表示成功, False表示失败."""
        print(f"Cleaning up plugin: {self.name} v{self.version}")
        return True

# --- Simplified Event Types (as per MVP doc) ---
PLUGIN_EVENTS = {
    "character_created": "角色创建后触发",
    "game_started": "游戏开始时触发",
    "choice_made": "玩家做出选择后触发",
<<<<<<< HEAD
    "scene_generated": "新场景生成后触发"
=======
    "scene_generated": "新场景生成后触发",
    "game_loaded": "游戏从存档加载后触发" # ADDED
>>>>>>> origin/haa
    # Add more events as needed
}

# --- Plugin Manager ---
class PluginManager:
    """简化的插件管理器"""

    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins: Dict[str, BasePlugin] = {}
        # Assuming plugins_dir is a subdirectory of the project root where this script might eventually run
        # For now, let's make it relative to the current working directory or an absolute path if needed.
        # If this script (plugin_system.py) is in app/core/, and plugins/ is at project root,
        # we might need to adjust pathing, e.g. Path(__file__).resolve().parent.parent.parent / plugins_dir
        # For this subtask, assume 'plugins' is at the same level as where the app would be run from (e.g. project root)
        self.plugins_dir = Path(plugins_dir)
        self._loaded_plugin_modules = {} # To keep track of loaded modules

    def load_plugins(self):
        """加载所有插件"""
        if not self.plugins_dir.is_dir():
            print(f"Plugins directory '{self.plugins_dir.resolve()}' not found or not a directory.")
            return

        print(f"Scanning for plugins in '{self.plugins_dir.resolve()}'...")
        for file_path in self.plugins_dir.glob("*.py"):
            if file_path.name == "__init__.py":
                continue # Skip __init__.py files

            module_name = file_path.stem
            if module_name in self._loaded_plugin_modules:
                print(f"Module {module_name} already loaded. Skipping.")
                continue

            try:
                spec = importlib.util.spec_from_file_location(module_name, str(file_path)) # Ensure file_path is str
                if spec and spec.loader: # Check if spec and loader are not None
                    module = importlib.util.module_from_spec(spec)
                    self._loaded_plugin_modules[module_name] = module # Store module
                    spec.loader.exec_module(module) # Execute module to define classes

                    # Find plugin classes within the module
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
                            try:
                                plugin_instance = obj(plugin_manager=self) # Pass self (PluginManager)
                                if plugin_instance.name in self.plugins:
                                    print(f"Warning: Plugin with name '{plugin_instance.name}' already loaded. Skipping {obj.__name__} from {file_path.name}.")
                                    continue

                                if plugin_instance.initialize():
                                    self.plugins[plugin_instance.name] = plugin_instance
                                    print(f"Successfully loaded and initialized plugin: {plugin_instance.name} v{plugin_instance.version} from {file_path.name}")
                                else:
                                    print(f"Failed to initialize plugin: {plugin_instance.name} from {file_path.name}")
                            except Exception as e:
                                print(f"Error instantiating or initializing plugin {name} from {file_path.name}: {e}")
                else:
                    print(f"Could not create module spec for {file_path.name}. Skipping.")
            except Exception as e:
                print(f"Error loading plugin module from {file_path.name}: {e}")

        if not self.plugins:
            print("No plugins were loaded.")

    def emit_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送事件到所有已加载并初始化的插件"""
        if event_type not in PLUGIN_EVENTS:
            print(f"Warning: Emitting unknown event type '{event_type}'. Known events: {PLUGIN_EVENTS}")
            # Depending on strictness, you might choose to not proceed or proceed cautiously.
            # For now, we'll proceed.

        # Ensure 'messages' key exists in data, as per MVP example plugin
        if "messages" not in data or not isinstance(data["messages"], list):
            data["messages"] = [] # Initialize or correct if not a list

        current_data = data.copy() # Work on a copy to allow plugins to modify it sequentially

        for plugin_name, plugin in self.plugins.items():
            try:
                print(f"Emitting event '{event_type}' to plugin '{plugin_name}'")
                returned_data = plugin.handle_event(event_type, current_data)
                if returned_data is not None and isinstance(returned_data, dict):
                    current_data = returned_data # Update data for the next plugin
                # If plugin returns None, current_data remains unchanged for the next plugin
            except Exception as e:
                print(f"Error in plugin {plugin_name} during event '{event_type}': {e}")

        return current_data # Return the final data after all plugins have processed it

    def unload_plugins(self):
        """Unload all plugins and call their cleanup methods."""
        for plugin_name, plugin in list(self.plugins.items()): # Iterate over a copy for safe removal
            try:
                plugin.cleanup()
            except Exception as e:
                print(f"Error during cleanup of plugin {plugin_name}: {e}")
            del self.plugins[plugin_name]
        self._loaded_plugin_modules.clear()
        print("All plugins unloaded.")
