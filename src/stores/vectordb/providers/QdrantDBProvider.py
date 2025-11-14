from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMetricEnums
from models.db_schemes import RetrievedDocument
from qdrant_client import QdrantClient, models
from logger import logger
from typing import List

class QdrantDBProvider(VectorDBInterface):
    
    def __init__(self, db_client: str, distance_method: str):

        self.client = None
        self.db_client = db_client
        self.distance_method = None

        if distance_method == DistanceMetricEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMetricEnums.EUCLIDEAN.value:
            self.distance_method = models.Distance.EUCLID
        elif distance_method == DistanceMetricEnums.DOT_PRODUCT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logger

    async def connect(self):
        self.client = QdrantClient(path=self.db_client)

    async def disconnect(self):
        self.client = None

    async def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    async def list_all_collections(self):
        return self.client.get_collections()

    async def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    async def delete_collection(self, collection_name: str) -> bool:
        if await self.is_collection_exists(collection_name):
            self.client.delete_collection(collection_name=collection_name)
            return True
        return False

    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):

        if do_reset:
            _ = await self.delete_collection(collection_name)

        if not await self.is_collection_exists(collection_name):
            self.logger.info(f"Creating new Qdrant collection: {collection_name}")

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )

            return True

        return False

    async def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict = None, id: str = None):

        if not await self.is_collection_exists(collection_name):
            logger.error(f"Collection {collection_name} does not exist.")
            return False

        point = models.PointStruct(
            id=id,
            vector=vector,
            payload={
                "text": text,
                "metadata": metadata
            }
        )

        self.client.upsert(
            collection_name=collection_name,
            points=[point]
        )

        return True

    async def insert_many(self, collection_name: str, texts: list, vectors: list, metadatas: list = None, ids: list = None, batch_size: int = 50):

        if not await self.is_collection_exists(collection_name):
            logger.error(f"Collection {collection_name} does not exist.")
            return False

        for start_idx in range(0, len(texts), batch_size):

            batch_text = texts[start_idx: start_idx + batch_size]
            batch_vectors = vectors[start_idx: start_idx + batch_size]
            batch_metadatas = metadatas[start_idx: start_idx + batch_size]
            batch_ids = ids[start_idx: start_idx + batch_size]

            batch_points = [
                models.PointStruct(
                    id=batch_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_text[x],
                        "metadata": batch_metadatas[x]
                    }
                )
                for x in range(len(batch_text))
            ]

            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch_points
                )

            except Exception as e:
                logger.error(f"Error while inserting batch: {e}")
                return False

        return True
    
    async def search_by_vector(self, collection_name: str, query_vector: List, limit: int):

        results = self.client.search(
            collection_name = collection_name,
            query_vector = query_vector, # <--- Dense vector
            limit = limit
            )
        

        results = [
            RetrievedDocument(**{
                "score": res.score,
                "text": res.payload["text"]
            })
            for res in results
        ]
        
        return results


