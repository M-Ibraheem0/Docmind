from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.document import DocumentChunk, Document, DocumentStatus
from app.config import settings


PROMPT = ChatPromptTemplate.from_template("""
You are a helpful assistant that answers questions based only on the provided document context.
Always cite which part of the document your answer comes from.
If the answer is not in the context, say "I could not find this information in the provided documents."

Context:
{context}

Question: {question}

Answer:
""")


async def get_answer(question: str, user_id: int, db: AsyncSession) -> dict:
    embeddings_model = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        api_key=settings.OPENAI_API_KEY
    )
    question_embedding = await embeddings_model.aembed_query(question)

    embedding_str = "[" + ",".join(str(x) for x in question_embedding) + "]"

    result = await db.execute(
        text("""
            SELECT dc.id, dc.content, dc.chunk_index, d.filename,
                   dc.embedding <=> CAST(:embedding AS vector) AS distance
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE d.user_id = :user_id AND d.status = 'ready'
            ORDER BY distance ASC
            LIMIT 5
        """),
        {"embedding": embedding_str, "user_id": user_id}
    )
    chunks = result.fetchall()

    if not chunks:
        return {
            "answer": "No documents found. Please upload a document first.",
            "sources": []
        }

    context = "\n\n".join([
        f"[Source: {chunk.filename}, chunk {chunk.chunk_index}]\n{chunk.content}"
        for chunk in chunks
    ])

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=settings.OPENAI_API_KEY
    )

    chain = PROMPT | llm
    response = await chain.ainvoke({"context": context, "question": question})

    sources = [
        {"filename": chunk.filename, "chunk_index": chunk.chunk_index, "excerpt": chunk.content[:200]}
        for chunk in chunks
    ]

    return {"answer": response.content, "sources": sources}