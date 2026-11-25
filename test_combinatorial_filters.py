"""
Test script for 3-Way Combinatorial Filters (Region, Category, Date, Article Type, Search).
"""

from fastapi.testclient import TestClient
from app.main import app


def test_filters():
    print("=" * 65)
    print(" WorldGames AI - Combinatorial Multi-Filters Diagnostic")
    print("=" * 65)

    with TestClient(app) as client:
        # 1. Total Feed
        res_all = client.get("/api/v1/publish/feed")
        assert res_all.status_code == 200
        total = res_all.json().get("total")
        print(f"[*] Total published items: {total}")

        # 2. Filter by Article Type (PLAYBOOK vs NEWS)
        print("[*] Testing Filter: article_type='PLAYBOOK'...")
        res_pb = client.get("/api/v1/publish/feed?article_type=PLAYBOOK")
        assert res_pb.status_code == 200
        pb_count = res_pb.json().get("total")
        print(f"    Total Playbooks: {pb_count}")

        print("[*] Testing Filter: article_type='NEWS'...")
        res_news = client.get("/api/v1/publish/feed?article_type=NEWS")
        assert res_news.status_code == 200
        news_count = res_news.json().get("total")
        print(f"    Total News: {news_count}")
        assert pb_count + news_count == total

        # 3. Filter by Region (South Asia)
        print("[*] Testing Filter: region='South Asia'...")
        res_reg = client.get("/api/v1/publish/feed?region=South%20Asia")
        assert res_reg.status_code == 200
        reg_count = res_reg.json().get("total")
        print(f"    South Asia count: {reg_count}")

        # 4. Filter by Category (Combat Sports & Martial Arts)
        print("[*] Testing Filter: category='Combat Sports & Martial Arts'...")
        res_cat = client.get("/api/v1/publish/feed?category=Combat%20Sports%20%26%20Martial%20Arts")
        assert res_cat.status_code == 200
        cat_count = res_cat.json().get("total")
        print(f"    Combat Sports count: {cat_count}")

        # 5. Combinatorial Filter: Region='South Asia' AND article_type='NEWS'
        print("[*] Testing Combinatorial: region='South Asia' AND article_type='NEWS'...")
        res_comb = client.get("/api/v1/publish/feed?region=South%20Asia&article_type=NEWS")
        assert res_comb.status_code == 200
        comb_count = res_comb.json().get("total")
        print(f"    Matching items: {comb_count}")
        if comb_count > 0:
            item = res_comb.json().get("articles")[0]
            print(f"    -> Title: '{item.get('title')}' [Type: {item.get('article_type')}]")

        # 6. Search Filter
        print("[*] Testing Search: 'Hurling'...")
        res_srch = client.get("/api/v1/publish/feed?search=Hurling")
        assert res_srch.status_code == 200
        print(f"    Search matches: {res_srch.json().get('total')}")

    print("\n[+] All Combinatorial Filtering tests passed successfully!")
    print("=" * 65)


if __name__ == "__main__":
    test_filters()
