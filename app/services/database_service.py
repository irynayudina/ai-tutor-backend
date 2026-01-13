import httpx
from typing import Dict, Any, Optional
from app.config import settings

class DatabaseService:
    """Service to fetch user data from NestJS backend"""
    
    def __init__(self):
        self.nestjs_url = settings.nestjs_api_url
        self.graphql_url = settings.nestjs_graphql_url
    
    async def get_user_context(
        self, 
        user_id: int, 
        auth_token: str
    ) -> Dict[str, Any]:
        """Fetch user's notes, roadmaps, and desktops from NestJS"""
        
        # GraphQL query to get user context
        query = """
        query GetUserStudyContext($userId: Int!) {
            notes(userId: $userId) {
                id
                title
                content
                createdAt
                updatedAt
                tags {
                    tag {
                        id
                        name
                    }
                }
            }
            roadmaps(userId: $userId) {
                id
                title
                description
                createdAt
                updatedAt
                steps {
                    id
                    title
                    description
                    order
                    isCompleted
                    createdAt
                }
            }
            desktops(userId: $userId) {
                id
                name
                description
            }
        }
        """
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.graphql_url,
                json={
                    "query": query,
                    "variables": {"userId": user_id}
                },
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to fetch user context: {response.status_code}")
            
            data = response.json()
            if "errors" in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            return data["data"]
    
    async def get_user_stats(
        self,
        user_id: int,
        auth_token: str
    ) -> Dict[str, Any]:
        """Get user statistics for analysis"""
        context = await self.get_user_context(user_id, auth_token)
        
        notes = context.get("notes", [])
        roadmaps = context.get("roadmaps", [])
        
        total_steps = sum(len(r.get("steps", [])) for r in roadmaps)
        completed_steps = sum(
            sum(1 for s in r.get("steps", []) if s.get("isCompleted", False))
            for r in roadmaps
        )
        
        return {
            "totalNotes": len(notes),
            "totalRoadmaps": len(roadmaps),
            "totalSteps": total_steps,
            "completedSteps": completed_steps,
            "completionRate": completed_steps / total_steps if total_steps > 0 else 0
        }