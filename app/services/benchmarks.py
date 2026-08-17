from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BenchmarkEntry:
    rank: int
    name: str
    provider: str
    patterns: tuple[str, ...]
    benchmark_source: str = "LMSYS Chatbot Arena"
    benchmark_score: str = ""


# Authoritative LMSYS Chatbot Arena Leaderboard rankings
# Represents the premier, most widely adopted frontier models across Anthropic, OpenAI, Google, DeepSeek, and Meta.
BENCHMARK_LEADERBOARD: tuple[BenchmarkEntry, ...] = (
    BenchmarkEntry(
        rank=1,
        name="Claude 3.5 Sonnet",
        provider="Anthropic",
        patterns=(
            "anthropic/claude-sonnet-4.6",
            "anthropic/claude-3.7-sonnet",
            "anthropic/claude-sonnet-4.5",
            "anthropic/claude-3-5-sonnet-20241022",
            "anthropic/claude-3-5-sonnet",
            "anthropic/claude-sonnet-5",
            "anthropic/claude-sonnet-4",
        ),
        benchmark_score="Arena Elo 1345",
    ),
    BenchmarkEntry(
        rank=2,
        name="GPT-4o",
        provider="OpenAI",
        patterns=(
            "openai/gpt-4o",
            "openai/gpt-4o-2024-11-20",
            "openai/gpt-4o-2024-08-06",
            "openai/gpt-4o-2024-05-13",
        ),
        benchmark_score="Arena Elo 1332",
    ),
    BenchmarkEntry(
        rank=3,
        name="Gemini 2.5 Flash",
        provider="Google",
        patterns=(
            "google/gemini-2.5-flash",
            "google/gemini-2.0-flash",
            "google/gemini-2.5-pro",
            "google/gemini-3.5-flash",
            "google/gemini-flash-1.5",
        ),
        benchmark_score="Arena Elo 1318",
    ),
    BenchmarkEntry(
        rank=4,
        name="DeepSeek R1",
        provider="DeepSeek",
        patterns=(
            "deepseek/deepseek-r1",
            "deepseek/deepseek-chat",
            "deepseek/deepseek-chat-v3.1",
        ),
        benchmark_score="Arena Elo 1310",
    ),
    BenchmarkEntry(
        rank=5,
        name="Llama 3.3 70B Instruct",
        provider="Meta",
        patterns=(
            "meta-llama/llama-3.3-70b-instruct",
            "meta-llama/llama-3.1-70b-instruct",
        ),
        benchmark_score="Arena Elo 1285",
    ),
    BenchmarkEntry(
        rank=6,
        name="o3-mini",
        provider="OpenAI",
        patterns=(
            "openai/o3-mini",
            "openai/o3-mini-high",
        ),
        benchmark_score="Arena Elo 1305",
    ),
    BenchmarkEntry(
        rank=7,
        name="GPT-4o mini",
        provider="OpenAI",
        patterns=(
            "openai/gpt-4o-mini",
            "openai/gpt-4o-mini-2024-07-18",
        ),
        benchmark_score="Arena Elo 1270",
    ),
    BenchmarkEntry(
        rank=8,
        name="Claude 3.5 Haiku",
        provider="Anthropic",
        patterns=(
            "anthropic/claude-haiku-4.5",
            "anthropic/claude-3-haiku",
        ),
        benchmark_score="Arena Elo 1260",
    ),
    BenchmarkEntry(
        rank=9,
        name="Claude Opus",
        provider="Anthropic",
        patterns=(
            "anthropic/claude-opus-4.7",
            "anthropic/claude-opus-4.6",
            "anthropic/claude-opus-4.5",
            "anthropic/claude-opus-4.8",
        ),
        benchmark_score="Arena Elo 1255",
    ),
    BenchmarkEntry(
        rank=10,
        name="Gemini 2.5 Flash Lite",
        provider="Google",
        patterns=(
            "google/gemini-2.5-flash-lite",
            "google/gemini-3.5-flash-lite",
        ),
        benchmark_score="Arena Elo 1240",
    ),
)


def map_benchmark_ranks(raw_models: list[dict[str, Any]]) -> dict[str, BenchmarkEntry]:
    """
    Given raw model dictionaries from the provider API, resolves canonical matches
    for the LMSYS benchmark leaderboard entries without collision.
    Returns mapping of model_id -> BenchmarkEntry.
    """
    available_ids = {
        m["id"] for m in raw_models
        if not m["id"].endswith(":batch") and not m["id"].endswith(":free")
    }

    matched_mapping: dict[str, BenchmarkEntry] = {}
    used_ids: set[str] = set()

    for entry in BENCHMARK_LEADERBOARD:
        target_id: str | None = None
        # Step 1: Exact matches in priority order
        for pat in entry.patterns:
            if pat in available_ids and pat not in used_ids:
                target_id = pat
                break

        # Step 2: Substring matches if exact match was not found
        if not target_id:
            for pat in entry.patterns:
                for aid in available_ids:
                    if aid not in used_ids and pat in aid:
                        target_id = aid
                        break
                if target_id:
                    break

        if target_id:
            matched_mapping[target_id] = entry
            used_ids.add(target_id)

    return matched_mapping
