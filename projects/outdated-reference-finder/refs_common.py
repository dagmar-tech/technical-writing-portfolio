"""Shared helpers for the outdated-references demo."""


def iter_locations(page):
    """Yield (location, text) for every searchable text field of a page."""
    yield "title", page.get("title", "")
    yield "body", page.get("body", "")
    for attachment in page.get("attachments", []):
        yield f"attachment:{attachment['filename']}", attachment.get("text", "")


def set_location(page, location, new_text):
    """Replace the text stored at a location (as produced by iter_locations)."""
    if location == "title":
        page["title"] = new_text
    elif location == "body":
        page["body"] = new_text
    elif location.startswith("attachment:"):
        filename = location.split(":", 1)[1]
        for attachment in page.get("attachments", []):
            if attachment["filename"] == filename:
                attachment["text"] = new_text
                return
        raise KeyError(location)
    else:
        raise KeyError(location)
