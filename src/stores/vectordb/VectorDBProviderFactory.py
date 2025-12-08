from .providers import QdrantDBProvider
from .providers import PGVectorProvider
from .VectorDBEnums import VectorDBEnums
from controllers.BaseController import BaseController
from sqlalchemy.orm import sessionmaker

class VectorDBProviderFactory:

    def __init__(self, config: dict, db_client: sessionmaker = None):
        self.config = config
        self.base_controller = BaseController()
        self.db_client = db_client
    
    def create(self, provider: str):

        if provider == VectorDBEnums.QDRANT.value:
            qdrant_db_client = self.base_controller.get_database_path(db_name = self.config.QDRANT_DB_PATH)
            qdrant_cache = self.base_controller.get_cache_path(cache_name = self.config.QDRANT_CACHE_PATH)

            return QdrantDBProvider(
                db_client = qdrant_db_client,
                qdrant_cache = qdrant_cache,
                distance_method = self.config.VECTOR_DB_DISTANCE_METHOD
            )
        
        if provider == VectorDBEnums.PGVECTOR.value:

            return PGVectorProvider(
                db_client = self.db_client,
                default_vector_size = self.config.EMBEDDING_MODEL_DIMENSION,
                distance_method = self.config.VECTOR_DB_DISTANCE_METHOD,
                index_threshold = self.config.INDEX_THRESHOLD
            )
        
        return None

