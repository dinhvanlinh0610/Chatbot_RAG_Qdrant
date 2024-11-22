from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai
from flask_cors import CORS
from rag.core import RAG_QRANT
from semantic_router import SemanticRouter, Route
from semantic_router.samples import lawSample, chitchatSample
from semantic_cache import SemanticCache
from embeddings import SentenceTransformerEmbedding, EmbeddingConfig
import google.generativeai as genai
from reflection.core import Reflection
from database import QDRANT_DATABASE
load_dotenv()

LLM_KEY = ""
EMBEDDING_MODEL = "keepitreal/vietnamese-sbert"
QDRANT_URI = "http://localhost:6333"
COLLECTION_NAME = "law_of_marriage"


# Semantic Router Setup
PRODUCT_ROUTE_NAME = "law"
CHITCHAT_ROUTE_NAME = "chitchat"

openAIEmbedding = SentenceTransformerEmbedding(EmbeddingConfig(name=EMBEDDING_MODEL))
lawRoute = Route(name=PRODUCT_ROUTE_NAME, samples=lawSample)
chitchatRoute = Route(name=CHITCHAT_ROUTE_NAME, samples=chitchatSample)
semanticRouter = SemanticRouter(openAIEmbedding,routes=[lawRoute, chitchatRoute])
semanticCache = SemanticCache(QDRANT_URI, "memory", EMBEDDING_MODEL)

# Set up LLMs
genai.configure(api_key=LLM_KEY)
llm = genai.GenerativeModel('gemini-1.0-pro')

reflection = Reflection(llm)

app = Flask(__name__)
CORS(app)

rag = RAG_QRANT(
    QdrantUri=QDRANT_URI,
    collectionName=COLLECTION_NAME,
    llm=llm,
    embeddingName=EMBEDDING_MODEL
)

def process_query(data):
    query =  data[-1]["parts"][0]["text"]
    query = query.strip()
    query = query.replace("\n", " ")
    query = query.replace("\t", " ")
    query = query.replace("\r", " ")
    query = query.replace("  ", " ")
    query = query.replace("?", "")
    query = query.replace("!", "")
    return query.lower()

def RAG_process(data, query, query_memory):
    print("Guided to RAGs")
    reflected_query = reflection(data)
    print("\n--------------------------------------\nreflected_query", reflected_query, "\n--------------------------------------\n")
    source_information = rag.enhance_prompt_law(reflected_query).replace('<br>', '\n')
    print("source_information", source_information,"\n--------------------------------------\n")
    combined_information = f"Hãy trở thành chuyên gia tư vấn về luật cho luật sư. Câu hỏi của khách hàng: {query}\nTrả lời câu hỏi dựa vào các thông tin dưới đây:{source_information}."
    # data.append({
    #     "role": "user",
    #     "parts": [
    #         {
    #             "text": combined_information
    #         }
    #     ]
    # })

    print("combined_information", combined_information,"\n--------------------------------------\n")
    response = rag.generate_content(combined_information)
    semanticCache.save_query(query_memory, response.text)
    return response
    

def LLM_process(data, query):
    print("Guided to LLMs")
    response = llm.generate_content(query)
    return response

@app.route('/api/insert_data', methods=['POST'])
def data_of_csv():
    #nhận vào data từ api là 1 đường dẫn tới file csv
    data_path = request.get_json()
    databaseVector = QDRANT_DATABASE(QDRANT_URI, "law_of_marriage", EMBEDDING_MODEL, data_path["data_path"])
    databaseVector.process_csv()
    return "Insert data successfully"

@app.route('/api/search', methods=['POST'])
def handle_query():
    data = list(request.get_json())
    query = process_query(data)
    query_memory = query
    if not query:
        return jsonify({"error": "No query provided."}), 400
    guidedMemory = semanticCache.vector_search(query)
    for results in guidedMemory:
        print("score", results.get('score'))
        if results.get('score') >= 0.98:
            print("Guided by Memory")
            print("score", results.get('score'))
            response = results.get('answer')
            return jsonify({
                'parts': [
                    {
                        'text': response
                    }
                ],
                'role': 'model'
            })

    guidedRoute = semanticRouter.guide(query)[1]
    if guidedRoute == PRODUCT_ROUTE_NAME:
        response = RAG_process(data, query, query_memory)
        return jsonify({
            'parts': [
                {
                    'text': response.text
                }
            ],
            'role': 'model'
        })

    if guidedRoute == CHITCHAT_ROUTE_NAME:
        response = LLM_process(data, query)
        return jsonify({
            'parts': [
                {
                    'text': response.text
                }
            ],
            'role': 'model'
        })
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
