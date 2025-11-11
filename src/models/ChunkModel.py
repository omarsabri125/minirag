from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from sqlalchemy.future import select
from sqlalchemy import func, delete
from typing import List

class ChunkModel(BaseDataModel):

    def __init__(self, db_client):
        super().__init__(db_client)

    async def create_chunk(self, chunk: DataChunk):
        async with self.db_client() as session: 
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        return chunk
    
    async def get_chunk(self, chunk_id: str):
        async with self.db_client() as session: 
            async with session.begin():
                query = select(DataChunk).where(DataChunk.chunk_id == chunk_id)
                chunk = await session.execute(query) 
                chunk = chunk.scalar_one_or_none()
                return chunk
    
    async def insert_many_chunks(self, chunks: List[DataChunk], batch_size: int=100):
        async with self.db_client() as session: 
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i+batch_size]
                    session.add_all(batch)
            await session.commit()
        
        return len(chunks)
    
    
    async def delete_chunks_by_project_id(self, project_id: str):
        async with self.db_client() as session:
            query = delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
            result = await session.execute(query)
            await session.commit()
        return result.rowcount
    
    async def get_poject_chunks(self, project_id: str, page_no: int=1, page_size: int=50):
        async with self.db_client() as session:
            query = select(DataChunk).where(DataChunk.chunk_project_id == project_id).offset((page_no - 1) * page_size).limit(page_size)
            result = await session.execute(query)
            records = result.scalars().all()
        return records
    
    async def get_total_chunks_count(self, project_id: str):
        total_count = 0
        async with self.db_client() as session:
            query = select(func.count(DataChunk.chunk_id)).where(DataChunk.chunk_project_id == project_id)
            records_count = await session.execute(query)
            total_count = records_count.scalar()
        
        return total_count
    
