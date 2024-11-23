from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = (
    "You are a web scraper agent. you are tasked with answering questions and extracting specific "
    "information from the following webpage content: {body_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Answer the query:** Answer the question delimited by <<>> in a clear way and using only the webpage content provided and no prior knowledge."
    "2. **Understand the question:** If the question is about extracting information then only extract the information that directly matches the question."
    "3. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "4. **Empty Response:** If no information matches the description, return 'I'm sorry, no information match your query!'."
    "5. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
    "The question: <<{query}>>"
)

model = OllamaLLM(model='llama3.1')

def parse_with_ollama(chunks, query):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_result = []

    for i, chunk in enumerate(chunks, start=1):
        response = chain.invoke({"body_content": chunk, "query": query})
        print(f"Parsed batch {i} of {len(chunks)}")
        parsed_result.append(response)
    return "\n".join(parsed_result)

