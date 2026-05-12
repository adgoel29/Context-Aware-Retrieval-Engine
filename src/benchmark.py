import json
from pathlib import Path
from tabulate import tabulate
from src.pipeline import RAGPipeline


BENCHMARK_QUERIES = [
    # "How does the system handle peak load?",
    # "What happens when a service becomes unavailable?",
    "How is data consistency maintained across nodes?",
    # "What mechanisms prevent the system from being overwhelmed by requests?",
    # "How does the system recover from failures?",
]


class BenchmarkRunner:

    def __init__(self, pipeline: RAGPipeline, output_dir: str = "outputs/"):
        self._pipeline = pipeline
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, queries: list, top_k: int = 3) -> list:
        results = []
        for query in queries:
            print(f"  Running: {query[:60]}...")
            comparison = self._pipeline.compare(query, top_k)
            results.append(comparison)
        return results

    def to_json(self, results: list, filepath: str) -> None:
        with open(filepath, "w",encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    def to_markdown(self, results: list, filepath: str) -> None:
        lines = [
            "# Retrieval Benchmark: Strategy A vs Strategy B\n",
            "**Strategy A** — raw query embedding search  \n",
            "**Strategy B** — LLM query expansion → embedding search\n\n",
            "---\n",
        ]

        summary_rows = []

        for item in results:
            query = item["query"]
            a_results = item["strategy_a"]["results"]
            b_results = item["strategy_b"]["results"]
            expanded = item["strategy_b"].get("expanded_query", "N/A")

            lines.append(f"## Query: *{query}*\n")
            lines.append(f"**Expanded (B):** {expanded}\n\n")

            # Side-by-side table
            rows = []
            for i in range(max(len(a_results), len(b_results))):
                a = a_results[i] if i < len(a_results) else {}
                b = b_results[i] if i < len(b_results) else {}
                rows.append([
                    i + 1,
                    a.get("metadata", {}).get("topic", "-"),
                    f"{a.get('score', 0):.4f}",
                    b.get("metadata", {}).get("topic", "-"),
                    f"{b.get('score', 0):.4f}",
                ])

            table = tabulate(
                rows,
                headers=["Rank", "A — Topic", "A Score", "B — Topic", "B Score"],
                tablefmt="pipe",
            )
            lines.append(table + "\n\n")

            summary_rows.append([
                query[:45] + "...",
                len(item["overlap"]),
                len(item["unique_to_a"]),
                len(item["unique_to_b"]),
            ])

        # Summary table
        lines.append("\nSummary\n")
        lines.append(tabulate(
            summary_rows,
            headers=["Query", "Overlap", "Unique to A", "Unique to B"],
            tablefmt="pipe",
        ))
        lines.append("\n")

        with open(filepath, "w",encoding="utf-8") as f:
            f.write("\n".join(lines))

    def generate_report(self, queries: list = None, top_k: int = 3) -> None:
        queries = queries or BENCHMARK_QUERIES
        print("\n Running Benchmark ")
        results = self.run(queries, top_k)

        json_path = self._output_dir / "benchmark.json"
        md_path = self._output_dir / "retrieval_benchmark.md"

        self.to_json(results, json_path)
        self.to_markdown(results, md_path)

        print(f"JSON  ={json_path}")
        print(f"MD    ={md_path}")