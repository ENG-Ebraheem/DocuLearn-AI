from enum import Enum


class ChatMode(Enum):
    GENERAL = "general"
    DOCUMENT_RAG = "document_rag"
    GENERAL_FALLBACK = "general_fallback"
