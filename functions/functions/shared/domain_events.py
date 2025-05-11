from pydantic import BaseModel, EmailStr, Field
from typing import Any

from functions.models.sync_profile import SyncProfile


class DomainEvent(BaseModel):
    """Base class for all domain/application events."""

    pass


class UserCreated(DomainEvent):
    """Published when a new user is detected."""

    user_id: str = Field(..., description="The unique ID of the newly created user.")
    email: str | None = Field(None, description="The user's email, if available.")
    display_name: str | None = Field(
        None, description="The user's display name, if available."
    )
    provider_id: str | None = Field(
        None, description="The primary auth provider ID (e.g., 'google.com')."
    )


class SyncProfileCreated(DomainEvent):
    """Published when a new sync profile is created."""

    user_id: str = Field(..., description="The ID of the user who owns the profile.")
    sync_profile_id: str = Field(
        ..., description="The ID of the newly created sync profile."
    )


class SyncFailed(DomainEvent):
    """Published when a synchronization fails."""

    user_id: str = Field(..., description="The ID of the user.")
    sync_profile_id: str = Field(..., description="The ID of the sync profile.")

    error_type: str = Field(..., description="The type/class name of the error.")
    error_message: str = Field(
        ..., description="Description of the synchronization error."
    )
    formatted_traceback: str | None = Field(
        None, description="The full error traceback if available."
    )


class IcsFetched(DomainEvent):
    """Published when ICS content has been successfully fetched from a source."""

    ics_str: str = Field(..., description="The raw ICS content as a string.")

    # Metadata passed down from the caller (e.g., sync_profile_id, user_id)
    metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata associated with the fetch."
    )


class SyncSucceeded(DomainEvent):
    """Published when a synchronization succeeds."""

    user_id: str = Field(..., description="The ID of the user.")
    sync_profile_id: str = Field(..., description="The ID of the sync profile.")


class SyncProfileCreationFailed(DomainEvent):
    """Published when a sync profile creation fails."""

    user_id: str = Field(..., description="The ID of the user.")
    error_type: str = Field(..., description="The type/class name of the error.")
    error_message: str = Field(..., description="Description of the creation error.")
    formatted_traceback: str | None = Field(
        None, description="The full error traceback if available."
    )


class SyncProfileDeletionFailed(DomainEvent):
    """Published when a sync profile deletion fails."""

    user_id: str = Field(..., description="The ID of the user.")
    sync_profile_id: str = Field(..., description="The ID of the sync profile.")
    error_type: str = Field(..., description="The type/class name of the error.")
    error_message: str = Field(..., description="Description of the deletion error.")
    formatted_traceback: str | None = Field(
        None, description="The full error traceback if available."
    )


class RulesetGenerationFailed(DomainEvent):
    """Published when a ruleset generation fails."""

    user_id: str = Field(..., description="The ID of the user.")
    sync_profile_id: str = Field(..., description="The ID of the sync profile.")
    error_type: str = Field(..., description="The type/class name of the error.")
    error_message: str = Field(..., description="Description of the generation error.")
    formatted_traceback: str | None = Field(
        None, description="The full error traceback if available."
    )
