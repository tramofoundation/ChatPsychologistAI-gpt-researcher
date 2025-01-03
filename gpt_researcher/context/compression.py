import os
import asyncio
from typing import Optional
from .retriever import SearchAPIRetriever, SectionRetriever
from langchain.retrievers import (
    ContextualCompressionRetriever,
)
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..memory.embeddings import OPENAI_EMBEDDING_MODEL
from ..vector_store import VectorStoreWrapper
from ..utils.costs import estimate_embedding_cost

class VectorstoreCompressor:
    def __init__(self, vector_store: VectorStoreWrapper, max_results=5, **kwargs):
        self.max_results = max_results
        self.vector_store = vector_store
        self.kwargs = kwargs
        self.similarity_threshold = os.environ.get("SIMILARITY_THRESHOLD", 0.38)

	# ChatPsy async_get_context()
    def __get_contextual_retriever(self):
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        #relevance_filter = EmbeddingsFilter(embeddings=self.embeddings,
                                            #similarity_threshold=self.similarity_threshold)
        pipeline_compressor = DocumentCompressorPipeline(
            # transformers=[splitter, relevance_filter]
            transformers=[splitter]
        )
        base_retriever = self.vector_store._get_retriever(self.similarity_threshold)
        contextual_retriever = ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=base_retriever
        )
        return contextual_retriever

    def __pretty_print_docs(self, docs, top_n):
        return f"\n".join(f"Source: {d.metadata.get('source')}\n"
                          f"Title: {d.metadata.get('title')}\n"
                          f"Content: {d.page_content}\n"
                          for i, d in enumerate(docs) if i < top_n)

	# ChatPsy ContextManager.get_similar_content_by_query()
    async def async_get_context(self, query, max_results=5, cost_callback=None):
        compressed_docs = self.__get_contextual_retriever()
        # if cost_callback:
           # cost_callback(estimate_embedding_cost(model=OPENAI_EMBEDDING_MODEL, docs=self.documents))
        relevant_docs = await asyncio.to_thread(compressed_docs.invoke, query)
        return self.__pretty_print_docs(relevant_docs, max_results)

class ContextCompressor:
    def __init__(self, documents, embeddings, max_results=5, **kwargs):
        self.max_results = max_results
        self.documents = documents
        self.kwargs = kwargs
        self.embeddings = embeddings
        self.similarity_threshold = os.environ.get("SIMILARITY_THRESHOLD", 0.38)

	# ChatPsy async_get_context()
    def __get_contextual_retriever(self):
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        relevance_filter = EmbeddingsFilter(embeddings=self.embeddings,
                                            similarity_threshold=self.similarity_threshold)
        pipeline_compressor = DocumentCompressorPipeline(
            transformers=[splitter, relevance_filter]
        )
        base_retriever = SearchAPIRetriever(
            pages=self.documents
        )
        contextual_retriever = ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=base_retriever
        )
        return contextual_retriever

    def __pretty_print_docs(self, docs, top_n):
        return f"\n".join(f"Source: {d.metadata.get('source')}\n"
                          f"Title: {d.metadata.get('title')}\n"
                          f"Content: {d.page_content}\n"
                          for i, d in enumerate(docs) if i < top_n)

	# ChatPsy ContextManager.get_similar_content_by_query()
    async def async_get_context(self, query, max_results=5, cost_callback=None):
        compressed_docs = self.__get_contextual_retriever()
        if cost_callback:
            cost_callback(estimate_embedding_cost(model=OPENAI_EMBEDDING_MODEL, docs=self.documents))
        relevant_docs = await asyncio.to_thread(compressed_docs.invoke, query)
        #return self.__pretty_print_docs(relevant_docs, max_results)
        self.__pretty_print_docs(relevant_docs, max_results)
        return relevant_docs
