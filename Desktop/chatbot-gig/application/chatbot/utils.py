import uuid

def ensure_session_id(session_id: str | None) -> str:
    try:
        # Check if provided value is a valid UUID
        if session_id and session_id.strip() != "":
            uuid.UUID(session_id) 
            return session_id 
    except (ValueError, AttributeError, TypeError):
        pass

    # If invalid or missing, generate a new one
    return str(uuid.uuid4())

import json

def normalize_post_payload(raw_data: dict | str) -> dict:
    """
    Normalize input into valid Postersz API `Post` schema.
    """

    # Convert JSON string → dict
    if isinstance(raw_data, str):
        raw_data = json.loads(raw_data)

    # Fix categoryArray schema
    normalized_category = []
    for cat in raw_data.get("categoryArray", []):
        normalized_category.append({
            "type": cat.get("type", "2"),
            "industry": cat.get("industry", ""),
            "category": cat.get("category", ""),
            "subcategory": cat.get("subcategory", ""),
            "subsubcategory": cat.get("subsubcategory", ""),
            "keywords1": cat.get("keywords1", ""),
            "keywords2": cat.get("keywords2", ""),
            "keywords3": cat.get("keywords3", ""),
            "keywords4": cat.get("keywords4", ""),
            "keywords5": cat.get("keywords5", ""),
            "keywords6": cat.get("keywords6", ""),
            "keywords7": cat.get("keywords7", ""),
            "keywords8": cat.get("keywords8", ""),
            "tab_label_option_posts": cat.get("tab_label_option_posts", ""),
            "tab_label_option_company": cat.get("tab_label_option_company", ""),
            "tab_label_option_looking_for": cat.get("tab_label_option_looking_for", ""),
            "pills": cat.get("pills", [])
        })

    final = {
            "image": raw_data.get("image", ""),
            "company_name": raw_data.get("company_name", ""),
            "email_addresses": raw_data.get("email_addresses", []),
            "phone_numbers": raw_data.get("phone_numbers", []),
            "post_locations": raw_data.get("post_locations", []),
            "categoryArray": normalized_category,
            "community": raw_data.get("community", ""),
            "website_link": raw_data.get("website_link", ""),
            "keywords": raw_data.get("keywords", []),
            "date": raw_data.get("date", ""),
            "instagram": raw_data.get("instagram", ""),
            "owner": raw_data.get("owner", ""),
            "title": raw_data.get("title", ""),
            "info": raw_data.get("info", ""),
            "service_area": raw_data.get("service_area", []),
            "address": raw_data.get("address", ""),
            "company_branches": raw_data.get("company_branches", []),
            "company_service_areas": raw_data.get("company_service_areas", [])
        }
    return final