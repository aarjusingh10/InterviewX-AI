from dataclasses import dataclass
from app.core.config import get_settings


SEED_KNOWLEDGE = [
    ("dsa", "Explain time and space complexity for hash maps, heaps, binary search, graphs, and dynamic programming."),
    ("machine_learning", "Discuss bias variance, model selection, evaluation metrics, overfitting prevention, feature engineering, and deployment monitoring."),
    ("nlp", "Cover tokenization, embeddings, transformers, RAG, hallucination mitigation, evaluation, and prompt design."),
    ("data_engineering", "Discuss batch and streaming pipelines, data quality, orchestration, partitioning, warehousing, and lineage."),
    ("system_design", "Cover API design, caching, queues, database choice, scaling, consistency, observability, and failure handling."),
    ("behavioral", "Ask STAR-based questions about ownership, conflict, leadership, ambiguity, and learning from failure."),
    ("frontend", "Cover React rendering, TypeScript, accessibility, performance, state management, testing, and design systems."),
    ("backend", "Cover REST APIs, authentication, SQL schema design, transactions, caching, containers, testing, and monitoring."),
]


@dataclass
class RetrievedContext:
    topic: str
    content: str


class KnowledgeBase:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.collection = None
        try:
            import chromadb

            client = chromadb.HttpClient(host=self.settings.chroma_host, port=self.settings.chroma_port)
            self.collection = client.get_or_create_collection("interviewx_knowledge")
            if self.collection.count() == 0:
                self.collection.add(
                    ids=[f"seed-{i}" for i, _ in enumerate(SEED_KNOWLEDGE)],
                    documents=[content for _, content in SEED_KNOWLEDGE],
                    metadatas=[{"topic": topic} for topic, _ in SEED_KNOWLEDGE],
                )
        except Exception:
            self.collection = None

    def retrieve(self, query: str, limit: int = 5) -> list[RetrievedContext]:
        if self.collection:
            try:
                result = self.collection.query(query_texts=[query], n_results=limit)
                docs = result.get("documents", [[]])[0]
                metas = result.get("metadatas", [[]])[0]
                return [RetrievedContext(meta.get("topic", "general"), doc) for doc, meta in zip(docs, metas)]
            except Exception:
                pass
        query_lower = query.lower()
        ranked = sorted(
            SEED_KNOWLEDGE,
            key=lambda item: sum(1 for word in query_lower.split() if word in f"{item[0]} {item[1]}".lower()),
            reverse=True,
        )
        return [RetrievedContext(topic, content) for topic, content in ranked[:limit]]


knowledge_base = KnowledgeBase()

