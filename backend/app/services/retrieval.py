"""
Offline Knowledge Retrieval Service for Indian Farmers.
Uses TF-IDF / BM25-style lexical and semantic keyword matching over local verified documents.
No cloud vector database or external API required. Completely self-contained.
"""
import json
import os
import re
from typing import List, Dict, Any, Optional

KB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "documents.json"))

class AgriculturalKnowledgeRetriever:
    def __init__(self, kb_path: str = KB_PATH):
        self.kb_path = kb_path
        self.documents: List[Dict[str, Any]] = []
        self.load_documents()

    def load_documents(self):
        if os.path.exists(self.kb_path):
            with open(self.kb_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
        else:
            self.documents = []

    def add_document(self, doc: Dict[str, Any]) -> bool:
        """Allows agricultural officers or administrators to append trusted offline guides."""
        required = ["id", "title", "language", "content", "source"]
        if not all(k in doc for k in required):
            return False
        
        # Check if exists and update or append
        existing = next((i for i, d in enumerate(self.documents) if d["id"] == doc["id"]), None)
        if existing is not None:
            self.documents[existing] = doc
        else:
            self.documents.append(doc)
            
        with open(self.kb_path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
        return True

    def _tokenize(self, text: str) -> set:
        """Tokenize text into lowercase words/terms."""
        # Clean punctuation while preserving Indic characters and numbers
        cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
        return {word.strip() for word in cleaned.split() if len(word.strip()) > 1}

    def search(self, query: str, language: Optional[str] = None, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Search for relevant agricultural documents given a user query.
        Returns top matching documents with match score and source metadata.
        """
        if not query or not self.documents:
            return []

        query_tokens = self._tokenize(query)
        scored_docs = []

        for doc in self.documents:
            # Score factors:
            # 1. Exact query terms matching in title, keywords, content
            # 2. Language match bonus
            score = 0.0

            title_tokens = self._tokenize(doc.get("title", ""))
            content_tokens = self._tokenize(doc.get("content", ""))
            keywords = [kw.lower() for kw in doc.get("keywords", [])]

            # Direct keyword phrase matching
            query_lower = query.lower()
            for kw in keywords:
                if kw in query_lower:
                    score += 5.0

            # Token overlap
            title_overlap = len(query_tokens.intersection(title_tokens))
            content_overlap = len(query_tokens.intersection(content_tokens))

            score += title_overlap * 3.5
            score += content_overlap * 1.0

            # Language affinity bonus
            if language and doc.get("language") == language:
                score += 1.5

            if score > 0:
                scored_docs.append({
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "crop": doc.get("crop"),
                    "category": doc.get("category"),
                    "language": doc.get("language"),
                    "content": doc.get("content"),
                    "source": doc.get("source"),
                    "score": round(score, 2)
                })

        # Sort by score descending
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]

# Global retriever singleton
retriever = AgriculturalKnowledgeRetriever()
