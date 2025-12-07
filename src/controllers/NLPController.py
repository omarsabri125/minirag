from .BaseController import BaseController
from stores.llm.LLMEnums import DocumentTypeEnum
from models.db_schemes import Project, DataChunk
from routes.schemes.QueryExpand import SemanticExpansion
from typing import List
import json

class NLPController(BaseController):

    def __init__(self, vector_db_client, embedding_client, generation_client, template_parser):
        super().__init__()
        self.vector_db_client = vector_db_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()

    async def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(
            project_id=project.project_id)
        return await self.vector_db_client.delete_collection(collection_name=collection_name)

    async def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(
            project_id=project.project_id)
        collection_info = await self.vector_db_client.get_collection_info(
            collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )

    async def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                             chunks_ids: List[int],
                             do_reset: bool = False):

        collection_name = self.create_collection_name(
            project_id=project.project_id)

        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]
        vectors = self.embedding_client.embed_text(
            texts, DocumentTypeEnum.DOCUMENT.value)

        _ = await self.vector_db_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset)

        _ = await self.vector_db_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadatas=metadata,
            ids=chunks_ids
        )

        return True
    
    async def query_expansion(self, query:str):

        system_prompt = self.template_parser.get("rag", "query_expand_system_prompt")
        user_prompt = self.template_parser.get("rag", "query_expand_user_prompt", {
            "query": query
        })

        chat_history = [
            self.generation_client.construt_prompt(
                prompt = system_prompt,
                role = self.generation_client.enums.SYSTEM.value
            )
        ]

        answer = self.generation_client.generate_text(
            prompt = user_prompt,
            chat_history = chat_history
        )

        if not answer:
            return False

        return SemanticExpansion(
            original_query = query,
            expanded_query = answer
        )

    async def search_vector_db_collection(self, project: Project, text: str, limit: int = 5):

        collection_name = self.create_collection_name(
            project_id=project.project_id)
        
        query_optimization = await self.query_expansion(
            query= text
        )

        if not query_optimization or not query_optimization.expanded_query:
            return False

        vectors = self.embedding_client.embed_text(
            query_optimization.expanded_query, DocumentTypeEnum.QUERY.value)

        if not vectors or len(vectors) == 0:
            return False

        if isinstance(vectors, list) and len(vectors) > 0:
            query_vector = vectors[0]

        if not query_vector:
            return False

        result = await self.vector_db_client.search_by_vector(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )

        if not result:
            return False

        return result    

    async def rag_answer_question(self, project: Project, query: str, limit: int = 5):

        answer, full_prompt, chat_history = None, None, None

        retrieved_documents = await self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history

        system_prompt = self.template_parser.get("rag", "system_prompt")

        documents_prompt = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_num": idx+1,
                "chunk_text": doc.text
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt", {
            "query": query
        })

        full_prompt = "\n\n".join([documents_prompt, footer_prompt])

        chat_history = [
            self.generation_client.construt_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value
            )
        ]

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history
