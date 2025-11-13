from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMetricEnums, PgVectorTableSchemeEnums, PgVectorDistanceMethodEnums, PgVectorIndexTypeEnums
from models.db_schemes import RetrievedDocument
from typing import List
import logging
from sqlalchemy.sql import text as sql_text
import json


class PGVectorProvider(VectorDBInterface):

    def __init__(self, db_client, default_vector_size: int = 768,
                 distance_method: str = None, index_threshold: int = 100):

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
                query = sql_text(
                    "SELECT 1 FROM pg_extension WHERE extname = 'vector'")
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
                query = sql_text(
                    "SELECT * FROM pg_tables WHERE tablename = :collection_name")
                results = await session.execute(query, {"collection_name": collection_name})
                record = results.scalar_one_or_none()
        return record

    async def list_all_collections(self) -> List:
        records = []
        async with self.db_client() as session:
            async with session.begin():
                query = sql_text(
                    "SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix")
                results = await session.execute(query, {"prefix": self.pgvector_table_prefix})
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
            _ = self.delete_collection(collection_name=collection_name)

        is_collection_existed = await self.is_collection_exists(collection_name=collection_name)

        if not is_collection_existed:
            self.logger.info(f"Creating collection: {collection_name}")

            async with self.db_client() as session:
                async with session.begin():
                    create_collection = sql_text(
                        f'CREATE TABLE {collection_name}('
                        f'{PgVectorTableSchemeEnums.ID.value} bigserial PRIMARY KEY, '
                        f'{PgVectorTableSchemeEnums.TEXT.value} text, '
                        f'{PgVectorTableSchemeEnums.VECTOR.value} vector({embedding_size}), '
                        f'{PgVectorTableSchemeEnums.METADATA.value} jsonb DEFAULT \'{{}}\', '
                        f'{PgVectorTableSchemeEnums.CHUNK_ID.value} integer, '
                        f'FOREIGN KEY ({PgVectorTableSchemeEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id)'
                        ')'
                    )
                    await session.execute(create_collection)
                    await session.commit()

            return True

        return False

    async def is_index_existed(self, collection_name: str) -> bool:
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                check_sql = sql_text(f"""
                                     SELECT 1 
                                     FROM pg_indexes
                                     WHERE table_name = :collection_name
                                     AND indexname = :index_name
                                     """)
                result = await session.execute(check_sql, {"collection_name": collection_name, "index_name": index_name})
                return bool(result.scalar_one_or_none())

    async def create_vector_index(self, collection_name: str,
                                  index_type: str = PgVectorIndexTypeEnums.HNSW.value):

        is_index_existed = await self.is_index_existed(collection_name)

        if not is_index_existed:
            async with self.db_client() as session:
                async with session.begin():
                    count_sql = sql_text(
                        f'SELECT COUNT(*) FROM {collection_name}')
                    result = await session.execute(count_sql)
                    records_count = result.scalar_one()

                    if records_count < self.index_threshold:
                        return False

                    self.logger.info(
                        f"START: Creating vector index for collection: {collection_name}")

                    index_name = self.default_index_name(collection_name)
                    create_idx_sql = sql_text(
                        f'CREATE INDEX {index_name} on {collection_name}'
                        f'USING {index_type} ({PgVectorTableSchemeEnums.VECTOR.value} {self.distance_method})'
                    )
                    await session.execute(create_idx_sql)
                    self.logger.info(
                        f"END: Created vector index for collection: {collection_name}")
                    return True
        return False

    async def reset_vector_index(self, collection_name: str,
                                 index_type: str = PgVectorIndexTypeEnums.HNSW.value) -> bool:

        index_name = self.default_index_name(collection_name)

        async with self.db_client() as session:
            async with session.begin():
                drop_sql = sql_text(f'DROP INDEX IF EXISTS {index_name}')
                await session.execute(drop_sql)

        create_index = await self.create_vector_index(collection_name, index_type)
        return create_index

    async def insert_one(self, collection_name: str, text: str, vector: List, metadata: dict = None, id: str = None):

        is_collection_existed = await self.is_collection_exists(collection_name=collection_name)

        if not is_collection_existed:
            self.logger.error(
                f"Can not insert new record to non-existed collection: {collection_name}")
            return False

        if not id:
            self.logger.error(
                f"Can not insert new record without chunk_id: {collection_name}")

        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(
                    f'INSERT INTO {collection_name} '
                    f'({PgVectorTableSchemeEnums.TEXT.value}, {PgVectorTableSchemeEnums.VECTOR.value}, {PgVectorTableSchemeEnums.METADATA.value}, {PgVectorTableSchemeEnums.CHUNK_ID.value}) '
                    f'VALUES (:text, :vector, :metadata, :chunk_id)'
                )
                metadata_json = json.dumps(
                    metadata, ensure_ascii=False) if metadata else "{}"
                await session.execute(
                    insert_sql, {
                        'text': text,
                        'vector': "[" + ",".join([str(v) for v in vector]) + "]",
                        'metadata': metadata_json,
                        'chunk_id': id
                    }
                )
                await session.commit()

        _ = await self.create_vector_index(collection_name)

        return True

    async def insert_many(self, collection_name: str, texts: List[str], vectors: List[List], metadatas: List[dict] = None, ids: List[str] = None, batch_size: int = 50):

        is_collection_existed = await self.is_collection_exists(collection_name=collection_name)

        if not is_collection_existed:
            self.logger.error(
                f"Can not insert new record to non-existed collection: {collection_name}")
            return False

        if len(vectors) != len(ids):
            self.logger.error(
                f"Invalid data items for collection: {collection_name}")
            return False

        if not metadatas or len(metadatas) == 0:
            metadatas = [None] * len(texts)

        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(texts), batch_size):

                    batch_texts = texts[i:i+batch_size]
                    batch_vectors = vectors[i:i+batch_size]
                    batch_metadatas = metadatas[i:i+batch_size]
                    batch_ids = ids[i:i+batch_size]

                    values = []

                    for _text, _vector, _metadata, _id in zip(batch_texts, batch_vectors, batch_metadatas, batch_ids):

                        metadata_json = json.dumps(
                            _metadata, ensure_ascii=False) if _metadata else "{}"

                        values.append(
                            {
                                'text': _text,
                                'vector': "[" + ",".join([str(v) for v in _vector]) + "]",
                                'metadata': metadata_json,
                                'chunk_id': _id
                            }
                        )

                    batch_insert_sql = sql_text(
                        f'INSERT INTO {collection_name}'
                        f'({PgVectorTableSchemeEnums.TEXT.value}, '
                        f'{PgVectorTableSchemeEnums.VECTOR.value}, '
                        f'{PgVectorTableSchemeEnums.METADATA.value}, '
                        f'{PgVectorTableSchemeEnums.CHUNK_ID.value}) '
                        f'VALUES (:text, :vector, :metadata, :chunk_id)'
                    )

                    await session.execute(batch_insert_sql, values)

        _ = await self.create_vector_index(collection_name)

        return True

    async def search_by_vector(self, collection_name: str, query_vector: List, limit: int) -> List[RetrievedDocument]:

        is_collection_existed = await self.is_collection_exists(collection_name=collection_name)

        if not is_collection_existed:
            self.logger.error(
                f"Can not insert new record to non-existed collection: {collection_name}")
            return False

        vector = "[" + ",".join([str(v) for v in query_vector]) + "]"

        async with self.db_client() as session:
            async with session.begin():
                search_sql = sql_text(
                    f'SELECT {PgVectorTableSchemeEnums.TEXT.value} as text,  1 - ({PgVectorTableSchemeEnums.VECTOR.value} <=> :vector) as score'
                    f' FROM {collection_name}'
                    f' ORDER BY score DEC'
                    f' LIMIT {limit}'
                )
                result = await session.execute(search_sql, {"vector": vector})
                records = result.fetchall()

                return [
                    RetrievedDocument(**{
                        "text": record.text,
                        "score": record.score
                    })
                    for record in records
                ]
