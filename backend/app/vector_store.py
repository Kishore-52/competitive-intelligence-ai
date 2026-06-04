import math
import re
from typing import List, Dict, Tuple
from app.database import get_all_products

# A basic list of stop words to improve text matching quality
STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'arent', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'cant', 'cannot', 'could',
    'did', 'didnt', 'do', 'does', 'doesnt', 'doing', 'dont', 'down', 'during', 'each', 'few', 'for', 'from', 'further',
    'had', 'hadnt', 'has', 'hasnt', 'have', 'havent', 'having', 'he', 'hed', 'hell', 'hes', 'her', 'here', 'heres',
    'hers', 'herself', 'him', 'himself', 'his', 'how', 'hows', 'i', 'id', 'ill', 'im', 'ive', 'if', 'in', 'into', 'is',
    'isnt', 'it', 'its', 'itself', 'lets', 'me', 'more', 'most', 'mustnt', 'my', 'myself', 'no', 'nor', 'not', 'of',
    'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same',
    'shant', 'she', 'shed', 'shell', 'shes', 'should', 'shouldnt', 'so', 'some', 'such', 'than', 'that', 'thats',
    'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'theres', 'these', 'they', 'theyd', 'theyll',
    'theyre', 'theyve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasnt',
    'we', 'wed', 'well', 'were', 'weve', 'werent', 'what', 'whats', 'when', 'whens', 'where', 'wheres', 'which',
    'while', 'who', 'whos', 'whom', 'why', 'whys', 'with', 'wont', 'would', 'wouldnt', 'you', 'youd', 'youll',
    'youre', 'youve', 'your', 'yours', 'yourself', 'yourselves'
}

def tokenize(text: str) -> List[str]:
    """Lowercase text and extract word tokens, removing punctuation and filtering stop words."""
    cleaned = re.sub(r'[^\w\s]', '', text.lower())
    words = cleaned.split()
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]

class LocalVectorStore:
    def __init__(self):
        self.documents = []  # List of dicts with: id, product_name, feature_text, type
        self.vocab = set()
        self.idf = {}
        self.doc_vectors = []
        self.rebuild_index()

    def rebuild_index(self):
        """Load all products and features from database and compile a TF-IDF index."""
        try:
            products = get_all_products()
        except Exception as e:
            # Database or table might not be initialized yet during initial app imports
            products = []
        
        self.documents = []
        self.vocab = set()
        self.idf = {}
        self.doc_vectors = []
        
        # We index:

        # 1. Product general descriptions
        # 2. Individual specific product features
        for product in products:
            p_name = product["name"]
            
            # Product overview
            self.documents.append({
                "product_name": p_name,
                "content": f"{p_name} overview: {product['description']}",
                "type": "overview"
            })
            
            # Features list
            import json
            try:
                features = json.loads(product["features"])
                for feature in features:
                    self.documents.append({
                        "product_name": p_name,
                        "content": f"{p_name} feature capability: {feature}",
                        "type": "feature"
                    })
            except Exception:
                pass
                
        if not self.documents:
            return

        # 1. Tokenize documents and build vocabulary
        tokenized_docs = [tokenize(doc["content"]) for doc in self.documents]
        
        for tokens in tokenized_docs:
            for token in tokens:
                self.vocab.add(token)

        # 2. Calculate IDF for each term
        num_docs = len(self.documents)
        term_doc_counts = {term: 0 for term in self.vocab}
        for tokens in tokenized_docs:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                if token in term_doc_counts:
                    term_doc_counts[token] += 1
                    
        for term, count in term_doc_counts.items():
            # Standard IDF with smoothing to avoid division by zero
            self.idf[term] = math.log((1 + num_docs) / (1 + count)) + 1

        # 3. Calculate TF-IDF vectors for all documents
        for tokens in tokenized_docs:
            tf = {}
            for token in tokens:
                tf[token] = tf.get(token, 0) + 1
                
            vector = {}
            magnitude_sq = 0.0
            for term, count in tf.items():
                tfidf_val = count * self.idf.get(term, 0)
                vector[term] = tfidf_val
                magnitude_sq += tfidf_val ** 2
                
            vector["__magnitude__"] = math.sqrt(magnitude_sq)
            self.doc_vectors.append(vector)

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Perform a TF-IDF cosine-similarity search against the indexed features."""
        # Make sure the index is fresh
        self.rebuild_index()
        
        if not self.documents:
            return []
            
        query_tokens = tokenize(query)
        if not query_tokens:
            # Fallback to returning the top overview documents if search query is empty/stopword-only
            return [
                {
                    "product_name": doc["product_name"],
                    "content": doc["content"],
                    "type": doc["type"],
                    "score": 0.0
                }
                for doc in self.documents[:top_k]
            ]
            
        # Calculate TF-IDF for query
        query_tf = {}
        for token in query_tokens:
            if token in self.vocab:
                query_tf[token] = query_tf.get(token, 0) + 1
                
        query_vector = {}
        query_magnitude_sq = 0.0
        for term, count in query_tf.items():
            tfidf_val = count * self.idf.get(term, 0)
            query_vector[term] = tfidf_val
            query_magnitude_sq += tfidf_val ** 2
        query_magnitude = math.sqrt(query_magnitude_sq)
        
        if query_magnitude == 0:
            # No matching words in dictionary
            return [
                {
                    "product_name": doc["product_name"],
                    "content": doc["content"],
                    "type": doc["type"],
                    "score": 0.0
                }
                for doc in self.documents[:top_k]
            ]

        # Calculate cosine similarity for each document vector
        results = []
        for idx, doc_vector in enumerate(self.doc_vectors):
            dot_product = 0.0
            for term, val in query_vector.items():
                dot_product += val * doc_vector.get(term, 0)
                
            doc_magnitude = doc_vector["__magnitude__"]
            
            score = 0.0
            if query_magnitude > 0 and doc_magnitude > 0:
                score = dot_product / (query_magnitude * doc_magnitude)
                
            results.append((score, self.documents[idx]))
            
        # Sort and select top_k
        results.sort(key=lambda x: x[0], reverse=True)
        
        formatted_results = []
        for score, doc in results[:top_k]:
            formatted_results.append({
                "product_name": doc["product_name"],
                "content": doc["content"],
                "type": doc["type"],
                "score": round(score, 4)
            })
            
        return formatted_results

# Global vector store instance
vector_store = LocalVectorStore()
