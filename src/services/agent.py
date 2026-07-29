from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3",
    temperature=0
)

messages = [
    (
        "system",
        "Você é um professor de engenharia de dados e IA, responda em portugues do Brasil",
    ),
    ("user", "Explique RAG dentro da engenharia de IA em uma frase"),
]
ai_msg = llm.invoke(messages)
print(ai_msg.content)