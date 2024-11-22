import pymongo
from IPython.display import Markdown
import textwrap
from embeddings import SentenceTransformerEmbedding, EmbeddingConfig
from qdrant_client import models, QdrantClient

class RAG_QRANT():
    def __init__(self,
                 QdrantUri: str,
                 collectionName: str,
                 llm,
                 embeddingName: str = "keepitreal/vietnamese-sbert",
                 ):
        self.qdrant = QdrantClient(QdrantUri)
        self.collectionName = collectionName
        self.embedding_model = SentenceTransformerEmbedding(EmbeddingConfig(name=embeddingName))
        self.llm = llm

    def get_embedding(self, text):
        if not text.strip():
            return []
        
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    
    def vector_search(self, user_query: str, limit = 4):
        query_embedding = self.get_embedding(user_query)

        if query_embedding is None:
            return "Invalid query or embedding generation failed."
        
        hits = self.qdrant.search(
            collection_name=self.collectionName,
            query_vector=query_embedding,
            limit = limit,
        )
        results = [{"score": hit.score, "name": hit.payload["name"], "price": hit.payload["priceInfo.linePrice"], "rating": hit.payload["rating"]} for hit in hits]
        return results
    
    def vector_search_law(self, user_query: str, limit = 4):
        query_embedding = self.get_embedding(user_query)

        if query_embedding is None:
            return "Invalid query or embedding generation failed."
        
        hits = self.qdrant.search(
            collection_name=self.collectionName,
            query_vector=query_embedding,
            limit = limit,
        )
        results = [{"score": hit.score, "Chương": hit.payload["Chương"], "Điều": hit.payload["Điều"], "Nội dung": hit.payload["Nội dung"] , "Mục":hit.payload["Mục"], "Phần":hit.payload["Phần"]} for hit in hits]
        return results
    
    def enhance_prompt_law(self, query):
        get_knowledge = self.vector_search_law(query, 10)
        enhanced_prompt = ""
        i=0
        for result in get_knowledge:
            if result.get('Chương'):
                i += 1
                enhanced_prompt += f"\n {i}){result.get('Chương')}"
                if result.get('Mục'):
                    enhanced_prompt += f",{result.get('Mục')}"
                if result.get('Điều'):
                    enhanced_prompt += f",{result.get('Điều')}"
                if result.get('Phần'):
                    enhanced_prompt += f",{result.get('Phần')}"
                if result.get('Nội dung'):
                    enhanced_prompt += f", Nội dung : {result.get('Nội dung')}"
                
        return enhanced_prompt
    
    def generate_content(self, prompt):
        return self.llm.generate_content(prompt)
    
    def _to_markdown(text):
        text = text.replace('•', '*')
        return Markdown(textwrap.indent(text, '> ', predicate=lambda _:True))


    


    