# requests.py
from pydantic import BaseModel
from typing import Optional, List

class DailyGoalsRequest(BaseModel):
    userId: int

class RoadmapAssistRequest(BaseModel):
    userId: int
    topic: str
    description: Optional[str] = None
    existingKnowledge: Optional[List[str]] = None

class NoteAssistRequest(BaseModel):
    userId: int
    content: str
    title: Optional[str] = None
    desktopId: Optional[int] = None

# responses.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Goal(BaseModel):
    id: Optional[str] = None
    type: str  # "roadmap_step" | "note_review" | "new_note" | "roadmap_creation"
    title: str
    description: str
    priority: str  # "high" | "medium" | "low"
    estimatedTime: int
    relatedContent: Optional[Dict[str, Any]] = None
    reasoning: str

class DailyGoalsResponse(BaseModel):
    goals: List[Goal]
    summary: Dict[str, Any]

class RoadmapStep(BaseModel):
    order: int
    title: str
    description: str
    estimatedTime: Optional[int] = None
    prerequisites: Optional[List[str]] = None
    learningObjectives: List[str]

class SuggestedRoadmap(BaseModel):
    title: str
    description: str
    steps: List[RoadmapStep]

class RoadmapAssistResponse(BaseModel):
    suggestedRoadmap: SuggestedRoadmap
    reasoning: str
    relatedNotes: List[int]

class NoteAssistResponse(BaseModel):
    suggestions: Dict[str, Any]