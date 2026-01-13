from typing import List, Dict, Any
from app.services.llm_service import LLMService
from app.services.database_service import DatabaseService
from datetime import datetime, timedelta

class RecommendationService:
    """Service for generating AI recommendations"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.db_service = DatabaseService()
    
    async def generate_daily_goals(
        self,
        user_id: int,
        auth_token: str
    ) -> List[Dict[str, Any]]:
        """Generate daily study goals for user"""
        
        # Fetch user context
        context = await self.db_service.get_user_context(user_id, auth_token)
        stats = await self.db_service.get_user_stats(user_id, auth_token)
        
        # Prepare prompt
        system_prompt = """You are an AI tutor helping students with their learning. 
        Analyze the user's study data and suggest 3-5 daily goals that are:
        1. Specific and actionable
        2. Based on their incomplete roadmaps and recent notes
        3. Appropriate for a single study session (30-120 minutes total)
        4. Prioritized by importance and urgency
        
        Return a JSON array of goals with this structure:
        {
            "goals": [
                {
                    "type": "roadmap_step" | "note_review" | "new_note" | "roadmap_creation",
                    "title": "Goal title",
                    "description": "Detailed description",
                    "priority": "high" | "medium" | "low",
                    "estimatedTime": 30,
                    "relatedContent": {
                        "roadmapId": 1,
                        "stepId": 2
                    },
                    "reasoning": "Why this goal is suggested"
                }
            ]
        }"""
        
        user_prompt = f"""User's study context:
        - Total notes: {stats['totalNotes']}
        - Total roadmaps: {stats['totalRoadmaps']}
        - Completion rate: {stats['completionRate']:.1%}
        
        Incomplete roadmap steps:
        {self._format_incomplete_steps(context.get('roadmaps', []))}
        
        Recent notes (last 7 days):
        {self._format_recent_notes(context.get('notes', []))}
        
        Suggest daily goals for today."""
        
        response = await self.llm_service.generate_structured_response(
            user_prompt,
            system_prompt=system_prompt
        )
        
        return response.get("goals", [])
    
    async def assist_roadmap_creation(
        self,
        user_id: int,
        topic: str,
        description: Optional[str],
        auth_token: str
    ) -> Dict[str, Any]:
        """Assist in creating a roadmap for a topic"""
        
        context = await self.db_service.get_user_context(user_id, auth_token)
        
        system_prompt = """You are an AI tutor helping create learning roadmaps.
        Create a structured learning roadmap that breaks down a topic into manageable steps.
        Each step should be:
        1. Clear and specific
        2. Build upon previous steps
        3. Include learning objectives
        4. Have estimated time if possible
        
        Return JSON with this structure:
        {
            "suggestedRoadmap": {
                "title": "Roadmap title",
                "description": "Overview",
                "steps": [
                    {
                        "order": 1,
                        "title": "Step title",
                        "description": "What to learn",
                        "estimatedTime": 60,
                        "prerequisites": ["topic1", "topic2"],
                        "learningObjectives": ["objective1", "objective2"]
                    }
                ]
            },
            "reasoning": "Why this structure",
            "relatedNotes": [1, 2, 3]
        }"""
        
        user_prompt = f"""Create a learning roadmap for:
        Topic: {topic}
        Description: {description or 'No description provided'}
        
        User's existing knowledge (from their notes):
        {self._format_user_knowledge(context.get('notes', []))}
        
        Suggest a comprehensive roadmap."""
        
        response = await self.llm_service.generate_structured_response(
            user_prompt,
            system_prompt=system_prompt
        )
        
        return response
    
    async def assist_note_creation(
        self,
        user_id: int,
        content: str,
        title: Optional[str],
        auth_token: str
    ) -> Dict[str, Any]:
        """Assist in creating/improving a note"""
        
        context = await self.db_service.get_user_context(user_id, auth_token)
        
        system_prompt = """You are an AI tutor helping improve study notes.
        Analyze the note content and provide suggestions for:
        1. Better title (if missing or unclear)
        2. Improved content structure
        3. Relevant tags based on content
        4. Related notes from user's collection
        5. Content gaps or areas needing more detail
        
        Return JSON with this structure:
        {
            "suggestions": {
                "title": "Suggested title",
                "improvedContent": "Improved content (if significant changes)",
                "suggestedTags": ["tag1", "tag2"],
                "relatedNotes": [
                    {
                        "id": 1,
                        "title": "Note title",
                        "relevance": 0.85,
                        "reason": "Why it's related"
                    }
                ],
                "contentGaps": ["gap1", "gap2"],
                "improvements": [
                    {
                        "type": "structure" | "clarity" | "completeness",
                        "suggestion": "What to improve",
                        "location": "Where in content"
                    }
                ]
            }
        }"""
        
        user_prompt = f"""Analyze this note:
        Title: {title or 'No title'}
        Content: {content}
        
        User's existing notes for context:
        {self._format_notes_summary(context.get('notes', []))}
        
        Provide suggestions."""
        
        response = await self.llm_service.generate_structured_response(
            user_prompt,
            system_prompt=system_prompt
        )
        
        return response.get("suggestions", {})
    
    def _format_incomplete_steps(self, roadmaps: List[Dict]) -> str:
        """Format incomplete roadmap steps for prompt"""
        result = []
        for roadmap in roadmaps:
            incomplete = [s for s in roadmap.get("steps", []) if not s.get("isCompleted", False)]
            if incomplete:
                result.append(f"\n{roadmap['title']}:")
                for step in incomplete:
                    result.append(f"  - Step {step['order']}: {step['title']}")
        return "\n".join(result) if result else "No incomplete steps"
    
    def _format_recent_notes(self, notes: List[Dict], days: int = 7) -> str:
        """Format recent notes for prompt"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [
            n for n in notes
            if datetime.fromisoformat(n["createdAt"].replace("Z", "+00:00")) > cutoff
        ]
        return "\n".join([f"- {n['title']}" for n in recent[:10]]) if recent else "No recent notes"
    
    def _format_user_knowledge(self, notes: List[Dict]) -> str:
        """Format user's knowledge from notes"""
        topics = {}
        for note in notes:
            tags = [t["tag"]["name"] for t in note.get("tags", [])]
            for tag in tags:
                topics[tag] = topics.get(tag, 0) + 1
        
        return ", ".join([f"{topic} ({count} notes)" for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]])
    
    def _format_notes_summary(self, notes: List[Dict]) -> str:
        """Format notes summary for prompt"""
        return "\n".join([
            f"- [{n['id']}] {n['title']}: {n['content'][:100]}..."
            for n in notes[:20]
        ])