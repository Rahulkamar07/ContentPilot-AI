from app.services.ai_pipeline import build_caption, summarize_text, vision_prompt_from_article
from app.services.rss_ingestion import _normalize_entry


def test_summarize_text_truncates_long_content() -> None:
    text = "word " * 200
    summary = summarize_text(text)
    assert len(summary) <= 280
    assert summary.startswith("word")


def test_build_caption_contains_category_hashtag() -> None:
    caption = build_caption("Major update", "Important product launch", "Tech News")
    assert "#technews" in caption
    assert "Major update" in caption


def test_vision_prompt_includes_context() -> None:
    prompt = vision_prompt_from_article("Title", "Summary", "science")
    assert "Title" in prompt
    assert "science" in prompt


def test_normalize_entry_extracts_basic_fields() -> None:
    entry = {
        "title": "Headline",
        "link": "https://example.com/article",
        "summary": "Summary text",
        "tags": [{"term": "World"}],
        "media_content": [{"url": "https://example.com/image.jpg"}],
    }

    normalized = _normalize_entry(entry, "general")

    assert normalized["title"] == "Headline"
    assert normalized["url"] == "https://example.com/article"
    assert normalized["category"] == "world"
    assert normalized["image_url"] == "https://example.com/image.jpg"
