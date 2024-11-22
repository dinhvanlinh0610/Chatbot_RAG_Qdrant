import pandas as pd
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse
from embeddings import SentenceTransformerEmbedding, EmbeddingConfig
from database.pdf_to_csv import extract_pdf_to_csv
from database.word_to_csv import extract_docx_to_csv
import time
class QDRANT_DATABASE():
    def __init__(self,
                 QdrantUri: str,
                 collectionName: str,
                 embeddingName: str ,
                 document_path: str ,

                 ):
        self.qdrant = QdrantClient(QdrantUri)
        self.collectionName = collectionName
        self.embedding_model = SentenceTransformerEmbedding(EmbeddingConfig(name=embeddingName))
        self.document_path = document_path

    # Load data from CSV csv file
    def load_data(self, document_path):
        #kiểm tra xem document_path là đường dẫn đuôi gì csv, pdf, word, xlxx, docs, txt
        if document_path.endswith('.csv'):
            df = pd.read_csv(document_path)
            df = df.fillna('')
        elif document_path.endswith('.pdf'):
            output_csv_path = f'temple-{time.time()}.csv'
            extract_pdf_to_csv(document_path, output_csv_path)
            df = pd.read_csv(output_csv_path)
            df = df.fillna('')
        elif document_path.endswith('.docx'):
            output_csv_path = f'temple-{time.time()}.csv'
            extract_docx_to_csv(document_path, output_csv_path)
            df = pd.read_csv(document_path)
            df = df.fillna('')
        else:
            raise ValueError("File format not supported")
        return df
    
    # Preprocess data
    def preprocess_data(self, df):
        df['combined_text'] = df['Chương'] + ' ' + df['Mục'] + ' ' + df['Điều']
        df['embedding'] = df['combined_text'].apply(lambda x: self.embedding_model.encode(x))
        return df
    
    # Create collection if not exists
    def create_collection(self):
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

    # upsert data to collection
    def upsert_data(self, df):
        points = [
            PointStruct(
                id=index,
                vector=row['embedding'],
                payload=row.drop(labels=['embedding']).to_dict()
            )
            for index, row in df.iterrows()
        ]
        self.qdrant.upsert(collection_name=self.collectionName, points=points)

    # Process data
    def process_csv(self):
        df = self.load_data(self.document_path)
        df = self.preprocess_data(df)
        self.create_collection()
        self.upsert_data(df)
        print(df.head())
