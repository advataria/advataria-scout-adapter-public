#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spoločné Pydantic modely pre AdvaScout uAgenta a klienta.

Dôležité:
- TENTO súbor importuj v 01_adva_uagent_scout.py aj v 02_scout_client_test.py
- Tak bude schéma 100 % identická a digest sa určite zhodne.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ScoutRequest(BaseModel):
    """
    Input model: URL stránky, ktorú má AdvaScout spracovať.
    """
    url: str = Field(
        ...,
        description="Client website URL to analyze, e.g. https://example.com",
        min_length=4,
    )


class ScoutResponseClient(BaseModel):
    """
    Výstupná štruktúra pre sekciu 'client'.
    """
    url: str
    title: str
    meta: str
    headings: str
    top_text: str


class ScoutResponse(BaseModel):
    """
    Plný výstup uAgenta.
    """
    job_id: str
    client: ScoutResponseClient
    scraped_at: str
    status: str
    error: Optional[str] = None
