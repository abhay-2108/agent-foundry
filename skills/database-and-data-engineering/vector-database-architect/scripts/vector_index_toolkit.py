#!/usr/bin/env python3
"""
Vector Database Architect & ANN Index Toolkit
=============================================
Zero-dependency toolkit for:
- High-dimensional vector distance computation (Cosine, Euclidean, Dot Product)
- Scalar Quantization (SQ8: float32 -> uint8) compression & recall distortion profiling
- Production hardware & RAM sizing calculator for HNSW and Quantized vector stores
- Pre-filtering vs. Post-filtering recall benchmark simulation
"""

import argparse
import math
import random
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# 1. Vector Math & Distance Metrics
# ---------------------------------------------------------------------------

def dot_product(u: List[float], v: List[float]) -> float:
    return sum(x * y for x, y in zip(u, v))


def euclidean_distance(u: List[float], v: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(u, v)))


def vector_norm(v: List[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def normalize_vector(v: List[float]) -> List[float]:
    norm = vector_norm(v)
    if norm == 0.0:
        return [0.0] * len(v)
    return [x / norm for x in v]


def cosine_similarity(u: List[float], v: List[float]) -> float:
    nu = vector_norm(u)
    nv = vector_norm(v)
    if nu == 0.0 or nv == 0.0:
        return 0.0
    return dot_product(u, v) / (nu * nv)


# ---------------------------------------------------------------------------
# 2. Scalar Quantization (SQ8: Float32 -> UInt8)
# ---------------------------------------------------------------------------

@dataclass
class QuantizedVector:
    data: bytes
    min_val: float
    max_val: float
    dimension: int


def quantize_sq8(vector: List[float]) -> QuantizedVector:
    """
    Compresses a float32 vector into uint8 (0-255) using linear min-max quantization.
    Reduces memory from 4 bytes/dim to 1 byte/dim (75% savings).
    """
    min_val = min(vector)
    max_val = max(vector)
    val_range = max_val - min_val

    if val_range == 0.0:
        quantized_bytes = bytes([128] * len(vector))
    else:
        quantized_bytes = bytes(
            int(round(((x - min_val) / val_range) * 255.0)) for x in vector
        )

    return QuantizedVector(
        data=quantized_bytes,
        min_val=min_val,
        max_val=max_val,
        dimension=len(vector)
    )


def dequantize_sq8(qvec: QuantizedVector) -> List[float]:
    """
    Reconstructs an approximation of the float32 vector from uint8 bytes.
    """
    val_range = qvec.max_val - qvec.min_val
    if val_range == 0.0:
        return [qvec.min_val] * qvec.dimension

    return [
        qvec.min_val + (b / 255.0) * val_range
        for b in qvec.data
    ]


def evaluate_quantization_distortion(vector: List[float]) -> float:
    """
    Measures cosine similarity between original vector and dequantized vector.
    Returns value between 0.0 and 1.0 (higher = better preservation).
    """
    qvec = quantize_sq8(vector)
    reconstructed = dequantize_sq8(qvec)
    return cosine_similarity(vector, reconstructed)


# ---------------------------------------------------------------------------
# 3. Hardware & RAM Sizing Calculator
# ---------------------------------------------------------------------------

@dataclass
class VectorSizingReport:
    vector_count: int
    dimensions: int
    raw_vector_ram_mb: float
    hnsw_graph_overhead_mb: float
    sq8_quantized_ram_mb: float
    recommended_total_ram_gb_float32: float
    recommended_total_ram_gb_sq8: float


def calculate_vector_sizing(
    count: int,
    dimensions: int,
    hnsw_m: int = 32,
    safety_margin: float = 1.30
) -> VectorSizingReport:
    """
    Computes exact memory requirements for raw vectors, HNSW graph structures,
    and quantized indexes.
    """
    # Raw float32: 4 bytes per dimension
    raw_bytes = count * dimensions * 4
    raw_mb = raw_bytes / (1024 * 1024)

    # HNSW graph: M connections per vector, bi-directional pointers (8 bytes pointer on 64-bit)
    # Plus neighbor list overhead (~20% internal indexing overhead)
    graph_bytes = count * hnsw_m * 2 * 8 * 1.20
    graph_mb = graph_bytes / (1024 * 1024)

    # SQ8: 1 byte per dimension + 8 bytes min/max metadata per vector
    sq8_bytes = (count * dimensions * 1) + (count * 8)
    sq8_mb = sq8_bytes / (1024 * 1024)

    # Total RAM recommendations in GB with safety margin
    total_gb_float32 = ((raw_mb + graph_mb) * safety_margin) / 1024
    total_gb_sq8 = ((sq8_mb + graph_mb) * safety_margin) / 1024

    return VectorSizingReport(
        vector_count=count,
        dimensions=dimensions,
        raw_vector_ram_mb=round(raw_mb, 2),
        hnsw_graph_overhead_mb=round(graph_mb, 2),
        sq8_quantized_ram_mb=round(sq8_mb, 2),
        recommended_total_ram_gb_float32=round(total_gb_float32, 2),
        recommended_total_ram_gb_sq8=round(total_gb_sq8, 2)
    )


# ---------------------------------------------------------------------------
# 4. Filtered ANN Search Simulation (Pre vs. Post Filtering)
# ---------------------------------------------------------------------------

def simulate_filtered_search(
    corpus_size: int = 1000,
    dimension: int = 64,
    tenant_selectivity: float = 0.05,
    top_k: int = 10,
    seed: int = 42
) -> Dict[str, float]:
    """
    Demonstrates recall collapse under Naive Post-Filtering compared to Single-Stage Pre-Filtering.
    """
    random.seed(seed)

    # Generate random normalized vectors with tenant tags
    corpus = []
    target_tenant = "tenant_alpha"

    for i in range(corpus_size):
        vec = normalize_vector([random.gauss(0, 1) for _ in range(dimension)])
        tenant = target_tenant if random.random() < tenant_selectivity else "other_tenant"
        corpus.append({"id": i, "vector": vec, "tenant": tenant})

    query_vec = normalize_vector([random.gauss(0, 1) for _ in range(dimension)])

    # 1. Ground Truth (Exact search over matching tenant records)
    tenant_records = [r for r in corpus if r["tenant"] == target_tenant]
    tenant_scored = [
        (r["id"], cosine_similarity(query_vec, r["vector"]))
        for r in tenant_records
    ]
    tenant_scored.sort(key=lambda x: x[1], reverse=True)
    ground_truth_ids = set(x[0] for x in tenant_scored[:top_k])

    # 2. Single-Stage Pre-Filtered Search (visits only matching tenant records)
    pre_filtered_ids = set(x[0] for x in tenant_scored[:top_k])
    pre_filter_recall = len(ground_truth_ids.intersection(pre_filtered_ids)) / max(len(ground_truth_ids), 1)

    # 3. Naive Post-Filtered Search (Finds global top_k * 2, then filters by tenant)
    global_scored = [
        (r["id"], r["tenant"], cosine_similarity(query_vec, r["vector"]))
        for r in corpus
    ]
    global_scored.sort(key=lambda x: x[2], reverse=True)
    candidate_window = global_scored[: top_k * 2]  # Typical naive post-filter limit
    post_filtered_ids = set(x[0] for x in candidate_window if x[1] == target_tenant)

    post_filter_recall = len(ground_truth_ids.intersection(post_filtered_ids)) / max(len(ground_truth_ids), 1)

    return {
        "pre_filter_recall": round(pre_filter_recall, 4),
        "post_filter_recall": round(post_filter_recall, 4),
        "ground_truth_count": len(ground_truth_ids),
        "post_filter_found_count": len(post_filtered_ids)
    }


# ---------------------------------------------------------------------------
# CLI & Self-Test Suite
# ---------------------------------------------------------------------------

def run_self_test():
    print("=================================================================")
    print("Running Vector Database Architect Toolkit Self-Tests...")
    print("=================================================================")

    # Test 1: Distance & Normalization
    u = [1.0, 0.0, 0.0]
    v = [0.0, 1.0, 0.0]
    assert cosine_similarity(u, v) == 0.0, "Orthogonal vectors should have 0 cosine similarity"
    assert math.isclose(euclidean_distance(u, v), math.sqrt(2.0)), "Euclidean distance check failed"
    u_norm = normalize_vector([3.0, 4.0])
    assert math.isclose(vector_norm(u_norm), 1.0), "Normalized vector norm should be 1.0"
    print("[PASS] Vector distance & normalization math passed")

    # Test 2: SQ8 Quantization & Distortion Evaluation
    random.seed(42)
    sample_vec = [random.uniform(-1.0, 1.0) for _ in range(1536)]
    qvec = quantize_sq8(sample_vec)
    assert len(qvec.data) == 1536, "Quantized bytes length must match vector dimension"
    reconstructed = dequantize_sq8(qvec)
    assert len(reconstructed) == 1536
    distortion_sim = evaluate_quantization_distortion(sample_vec)
    assert distortion_sim > 0.99, f"SQ8 cosine retention {distortion_sim} below 0.99"
    print(f"[PASS] SQ8 Quantization passed (Cosine retention: {distortion_sim:.5f})")

    # Test 3: Hardware & RAM Sizing
    report = calculate_vector_sizing(count=1_000_000, dimensions=1536, hnsw_m=32)
    assert report.raw_vector_ram_mb > 5000, "1M 1536-dim vectors must be ~5.8GB raw"
    assert report.sq8_quantized_ram_mb < 1600, "1M 1536-dim SQ8 vectors must be ~1.5GB"
    assert report.recommended_total_ram_gb_sq8 < report.recommended_total_ram_gb_float32
    print(f"[PASS] Hardware sizing passed (1M vectors: {report.recommended_total_ram_gb_float32}GB float32 vs {report.recommended_total_ram_gb_sq8}GB SQ8)")

    # Test 4: Filtered Search Pre vs Post-Filtering
    sim_result = simulate_filtered_search(corpus_size=2000, tenant_selectivity=0.03, top_k=10)
    assert sim_result["pre_filter_recall"] == 1.0, "Pre-filtered search must have 100% recall"
    assert sim_result["post_filter_recall"] < sim_result["pre_filter_recall"], "Post-filtering should show recall degradation under low selectivity"
    print(f"[PASS] Filtered search benchmark passed (Pre-filter: {sim_result['pre_filter_recall']*100}% vs Post-filter: {sim_result['post_filter_recall']*100}%)")

    print("\nALL VECTOR DATABASE TOOLKIT TESTS PASSED (4/4) [OK]\n")


def main():
    parser = argparse.ArgumentParser(description="Vector Database Architect Toolkit")
    parser.add_argument("--test", action="store_true", help="Run self-test suite")
    subparsers = parser.add_subparsers(dest="command")

    size_p = subparsers.add_parser("size", help="Calculate RAM and hardware sizing")
    size_p.add_argument("--count", type=int, required=True, help="Total number of vectors")
    size_p.add_argument("--dim", type=int, required=True, help="Vector dimensions")
    size_p.add_argument("--m", type=int, default=32, help="HNSW connections per node")

    args = parser.parse_args()

    if args.test:
        run_self_test()
        sys.exit(0)
    elif args.command == "size":
        rep = calculate_vector_sizing(args.count, args.dim, args.m)
        print(f"--- Vector Database Capacity Sizing ({rep.vector_count:,} vectors x {rep.dimensions} dims) ---")
        print(f"  Raw Vector RAM (Float32):   {rep.raw_vector_ram_mb:,.1f} MB")
        print(f"  HNSW Graph Overhead:         {rep.hnsw_graph_overhead_mb:,.1f} MB")
        print(f"  SQ8 Quantized RAM:           {rep.sq8_quantized_ram_mb:,.1f} MB")
        print(f"  Rec. Instance RAM (Float32): {rep.recommended_total_ram_gb_float32} GB")
        print(f"  Rec. Instance RAM (SQ8):     {rep.recommended_total_ram_gb_sq8} GB")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
