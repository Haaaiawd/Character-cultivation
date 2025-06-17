# app/core/rag_system.py
import os
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
            return

        doc_count = 0
        for file_path in kb_dir.glob("**/*.md"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Add file path as metadata, useful for context or debugging
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
