# app/core/rag_system.py
import os
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
            return

        doc_count = 0
        for file_path in kb_dir.glob("**/*.md"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
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
