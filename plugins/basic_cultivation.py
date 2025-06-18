# plugins/basic_cultivation.py
from typing import Dict, Any, Optional

from app.core.plugin_system import BasePlugin # Assuming BasePlugin is in app.core.plugin_system

class BasicCultivationPlugin(BasePlugin):
    """基础修仙插件"""

    name = "BasicCultivation"
    version = "0.1.0"
    author = "XiuXian Games MVP"
    description = "A basic plugin to manage cultivation stages and progression."

    # 修仙境界定义 (Cultivation Stages Definition)
    CULTIVATION_STAGES = [
        "炼气期一层", "炼气期二层", "炼气期三层",
        "炼气期四层", "炼气期五层", "炼气期六层",
        "炼气期七层", "炼气期八层", "炼气期九层", # Qi Refining Stage 1-9
        "筑基期初期", "筑基期中期", "筑基期后期"  # Foundation Establishment Stage (Early, Mid, Late)
    ]

    # Max progress for each stage before breakthrough (example)
    STAGE_MAX_PROGRESS = 100

    def initialize(self) -> bool:
        # Perform any setup for this plugin, e.g., load data files specific to this plugin
        # Call parent initialize first
        super_initialized = super().initialize()
        if not super_initialized:
            return False # Stop if parent initialization failed
<<<<<<< HEAD
        print(f"Plugin {self.name} initialized by example plugin. Ready to manage cultivation.")
=======
        logging.info(f"Plugin {self.name} initialized by example plugin. Ready to manage cultivation.")
>>>>>>> origin/haa
        # Example: self.load_cultivation_data()
        return True

    def handle_event(self, event_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handles game events related to cultivation."""
        # Call parent's handle_event first, though it does nothing by default, it's good practice
        super().handle_event(event_type, data)

        character_data = data.get("character") # Get character data if available

        # Ensure messages list exists in data, even if character_data is not processed further
        if "messages" not in data or not isinstance(data.get("messages"), list):
            data["messages"] = []

        if not character_data or not isinstance(character_data, dict):
            if event_type in ["character_created", "choice_made"]: # Only print warning for relevant events
                 print(f"{self.name} plugin: Character data not found or invalid for event '{event_type}'. Plugin will not act.")
            return None # No changes if no character data for this plugin to act upon

        if event_type == "character_created":
            # Initialize character cultivation attributes
            if "cultivation" not in character_data or not isinstance(character_data.get("cultivation"), dict) :
                character_data["cultivation"] = {}

            character_data["cultivation"]["stage"] = self.CULTIVATION_STAGES[0]
            character_data["cultivation"]["progress"] = 0
            character_data["cultivation"]["spiritual_power"] = 50 # Example starting spiritual power
            print(f"{self.name}: Initialized cultivation for character {character_data.get('name', 'Unknown')}.")
            data["messages"].append(f"你感受到了体内的气感，踏入了{self.CULTIVATION_STAGES[0]}。")


        elif event_type == "choice_made":
            choice_data = data.get("choice") # Get choice data
            if not choice_data or not isinstance(choice_data, dict):
                print(f"{self.name} plugin: Choice data not found or invalid for event '{event_type}'.")
                return data # Return original data if no choice data to process

            # Ensure 'cultivation' key exists and is a dict in character_data
            if "cultivation" not in character_data or not isinstance(character_data.get("cultivation"), dict) :
                print(f"{self.name}: Cultivation data missing or invalid for character {character_data.get('name', 'Unknown')} during 'choice_made'.")
                return data # Return original data if no cultivation data to process

            effects = choice_data.get("effects", {})
            if "cultivation_gain" in effects:
                gain = effects["cultivation_gain"]
                if not isinstance(gain, (int, float)):
                    print(f"{self.name}: Invalid cultivation_gain value '{gain}'. Must be a number.")
                    return data # Return original data if gain is invalid

                cult_data = character_data["cultivation"]
                current_stage_name = cult_data.get("stage", self.CULTIVATION_STAGES[0])
                try:
                    current_stage_index = self.CULTIVATION_STAGES.index(current_stage_name)
                except ValueError:
                    print(f"{self.name}: Unknown cultivation stage '{current_stage_name}' for character. Resetting to first stage.")
                    current_stage_index = 0
                    cult_data["stage"] = self.CULTIVATION_STAGES[0]


                cult_data["progress"] = cult_data.get("progress", 0) + gain
                print(f"{self.name}: Character {character_data.get('name', 'Unknown')} gained {gain} cultivation progress.")
                data["messages"].append(f"你感觉到修为精进了一丝，当前进度：{cult_data['progress']}/{self.STAGE_MAX_PROGRESS}。")

                if cult_data["progress"] >= self.STAGE_MAX_PROGRESS:
                    if current_stage_index < len(self.CULTIVATION_STAGES) - 1:
                        new_stage_index = current_stage_index + 1
                        cult_data["stage"] = self.CULTIVATION_STAGES[new_stage_index]
                        cult_data["progress"] -= self.STAGE_MAX_PROGRESS
                        if cult_data["progress"] < 0: cult_data["progress"] = 0 # Ensure progress isn't negative

                        breakthrough_message = f"恭喜！你成功突破到了 {cult_data['stage']}！"
                        print(f"{self.name}: {breakthrough_message}")
                        data["messages"].append(breakthrough_message)
                        cult_data["spiritual_power"] = cult_data.get("spiritual_power", 50) + 50
                    else:
                        cult_data["progress"] = self.STAGE_MAX_PROGRESS
                        data["messages"].append("你感觉修为已至当前境界顶峰，寻求新的机缘以图突破吧！")

        return data

    def cleanup(self) -> bool:
        super_cleaned = super().cleanup()
        if not super_cleaned:
            return False
        print(f"Plugin {self.name} specific cleanup done.")
        return True
