from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


@dataclass
class Context:
    user_id: str


class SourceItem(BaseModel):
    title: str
    url: str
    note: str


class ResearchReport(BaseModel):
    summary: str
    steps: List[str]
    sources: List[SourceItem]
    next_actions: List[str]


class AskRequest(BaseModel):
    user_id: str
    thread_id: str
    question: str


class InterveneRequest(BaseModel):
    thread_id: str
    user_id: str
    decisions: List[Dict[str, Any]]


class AgentResponse(BaseModel):
    status: str
    result: Optional[str] = None
    interrupt_details: Optional[Dict[str, Any]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    trace_id: Optional[str] = None
