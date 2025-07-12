from arango import ArangoClient
from langchain_community.graphs import ArangoGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_ollama import ChatOllama
from langchain_core.documents import Document



llm = ChatOllama(model="gemma3")

client = ArangoClient()

graph = ArangoGraph.from_db_credentials(
    url="http://localhost:8529",
    dbname="InsurBot_Graph",
)


text = ""
with open("actions\document_store\policy_docs\life_insurance_benefits.txt", "r") as file:
    text = file.read(
    )
    

documents = [Document(page_content=text)]
llm_transformer = LLMGraphTransformer(llm=llm)
graph_documents = llm_transformer.convert_to_graph_documents(documents)
