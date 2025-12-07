from enum import Enum
class ResponseEnumeration(Enum):
    FILE_VALIDATION_SUCCESS = "File validation successful."
    FILE_UPLOADED_SUCCESS = "File uploaded successfully."
    FILE_UPLOAD_FAILED = "File upload failed."
    INVALID_FILE_TYPE = "File type {file_type} is not allowed."
    FILE_TOO_LARGE = "File size exceeds the maximum limit of {file_size} MB."
    FILE_NOT_EXIST = "The file {file_path} does not exist."
    FILE_EXIST = "The file {file_path} already exists."
    PROJECT_NOT_FOUND_ERROR = "project_not_found"
    INSERT_INTO_VECTORDB_ERROR = "insert_into_vectordb_error"
    INSERT_INTO_VECTORDB_SUCCESS = "insert_into_vectordb_success"
    VECTORDB_COLLECTION_RETRIEVED = "vectordb_collection_retrieved"
    VECTORDB_SEARCH_ERROR = "vectordb_search_error"
    VECTORDB_SEARCH_SUCCESS = "vectordb_search_success"
    RAG_ANSWER_ERROR = "rag_answer_error"
    RAG_ANSWER_SUCCESS = "rag_answer_success"
    QUERY_EXPANSION_FAILD = "query_expansion_faild"
    # PROCESSING_SUCCESS = "File {file_name} processed successfully with {chunks} chunks."
    PROCESSING_SUCCESS = "processing_success"
    PROCESSING_FAILED = "processing_failed"
    NO_FILES_ERROR = "not_found_files"
    FILE_ID_ERROR = "no_file_found_with_this_id"



# "File '{file.filename}' uploaded successfully to project '{project_id}'."