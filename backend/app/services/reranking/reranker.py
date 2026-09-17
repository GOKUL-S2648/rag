from collections import defaultdict

from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker_model = CrossEncoder(MODEL_NAME)


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
    # 2. Create query-document pairs
    # =====================================================

    pairs = [
        [query, result.content]
        for result in unique_results
    ]

    # =====================================================
    # 3. Cross-encoder scoring
    # =====================================================

    scores = reranker_model.predict(pairs)

    scored_results = []

    for result, score in zip(
        unique_results,
        scores
    ):
        scored_results.append(
            {
                "result": result,
                "score": float(score)
            }
        )

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
    #
    # Use the best two chunks from each document.
    # This prevents one document with many weak chunks
    # from dominating the results.
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
    #
    # Give priority to the most relevant document.
    # Still allow other highly relevant documents.
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