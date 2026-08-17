import asyncio
import httpx
from app.main import app
from app.services.catalog import catalog_service


async def run_tests():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        print("1. Testing /health...")
        r_health = await client.get("/health")
        assert r_health.status_code == 200, f"Health check failed: {r_health.text}"
        print("   Health response:", r_health.json())

        print("\n2. Testing /api/v1/market/top-five...")
        r_top = await client.get("/api/v1/market/top-five")
        assert r_top.status_code == 200, f"Top five failed: {r_top.text}"
        top_models = r_top.json()
        assert len(top_models) == 5, f"Expected 5 models, got {len(top_models)}"

        print("   Top 5 models (LMSYS Chatbot Arena Leaderboard):")
        for m in top_models:
            rank = m["market_rank"]
            provider = m["provider"]
            model_name = m["model"]
            model_id = m["model_id"]
            p_in = m["input_per_million"]
            p_out = m["output_per_million"]
            bench_src = m.get("benchmark_source")
            bench_score = m.get("benchmark_score")
            print(f"     #{rank} [{provider}] {model_name} ({model_id}) - IN: ${p_in:.2f}, OUT: ${p_out:.2f} | {bench_src} ({bench_score})")

        providers = {m["provider"] for m in top_models}
        print("\n   Providers in Top 5:", sorted(list(providers)))
        assert "Anthropic" in providers, "Anthropic should be in top 5"
        assert "OpenAI" in providers, "OpenAI should be in top 5"
        assert "Google" in providers, "Google should be in top 5"
        assert "DeepSeek" in providers, "DeepSeek should be in top 5"
        assert "Meta" in providers, "Meta should be in top 5"

        print("\n3. Testing /api/v1/catalog...")
        r_cat = await client.get("/api/v1/catalog")
        assert r_cat.status_code == 200
        cat_data = r_cat.json()
        assert len(cat_data["models"]) > 0
        print(f"   Total catalog models: {len(cat_data['models'])}")

        print("\n4. Testing /api/v1/catalog/estimate...")
        r_est = await client.post("/api/v1/catalog/estimate", json={
            "input_tokens": 1000000,
            "output_tokens": 500000,
            "calls_per_month": 10,
            "model_ids": [top_models[0]["id"], top_models[1]["id"]]
        })
        assert r_est.status_code == 200
        print("   Estimate lines:", r_est.json())

    print("\n[OK] ALL TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_tests())
