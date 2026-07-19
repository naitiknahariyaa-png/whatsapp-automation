"""
Linear Integration - Issue Tracking
Connect WhatsApp to project management
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class LinearClient:
    """
    Linear Issue Tracker Client
    
    Perfect for:
    - Create issues from WhatsApp messages
    - Track bug reports
    - Team task management
    
    Setup:
    1. Sign up at https://linear.app
    2. Go to Settings → API → Create API Key
    3. Copy the API key
    4. Add to .env
    
    Environment:
    - LINEAR_API_KEY=lin_api_xxx
    """
    
    BASE_URL = "https://api.linear.app/graphql"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("LINEAR_API_KEY", "")
        self.enabled = bool(self.api_key)
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key
        }
        
        if self.enabled:
            logger.info("✅ Linear configured")
        else:
            logger.warning("⚠️ Linear not configured (set LINEAR_API_KEY)")
    
    def _query(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        """Execute GraphQL query"""
        if not self.enabled:
            return None
        
        try:
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                json={"query": query, "variables": variables or {}},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    logger.error(f"Linear errors: {data['errors']}")
                    return None
                return data.get("data")
            return None
            
        except Exception as e:
            logger.error(f"Linear request error: {e}")
            return None
    
    def get_teams(self) -> List[Dict]:
        """Get all teams"""
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                    key
                }
            }
        }
        """
        data = self._query(query)
        return data.get("teams", {}).get("nodes", []) if data else []
    
    def create_issue(
        self,
        title: str,
        team_id: str,
        description: Optional[str] = None,
        priority: int = 3,
        labels: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Create a new issue
        
        Args:
            title: Issue title
            team_id: Team ID (get from get_teams())
            description: Issue description
            priority: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
            labels: List of label names
        """
        mutation = """
        mutation CreateIssue($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    url
                }
            }
        }
        """
        
        variables = {
            "input": {
                "title": title,
                "teamId": team_id,
                "priority": priority
            }
        }
        
        if description:
            variables["input"]["description"] = description
        
        data = self._query(mutation, variables)
        
        if data:
            return data.get("issueCreate", {}).get("issue")
        return None
    
    def create_bug_report(
        self,
        title: str,
        description: str,
        team_id: str,
        reporter: Optional[str] = None
    ) -> Optional[Dict]:
        """Create a bug report issue"""
        full_description = f"""
**Reported from WhatsApp Bot**

**Reporter:** {reporter or "Unknown"}

**Description:**
{description}
"""
        return self.create_issue(
            title=f"[Bug] {title}",
            team_id=team_id,
            description=full_description,
            priority=2,
            labels=["bug"]
        )
    
    def get_my_issues(self, status_filter: Optional[str] = None) -> List[Dict]:
        """
        Get issues assigned to current user
        
        Args:
            status_filter: Filter by status type (backlog, unstarted, started, completed, canceled)
        """
        filter_clause = ""
        if status_filter:
            filter_clause = f', state: {{ type: eq: "{status_filter}" }}'
        
        query = f"""
        query {{
            viewer {{
                assignedIssues(first: 50, filter: {{ {filter_clause} }}) {{
                    nodes {{
                        id
                        identifier
                        title
                        priority
                        priorityLabel
                        state {{
                            name
                            type
                        }}
                        url
                    }}
                }}
            }}
        }}
        """
        
        data = self._query(query)
        return data.get("viewer", {}).get("assignedIssues", {}).get("nodes", []) if data else []
    
    def update_issue_state(self, issue_id: str, state_id: str) -> bool:
        """Update issue state (move to different column)"""
        mutation = """
        mutation UpdateIssue($id: String!, $stateId: String!) {
            issueUpdate(id: $id, input: { stateId: $stateId }) {
                success
            }
        }
        """
        
        data = self._query(mutation, {"id": issue_id, "stateId": state_id})
        return data.get("issueUpdate", {}).get("success", False) if data else False
    
    def add_comment(self, issue_id: str, body: str) -> bool:
        """Add comment to issue"""
        mutation = """
        mutation CreateComment($issueId: String!, $body: String!) {
            commentCreate(input: { issueId: $issueId, body: $body }) {
                success
            }
        }
        """
        
        data = self._query(mutation, {"issueId": issue_id, "body": body})
        return data.get("commentCreate", {}).get("success", False) if data else False


def setup_linear():
    """Interactive setup for Linear"""
    print("\n" + "="*50)
    print("📋 Linear Issue Tracker Setup")
    print("="*50 + "\n")
    
    print("How to get Linear API Key:")
    print("1. Sign up at https://linear.app")
    print("2. Go to Settings → API → Create API Key")
    print("3. Name it 'WhatsApp Bot'")
    print("4. Copy the API key\n")
    
    api_key = input("Linear API Key (lin_api_xxx): ").strip()
    
    if api_key:
        with open(".env", "a") as f:
            f.write(f"\n# Linear Issue Tracker\n")
            f.write(f"LINEAR_API_KEY={api_key}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ API Key required!")


if __name__ == "__main__":
    setup_linear()
