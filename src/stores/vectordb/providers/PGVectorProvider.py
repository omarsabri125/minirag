from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMetricEnums, PgVectorTableSchemeEnums, PgVectorDistanceMethodEnums, PgVectorIndexTypeEnums
from models.db_schemes import RetrievedDocument
from typing import List
import logging
from sqlalchemy.sql import text as sql_text
import json

class PGVectorProvider(VectorDBInterface):

    def __init__(self, db_client, default_vector_size: int = 768, 
                        distance_method: str = None, index_threshold: int=100):
        
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.index_threshold = index_threshold
        self.distance_method = None

        if distance_method == DistanceMetricEnums.COSINE.value:
            self.distance_method = PgVectorDistanceMethodEnums.COSINE.value
        elif distance_method == DistanceMetricEnums.DOT_PRODUCT.value:
            self.distance_method = PgVectorDistanceMethodEnums.DOT.value
        
        self.pgvector_table_prefix = PgVectorTableSchemeEnums._PREFIX.value

        self.logger = logging.getLogger("uvicorn")
        self.default_index_name = lambda collection_name: f"{collection_name}_vector_idx"
    
    async def connect(self):
        async with self.db_client() as session:
            try:
                query = sql_text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                result = await session.execute(query)
                extension_exists = result.scalar_one_or_none()

                if not extension_exists:
                    await session.execute(sql_text("CREATE EXTENSION vector"))
                    await session.commit()

            except Exception as e:
                self.logger.warning(f"Vector extension setup: {str(e)}")
                await session.rollback()
    
    async def disconnect(self):
        pass

    async def is_collection_exists(self, collection_name: str) -> bool:
        record = None
        async with self.db_client() as session: 
            async with session.begin():
                query = sql_text("SELECT * FROM pg_tables WHERE tablename = :collection_name")
                results = await session.execute(query,{"collection_name": collection_name})
                record = results.scalar_one_or_none()
        return record
    
    async def list_all_collections(self) -> List:
        records = []
        async with self.db_client() as session: 
            async with session.begin():
                query = sql_text("SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix")
                results = await session.execute(query,{"prefix": self.pgvector_table_prefix})
                records = results.scalars().all()
        return records
    
    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.db_client() as session: 
            async with session.begin():

                table_info_sql = sql_text(f'''
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes 
                    FROM pg_tables 
                    WHERE tablename = :collection_name
                ''')

                count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')

                
                table_info = await session.execute(table_info_sql, {"collection_name": collection_name})
                record_count = await session.execute(count_sql)

                table_data = table_info.fetchone()

                if not table_data:
                    return None
                
                return {
                    "table_info": {
                        "schemaname": table_data[0],
                        "tablename": table_data[1],
                        "tableowner": table_data[2],
                        "tablespace": table_data[3],
                        "hasindexes": table_data[4],
                    },
                    "record_count": record_count.scalar_one(),
                }
    
    async def delete_collection(self, collection_name: str) -> bool:
        async with self.db_client() as session: 
            async with session.begin():
                self.logger.info(f"Deleting collection: {collection_name}")

                query = sql_text(f"DROP TABLE IF EXISTS {collection_name}")
                await session.execute(query)
                await session.commit()

        return True
    
    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        
        if do_reset:
            _ = self.delete_collection(collection_name = collection_name)

        