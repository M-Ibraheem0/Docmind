import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from app.config import settings

from app.database import engine
from app.models.document import Document, DocumentChunk, DocumentStatus

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def process_document(document_id: int):
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Document).where(Document.id == document_id))
            doc = result.scalar_one_or_none()
            if not doc:
                return

            doc.status = DocumentStatus.processing
            await db.commit()

            # load PDF in thread so we dont block the event loop
            loader = PyPDFLoader(doc.file_path)
            pages = await asyncio.to_thread(loader.load)

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(pages)

            embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=settings.OPENAI_API_KEY)
            texts = [chunk.page_content for chunk in chunks]
            embeddings = await embeddings_model.aembed_documents(texts)

            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                db.add(DocumentChunk(
                    document_id=document_id,
                    content=chunk.page_content,
                    embedding=embedding,
                    chunk_index=i,
                ))

            doc.status = DocumentStatus.ready
            doc.chunk_count = len(chunks)
            await db.commit()

        except Exception as e:
            async with AsyncSessionLocal() as err_db:
                result = await err_db.execute(select(Document).where(Document.id == document_id))
                doc = result.scalar_one_or_none()
                if doc:
                    doc.status = DocumentStatus.failed
                    await err_db.commit()
            raise