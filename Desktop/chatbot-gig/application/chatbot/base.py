from typing import Optional
from pydantic import BaseModel,Field
from enum import Enum

class Intent(str, Enum):
    create_post = "create_post"
    create_listing = "create_listing"
    upgrade_post_to_ad = "upgrade_post_to_ad"
    resume_payment = "resume_payment"
    boost_ad = "boost_ad"
    search_inventory = "search_inventory"
    ask_analytics = "ask_analytics"
    smalltalk = "smalltalk"

    # Admin intents
    admin_add_example = "admin_add_example"
    admin_list_low_conf = "admin_list_low_conf"
    admin_retrain = "admin_retrain"
    admin_test_query = "admin_test_query"


class Entities(BaseModel):
    location: Optional[str] = None
    price: Optional[float] = None
    price_per: Optional[str] = None
    date_validity: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    category: Optional[str] = None


class ResponseFormatter(BaseModel):
    """Chatbot response model"""

    intent: Intent = Field(
        ...,
        description=(
            "The predicted intent of the user message. "
            "Must be one of the predefined intents in the Intent enum "
            "(e.g., create_post, create_listing, boost_ad, admin_retrain, etc.)."
        )
    )

    # Closed schema: additionalProperties = false (OK for OpenAI structured outputs)
    entities: Entities = Field(
        default_factory=Entities,
        description="Structured entities; all fields optional. Empty object if none."
    )

    bot_message: str = Field(
        ...,
        description=(
            "A natural language response the bot will send back to the user. "
        )
    )

    uploading_required: bool = Field(
        default=False,
        description="Whether the user must upload a file (e.g., for create_post or create_listing)."
    )
    verified_by_user: bool = Field(
        default=False,
        description="Whether the user has verified the output to be submitted to ."
    )


class ChatRequest(BaseModel):
    message:str
    session_id: Optional[str] = None   # first-time users may not provide this
