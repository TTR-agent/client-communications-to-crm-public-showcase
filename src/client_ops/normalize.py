PUBLIC_FIELDS = ("source", "speaker", "text", "timestamp")


def normalize_communications(raw_items):
    """Reduce calls, emails, and notes into a shared public-safe shape."""
    normalized = []
    for item in raw_items:
        text = item.get("text") or item.get("body") or item.get("notes") or item.get("transcript") or ""
        normalized.append(
            {
                "source": item.get("source", "unknown"),
                "speaker": item.get("speaker") or item.get("from") or "Unknown",
                "text": " ".join(text.split()),
                "timestamp": item.get("timestamp", ""),
            }
        )
    return normalized

