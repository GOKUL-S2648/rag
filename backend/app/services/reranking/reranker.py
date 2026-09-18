from collections import defaultdict
from fastembed import TextReRanker


MODEL_NAME = "BAAI/bge-reranker-base"

_reranker_model = None


def get_reranker_model():
    global _reranker_model
    if _reranker_model is None:
        try:
            _reranker_model = TextReRanker(model_name=MODEL_NAME)
        except Exception as e:
            print(f"Warning: Failed to load reranker model: {e}")
            _reranker_model = False
    return _reranker_model if _reranker_model is not False else None


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
    # 2. Rerank using FastEmbed TextReRanker (or fallback)
    # =====================================================

    reranker = get_reranker_model()

    if reranker is None:
        # Fallback to returning original top_k results if reranker unavailable
        return unique_results[:top_k]

    try:
        contents = [res.content for res in unique_results]
        rerank_gen = reranker.rerank(query, contents)

        scored_results = []
        for item in rerank_gen:
            idx = item["index"] if isinstance(item, dict) else getattr(item, "index", 0)
            score = item["score"] if isinstance(item, dict) else getattr(item, "score", 0.0)
            scored_results.append(
                {
                    "result": unique_results[idx],
                    "score": float(score)
                }
            )
    except Exception as e:
        print(f"Warning: Error during reranking execution: {e}")
        return unique_results[:top_k]

    # =====================================================
    # 4. Sort by relevance
    # =====================================================

    scored_results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # =====================================================
    # 5. Group results by document
    # =====================================================

    document_groups = defaultdict(list)

    for item in scored_results:
        document_id = str(
            item["result"].document_id
        )
        document_groups[document_id].append(item)

    # =====================================================
    # 6. Calculate document relevance
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
    # 7. Rank documents
    # =====================================================

    document_scores.sort(
        key=lambda item: item[1],
        reverse=True
    )

    # =====================================================
    # 8. Select chunks
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