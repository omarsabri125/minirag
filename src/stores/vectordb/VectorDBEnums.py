from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "qdrant"
    PINECONE = "pinecone"


class DistanceMetricEnums(Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclid"
    DOT_PRODUCT = "dot"