# app/core/rag_system.py
import os
<<<<<<< HEAD
import re # Import re for parsing
from pathlib import Path
from typing import Dict, Any, List, Optional # Added Optional

from langchain.llms.openai import OpenAI # Corrected import for OpenAI LLM
from langchain.embeddings.openai import OpenAIEmbeddings # Corrected import
from langchain.vectorstores.faiss import FAISS
# from langchain.chains import RetrievalQA # Not used in the MVP snippet, direct retrieval and formatting
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document # For creating documents for FAISS

from app.core.config import settings
from app.schemas.game_schemas import StoryScene, StoryChoice # For return type

class RAGSystem:
    """简化的RAG系统"""

    def __init__(self):
        self.knowledge_base: Optional[FAISS] = None # Type hint for clarity
        # Ensure API key is available
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables.")

        self.llm = OpenAI(temperature=0.7, openai_api_key=settings.OPENAI_API_KEY)
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.load_knowledge_base()

    def load_knowledge_base(self):
        """加载知识库"""
        kb_dir = Path("knowledge_base") # Assuming this is relative to project root
        documents_for_faiss: List[Document] = [] # Use Langchain Document objects

        if not kb_dir.exists() or not kb_dir.is_dir():
            print(f"Knowledge base directory {kb_dir.resolve()} not found or is not a directory.")
            # In a real app, might raise an error or handle this more gracefully
            self.knowledge_base = None # Ensure it's None if loading fails
=======
import re # Keep re for any potential fallback or minor string cleaning if needed
import json # ADDED for JSON parsing
from pathlib import Path
from typing import Dict, Any, List, Optional # Ensure Optional is imported

# Langchain imports - ensure these are compatible with current langchain version
# For OpenAI, it's likely from langchain_openai now
# from langchain.llms.openai import OpenAI # Old import
# from langchain.embeddings.openai import OpenAIEmbeddings # Old import
# Try new imports if available and adjust instantiation if needed.
# For this subtask, assume the existing OpenAI/OpenAIEmbeddings imports are working
# as per previous setup, or the subtask runner will handle version compatibility.
# If using newer langchain:
from langchain_openai import OpenAI, OpenAIEmbeddings

from langchain.vectorstores.faiss import FAISS
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document

from app.core.config import settings
# Assuming StoryScene and StoryChoice schemas are updated as per Plan Step 1 (new plan)
from app.schemas.game_schemas import StoryScene, StoryChoice

class RAGSystem:
    """简化的RAG系统 - Modified for JSON output"""

    def __init__(self):
        self.knowledge_base: Optional[FAISS] = None
        if not settings.OPENAI_API_KEY:
            # In a real app, this might be a fatal error preventing startup.
            print("CRITICAL: OPENAI_API_KEY not set. RAGSystem will not function.")
            self.llm = None # Ensure LLM is None if key is missing
            self.embeddings = None
            # Attempt to load KB even without LLM, it might be useful for other things or if key is set later.
            # self.load_knowledge_base() # Or skip if embeddings also fail.
            return

        try:
            self.llm = OpenAI(temperature=0.7, openai_api_key=settings.OPENAI_API_KEY)
            self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        except Exception as e:
            print(f"CRITICAL: Failed to initialize OpenAI components: {e}. RAGSystem may not function.")
            self.llm = None
            self.embeddings = None
            return

        self.load_knowledge_base() # Load KB after LLM/Embeddings are potentially initialized

    def load_knowledge_base(self):
        """加载知识库 (Unchanged from previous version, but ensure embeddings are available)"""
        if not self.embeddings:
            print("Knowledge base loading skipped: OpenAIEmbeddings not initialized.")
            self.knowledge_base = None
            return

        kb_dir = Path("knowledge_base")
        documents_for_faiss: List[Document] = []

        if not kb_dir.exists() or not kb_dir.is_dir():
            print(f"Knowledge base directory {kb_dir.resolve()} not found or is not a directory.")
            self.knowledge_base = None
>>>>>>> origin/haa
            return

        doc_count = 0
        for file_path in kb_dir.glob("**/*.md"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
<<<<<<< HEAD
                    # Add file path as metadata, useful for context or debugging
=======
>>>>>>> origin/haa
                    metadata = {"source": str(file_path.relative_to(kb_dir))}
                    documents_for_faiss.append(Document(page_content=content, metadata=metadata))
                    doc_count +=1
            except Exception as e:
                print(f"Error reading or processing file {file_path}: {e}")

        if documents_for_faiss:
            try:
                self.knowledge_base = FAISS.from_documents(documents_for_faiss, self.embeddings)
                print(f"Knowledge base loaded successfully with {doc_count} documents.")
            except Exception as e:
                print(f"Error creating FAISS index: {e}")
                self.knowledge_base = None
        else:
            print("No documents found to load into knowledge base.")
            self.knowledge_base = None

<<<<<<< HEAD
    def generate_story(self, game_state: Dict[str, Any], character: Dict[str, Any]) -> StoryScene:
        """生成剧情内容"""
        if self.knowledge_base is None:
            # Fallback if KB didn't load
            return StoryScene(
                description="The world feels hazy and indistinct, as if waiting to be fully imagined. (Knowledge Base Error)",
                choices=[
                    StoryChoice(id="choice_1", text="Try to focus..."),
                    StoryChoice(id="choice_2", text="Wait for clarity..."),
                    StoryChoice(id="choice_3", text="Ponder the void..."),
                ]
            )

        # Ensure required fields are present in inputs
        char_name = character.get("name", "Unnamed Hero")
        char_stage = character.get("cultivation_stage", "Mortal") # Use .get for safety
        current_scene_info = game_state.get("current_scene_id", "an unknown place") # Use .get for safety

        # 构建查询上下文
        query = f"Character: {char_name}, Stage: {char_stage}, Current Scene: {current_scene_info}"

        # 检索相关信息
        # FAISS.similarity_search returns List[Document]
        relevant_docs_list: List[Document] = self.knowledge_base.similarity_search(query, k=3)
        context = "\n".join([doc.page_content for doc in relevant_docs_list])

        # 构建提示
        prompt_template_str = """
You are a text-based cultivation game's AI storyteller. Based on the following information, generate an engaging story description and provide 3 choices.

Character Information: {character_info}

Game History (last 3 events): {history}

Relevant Background Knowledge: {context}

Please generate a story description (100-200 words) and three choices (each 20-30 words).
Format the output EXACTLY like this:
Story: [Your generated story description here]
Choice 1: [Your first choice text here]
Choice 2: [Your second choice text here]
Choice 3: [Your third choice text here]
"""
        prompt = PromptTemplate(
            template=prompt_template_str,
            input_variables=["character_info", "history", "context"]
        )

        # 生成内容
        story_history_list = game_state.get("story_history", [])
        story_history_str = str(story_history_list[-3:]) if story_history_list else "Game start"


        inputs = {
            "character_info": str(character), # Convert whole character dict to string
            "history": story_history_str,
            "context": context
        }

        raw_llm_output = self.llm(prompt.format(**inputs))

        # 解析结果
        story_text = "Error: Could not parse story."
        choice_texts = ["Retry", "Explore", "Rest"] # Default choices on parsing error

        try:
            story_match = re.search(r"Story:(.*?)Choice 1:", raw_llm_output, re.DOTALL | re.IGNORECASE)
            if story_match:
                story_text = story_match.group(1).strip()

            parsed_choices = []
            for i in range(1, 4):
                choice_match = re.search(rf"Choice {i}:(.*?)(Choice {i+1}:|\Z)", raw_llm_output, re.DOTALL | re.IGNORECASE)
                if choice_match:
                    parsed_choices.append(choice_match.group(1).strip())
                else:
                    # If a specific choice isn't found with the new format, stop trying to parse this way
                    # and let the fallback logic handle it.
                    break

            if len(parsed_choices) == 3:
                 choice_texts = parsed_choices
            elif not story_match and not parsed_choices: # If nothing matches with new format, try old split
                parts = raw_llm_output.split("选择")
                parsed_story_text = parts[0].strip().replace("剧情：", "").strip()
                if parsed_story_text : story_text = parsed_story_text # Update story if old parsing finds something

                temp_choices = []
                for i in range(1, min(4, len(parts))): # Iterate up to 3 choices
                    choice_part = parts[i].strip()
                    # Extract text after colon (Chinese or English)
                    if "：" in choice_part:
                        choice_part_text = choice_part.split("：", 1)[1].strip()
                    elif ":" in choice_part:
                        choice_part_text = choice_part.split(":", 1)[1].strip()
                    else: # If no colon, take the whole part (might be just text)
                        choice_part_text = choice_part
                    if choice_part_text: temp_choices.append(choice_part_text)

                if len(temp_choices) >= 1: # Use if old parsing finds at least one choice
                    choice_texts = temp_choices[:3]
                    # Fill remaining choices if less than 3 found by old parsing
                    while len(choice_texts) < 3:
                        choice_texts.append(f"Fallback Action {len(choice_texts) + 1}")


        except Exception as e:
            print(f"Error parsing LLM output: {e}\nOutput was: {raw_llm_output}")
            # story_text and choice_texts will use their default error values set before try block

        final_choices = []
        for i, text in enumerate(choice_texts[:3]): # Ensure max 3 choices
            final_choices.append(StoryChoice(id=f"choice_{i+1}", text=text))

        # This loop is to ensure exactly 3 choices if parsing yielded fewer than 3.
        # The parsing logic itself now tries to provide 3 fallbacks if direct parsing fails.
        while len(final_choices) < 3:
            final_choices.append(StoryChoice(id=f"choice_{len(final_choices)+1}", text=f"Consider option {len(final_choices)+1}"))

        return StoryScene(
            description=story_text,
            choices=final_choices
        )
=======
    def _get_default_error_scene(self, error_message: str = "Error generating story.") -> StoryScene:
        """Provides a fallback StoryScene in case of errors."""
        return StoryScene(
            scene_id="error_scene",
            plot=f"{error_message} The path ahead is unclear, but you must choose a way forward.",
            choices=[
                StoryChoice(id="choice_1", text="Try to re-evaluate the situation."),
                StoryChoice(id="choice_2", text="Push forward cautiously."),
                StoryChoice(id="choice_3", text="Seek guidance or rest."),
            ],
            duration_days=1 # Default duration for an error/fallback scene
        )

    def generate_story(self, game_state: Dict[str, Any], character: Dict[str, Any]) -> StoryScene:
        """生成剧情内容 as JSON"""
        if self.llm is None:
            print("LLM not initialized. Returning default error scene.")
            return self._get_default_error_scene("LLM (AI Storyteller) is currently unavailable.")

        if self.knowledge_base is None:
            print("Knowledge base not loaded. Using very limited context for story generation.")
            context = "No specific background knowledge available for this scene."
        else:
            char_name = character.get("name", "The Wanderer")
            char_stage = character.get("cultivation_stage", "an early stage")
            current_scene_desc = game_state.get("current_scene_id", "an unknown location")
            query = f"Character: {char_name}, Cultivation Stage: {char_stage}, Current Location/Situation: {current_scene_desc}"
            try:
                relevant_docs_list: List[Document] = self.knowledge_base.similarity_search(query, k=2) # k=2 for brevity
                context = "\n".join([doc.page_content for doc in relevant_docs_list])
                if not context.strip(): # Ensure context is not empty
                    context = "General knowledge about the world applies here."
            except Exception as e:
                print(f"Error during similarity search: {e}. Using generic context.")
                context = "The winds of fate are swirling, obscuring detailed knowledge."


        # NEW Prompt Engineering for JSON output
        prompt_template_str = """
You are an AI storyteller for a text-based cultivation (Xianxia) game.
Your task is to generate the next part of the story based on the provided information.
The user is playing as: {character_info}
Current in-game date: {current_date}
Recent game history (last 1-2 events): {history}
Relevant background knowledge from the game world:
{context}

Please generate the output as a single, valid JSON object. Do NOT write any text outside this JSON object.
The JSON object must have the following structure:
{{
  "plot": "A short, engaging plot description for the current scene. This should be 2-3 sentences long.",
  "choices": [
    {{"id": "choice_1", "text": "A brief text for the first choice (10-15 words max)."}},
    {{"id": "choice_2", "text": "A brief text for the second choice (10-15 words max)."}},
    {{"id": "choice_3", "text": "A brief text for the third choice (10-15 words max)."}}
  ],
  "duration_days": <an integer between 1 and 7, representing the number of in-game days this plot segment will take>
}}

Ensure the plot is concise and leads to the choices. The choices should be distinct actions the player can take.
Example for "plot": "You arrive at the Whispering Glade, sunlight filtering through ancient trees. A faint spiritual energy emanates from a moss-covered shrine in the center."
Example for "duration_days": 3

Current JSON output:
"""

        prompt = PromptTemplate(
            template=prompt_template_str,
            input_variables=["character_info", "current_date", "history", "context"]
        )

        story_history_for_prompt = str(game_state.get("story_history", [])[-2:]) if game_state.get("story_history") else "This is the beginning of your journey."
        current_date_for_prompt = game_state.get("current_date", "An unknown day")

        inputs = {
            "character_info": json.dumps(character),
            "current_date": current_date_for_prompt,
            "history": story_history_for_prompt,
            "context": context
        }

        try:
            raw_llm_output = self.llm(prompt.format(**inputs))
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return self._get_default_error_scene("There was an issue with the AI Storyteller.")

        # NEW JSON Parsing Logic
        try:
            match = re.search(r"```json\s*([\s\S]*?)\s*```", raw_llm_output)
            if match:
                json_str = match.group(1)
            else:
                json_start_index = raw_llm_output.find('{')
                json_end_index = raw_llm_output.rfind('}')
                if json_start_index != -1 and json_end_index != -1 and json_end_index > json_start_index:
                    json_str = raw_llm_output[json_start_index : json_end_index+1]
                else:
                    json_str = raw_llm_output

            parsed_output = json.loads(json_str)

            if not all(k in parsed_output for k in ["plot", "choices", "duration_days"]):
                raise ValueError("Missing one or more required keys in JSON output (plot, choices, duration_days).")
            if not isinstance(parsed_output["choices"], list) or len(parsed_output["choices"]) != 3:
                raise ValueError("JSON 'choices' must be a list of 3 items.")
            for choice in parsed_output["choices"]:
                if not all(k in choice for k in ["id", "text"]):
                    raise ValueError("Each choice object must have 'id' and 'text' keys.")

            duration = parsed_output.get("duration_days", 1) # Default to 1 if missing
            if not isinstance(duration, int) : # Check if it's not an int (e.g. float, string)
                 try: duration = int(duration) # Try to cast
                 except ValueError: duration = 1 # Fallback if cast fails
            parsed_output["duration_days"] = min(max(1, duration), 7)


            story_choices = [StoryChoice(id=str(c.get("id","choice_fallback")), text=str(c.get("text", "---"))) for c in parsed_output["choices"]]

            return StoryScene(
                plot=str(parsed_output["plot"]),
                choices=story_choices,
                duration_days=int(parsed_output["duration_days"])
            )

        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON from LLM output: {e}")
            print(f"LLM Raw Output was:\n{raw_llm_output}")
            return self._get_default_error_scene("The story's path became muddled (AI response format error).")
        except ValueError as e:
            print(f"Invalid JSON structure from LLM: {e}")
            print(f"LLM Raw Output was:\n{raw_llm_output}")
            return self._get_default_error_scene("The story's details were unclear (AI response structure error).")
        except Exception as e:
            print(f"An unexpected error occurred while processing LLM response: {e}")
            print(f"LLM Raw Output was:\n{raw_llm_output}")
            return self._get_default_error_scene("An unforeseen twist in the tale (unexpected AI response error).")
>>>>>>> origin/haa
