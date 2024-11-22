import pandas as pd
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct, VectorParams, PayloadSchemaType, CollectionInfo

# Đọc file CSV
df = pd.read_csv('van_ban_phap_luat_5.csv')

# Khởi tạo SentenceTransformer
model = SentenceTransformer('keepitreal/vietnamese-sbert')  # Bạn có thể chọn mô hình khác nếu muốn

# Tạo cột mới "combined_text" từ các cột "chương", "mục" và "điều", nếu cái nào không có thì bỏ qua
df = df.fillna('')
df['combined_text'] = df['Chương'] + ' ' + df['Mục'] + ' ' + df['Điều']

# Tạo embedding cho cột "name" và cột "description"
df['embedding'] = df['combined_text'].apply(lambda x: model.encode(x))



# df['embedding'] = df['name'].apply(lambda x: model.encode(x))

# Khởi tạo Qdrant client
client = QdrantClient(host="localhost", port=6333)

# Tên collection mong muốn 
collection_name = "law_of_marriage"

# Kiểm tra xem collection có tồn tại không
collections = client.get_collections().collections
collection_names = [col.name for col in collections]

# Nếu collection chưa tồn tại, tạo nó với các trường từ CSV và embedding
if collection_name not in collection_names:
    # Lấy kích thước của vector embedding
    vector_size = len(df['embedding'].iloc[0])
    
    # Tạo collection với các thông số vector và schema cho các trường khác
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=vector_size, distance="Cosine"),  
    )

# Tạo điểm (point) để lưu trữ trong Qdrant
points = [
    PointStruct(
        id=index, 
        vector=row['embedding'], 
        payload=row.drop(labels=['embedding']).to_dict()
    )
    for index, row in df.iterrows()
]
# Lưu điểm vào Qdrant
client.upsert(collection_name=collection_name, points=points)

# Hiển thị DataFrame với cột embedding mới
print(df.head())
