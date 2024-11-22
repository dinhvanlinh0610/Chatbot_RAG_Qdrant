import pymongo
from IPython.display import Markdown
import textwrap
from embeddings import SentenceTransformerEmbedding, EmbeddingConfig
from qdrant_client import models, QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
import uuid
class SemanticCache():
    def __init__(self,
                 QdrantUri: str,
                 collectionName: str,
                 embeddingName: str = "keepitreal/vietnamese-sbert",
                 ):
        self.qdrant = QdrantClient(QdrantUri)
        self.collectionName = collectionName
        self.embedding_model = SentenceTransformerEmbedding(EmbeddingConfig(name=embeddingName))

        # Ensure the collection exists or create it if it doesn't
        try:
            self.qdrant.get_collection(self.collectionName)
        except UnexpectedResponse:
            self.qdrant.create_collection(
                collection_name=self.collectionName,
                vectors_config=models.VectorParams(
                    size=768,
                    distance=models.Distance.COSINE
                )
            )
        
    def get_embedding(self, text):
        if not text.strip():
            return []
        
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    
    def vector_search(self, user_query: str, limit=1):
        query_embedding = self.get_embedding(user_query)

        if not query_embedding:
            return "Invalid query or embedding generation failed."
        
        hits = self.qdrant.search(
            collection_name=self.collectionName,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )
        
        results = [{"score": hit.score, "query": hit.payload["query"], "answer": hit.payload["answer"]} for hit in hits]
        return results
    
    def save_query(self, query, answer):
        # Lưu lại vào qdrant
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            return "Invalid query or embedding generation failed."
        
        # Tạo một UUID duy nhất cho mỗi điểm
        point_id = str(uuid.uuid4())
        
        self.qdrant.upsert(
            collection_name=self.collectionName,
            points=[
                models.PointStruct(
                    id=point_id,  # Sử dụng UUID làm ID
                    vector=query_embedding,
                    payload={"query": query, "answer": answer}
                )
            ]
        )
        return "Query saved successfully."
