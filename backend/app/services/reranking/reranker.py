from collections import defaultdict
import numpy as np

from app.services.embeddings.embedder import get_embedding_model


def rerank_results(
    query: str,
    results: list,
    top_k: int = 5
):
    if not results:
        return []

    # =====================================================
    # 1. Remove duplicate chunks
    # =====================================================

    unique_results = []
    seen_chunks = set()

    for result in results:
        chunk_id = str(result.id)
        if chunk_id in seen_chunks:
            continue

        seen_chunks.add(chunk_id)
        unique_results.append(result)

    if not unique_results:
        return []

    # =====================================================
    # 2. Score chunks using FastEmbed vector similarity
    # =====================================================

    try:
        model = get_embedding_model()
        query_vec = list(model.embed([query]))[0]
        contents = [res.content for res in unique_results]
        content_vecs = list(model.embed(contents))

        scored_results = []
        for result, vec in zip(unique_results, content_vecs):
            norm_q = np.linalg.norm(query_vec)
            norm_v = np.linalg.norm(vec)
            score = float(np.dot(query_vec, vec) / ((norm_q * norm_v) + 1e-9))
            scored_results.append(
                {
                    "result": result,
                    "score": score
                }
            )
    except Exception as e:
        print(f"Warning: Reranking error: {e}")
        return unique_results[:top_k]

    # =====================================================
    # 3. Sort by relevance score
    # =====================================================

    scored_results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # =====================================================
    # 4. Group results by document
    # =====================================================

    document_groups = defaultdict(list)

    for item in scored_results:
        document_id = str(
            item["result"].document_id
        )
        document_groups[document_id].append(item)

    # =====================================================
    # 5. Calculate document relevance
    # =====================================================

    document_scores = []

    for document_id, items in document_groups.items():
        items.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        best_scores = [
            item["score"]
            for item in items[:2]
        ]

        document_score = sum(
            best_scores
        ) / len(best_scores)

        document_scores.append(
            (
                document_id,
                document_score
            )
        )

    # =====================================================
    # 6. Rank documents
    # =====================================================

    document_scores.sort(
        key=lambda item: item[1],
        reverse=True
    )

    # =====================================================
    # 7. Select chunks
    # =====================================================

    ranked_results = []

    for document_id, _ in document_scores:
        items = document_groups[
            document_id
        ]

        items.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        for item in items:
            ranked_results.append(
                item["result"]
            )

            if len(ranked_results) >= top_k:
                break

        if len(ranked_results) >= top_k:
            break

    return ranked_results