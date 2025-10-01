"""
Filter Builder Tools for LangChain Agent
========================================

Helper functions for building intelligent filters that combine user preferences with search criteria.
These functions are called by the agent to generate filters for Pinecone API searches.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

def build_default_user_filter(user_id: str) -> Dict[str, Any]:
    """Build a base filter from user's profile preferences (allergies, dietary preferences, budget)."""
    try:
        logger.info(f"Building default filter for user: {user_id}")
        
        base_filter = {
            "description": f"Base filter template for user {user_id}",
            "user_profile": {
                "milk_allergy": False,
                "eggs_allergy": False,
                "peanuts_allergy": False,
                "tree_nuts_allergy": False,
                "shellfish_allergy": False,
                "other_allergies": [],
                "dietary_preferences": [],
                "user_identity": "student",
                "budget": None
            },
            "instructions": "Replace the placeholder values with actual user profile data from get_item result. The agent will transform user_identity + budget into the appropriate price field filter."
        }
        
        return base_filter
        
    except Exception as e:
        logger.error(f"Failed to build default user filter: {e}")
        return {"error": f"Failed to build default user filter: {str(e)}"}

def build_food_search_filter(
    base_filter: Dict[str, Any],
    search_criteria: Dict[str, Any],
    use_base_filter: bool = True,
    override_preferences: bool = False
) -> Dict[str, Any]:
    """Build a final search filter by combining base user filter with search-specific criteria."""
    try:
        logger.info(f"Building food search filter - use_base_filter: {use_base_filter}, override_preferences: {override_preferences}")
        logger.info(f"Search criteria: {search_criteria}")
        
        final_filter = {}
        
        if use_base_filter and base_filter:
            user_profile = base_filter.get("user_profile", {})
            
            # ALWAYS apply allergy filters from base filter (safety first)
            if user_profile.get("milk_allergy"):
                final_filter["milk_allergy"] = {"$eq": False}
            if user_profile.get("eggs_allergy"):
                final_filter["eggs_allergy"] = {"$eq": False}
            if user_profile.get("peanuts_allergy"):
                final_filter["peanuts_allergy"] = {"$eq": False}
            if user_profile.get("tree_nuts_allergy"):
                final_filter["tree_nuts_allergy"] = {"$eq": False}
            if user_profile.get("shellfish_allergy"):
                final_filter["shellfish_allergy"] = {"$eq": False}
            
            # ALWAYS apply other allergies filter
            other_allergies = user_profile.get("other_allergies", [])
            if other_allergies:
                final_filter["other_allergies"] = {"$nin": other_allergies}
            
            # Apply dietary preferences (can be overridden)
            if not override_preferences or "dietary_preferences" not in search_criteria:
                dietary_preferences = user_profile.get("dietary_preferences", [])
                if dietary_preferences:
                    final_filter["dietary_preferences"] = {"$in": dietary_preferences}
            
            # Apply budget (can be overridden)
            if not override_preferences or "max_price" not in search_criteria:
                user_identity = user_profile.get("user_identity", "student")
                budget = user_profile.get("budget")
                
                if budget is not None:
                    if user_identity == "student":
                        final_filter["student_price"] = {"$lte": budget}
                    elif user_identity == "staff":
                        final_filter["staff_price"] = {"$lte": budget}
        
        # Add search-specific criteria (these can override base preferences)
        if search_criteria:
            # Handle cuisine type
            if "cuisine_type" in search_criteria:
                final_filter["cuisine_type"] = {"$in": search_criteria["cuisine_type"]}
            
            # Handle price override
            if "max_price" in search_criteria:
                user_identity = base_filter.get("user_profile", {}).get("user_identity", "student")
                if user_identity == "student":
                    final_filter["student_price"] = {"$lte": search_criteria["max_price"]}
                elif user_identity == "staff":
                    final_filter["staff_price"] = {"$lte": search_criteria["max_price"]}
            
            # Handle dietary preferences override
            if "dietary_preferences" in search_criteria:
                final_filter["dietary_preferences"] = {"$in": search_criteria["dietary_preferences"]}
            
            # Handle period plan override
            if "period_plan" in search_criteria:
                final_filter["_period_plan_override"] = search_criteria["period_plan"]
        
        logger.info(f"Final combined filter: {final_filter}")
        return final_filter
        
    except Exception as e:
        logger.error(f"Failed to build food search filter: {e}")
        return {"error": f"Failed to build food search filter: {str(e)}"}

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Filter Builder Tools")
    print("=" * 50)
    
    # Test 1: Build default user filter
    print("\n1. Building default user filter:")
    base_filter = build_default_user_filter("test_user_123")
    print(f"Base filter structure: {base_filter}")
    
    # Test 2: Build search filter with REAL user profile data
    print("\n2. Building search filter with REAL user profile data:")
    
    # Real DynamoDB user profile data (from agent output)
    real_user_profile = {
        "Item": {
            "budget": {"N": "15"},
            "dietary_preferences": {"S": "vegetarian"},
            "eggs_allergy": {"BOOL": True},
            "email": {"S": "test@example.com"},
            "milk_allergy": {"BOOL": True},
            "other_allergies": {
                "L": [
                    {"S": "banana"},
                    {"S": "noodles"}
                ]
            },
            "peanuts_allergy": {"BOOL": True},
            "shellfish_allergy": {"BOOL": True},
            "tree_nuts_allergy": {"BOOL": False},
            "user_id": {"S": "test_user_123"},
            "user_identity": {"S": "student"},
            "user_name": {"S": "Leslie"},
            "period_plan": {"S": "I always want to eat hot food"}
        }
    }
    
    # Convert DynamoDB format to flat structure for filter building
    search_query_filter = {
        "budget": float(real_user_profile["Item"]["budget"]["N"]),
        "dietary_preferences": [real_user_profile["Item"]["dietary_preferences"]["S"]],
        "eggs_allergy": real_user_profile["Item"]["eggs_allergy"]["BOOL"],
        "milk_allergy": real_user_profile["Item"]["milk_allergy"]["BOOL"],
        "other_allergies": [item["S"] for item in real_user_profile["Item"]["other_allergies"]["L"]],
        "peanuts_allergy": real_user_profile["Item"]["peanuts_allergy"]["BOOL"],
        "shellfish_allergy": real_user_profile["Item"]["shellfish_allergy"]["BOOL"],
        "tree_nuts_allergy": real_user_profile["Item"]["tree_nuts_allergy"]["BOOL"],
        "user_identity": real_user_profile["Item"]["user_identity"]["S"],
        "period_plan": real_user_profile["Item"]["period_plan"]["S"]
    }
    
    # Create base filter with real data
    real_base_filter = {
        "description": f"Base filter for user {search_query_filter['user_identity']}",
        "user_profile": search_query_filter
    }
    
    print(f"Search query filter: {search_query_filter}")
    
    # Test with search criteria
    search_criteria = {
        "cuisine_type": ["Indian"],
        "max_price": 8.0
    }
    final_filter = build_food_search_filter(real_base_filter, search_criteria, use_base_filter=True)
    print(f"Final filter with real data: {final_filter}")
    
    # Test 3: Build search filter without base filter (for friend)
    print("\n3. Building search filter without base filter (for friend):")
    friend_criteria = {
        "cuisine_type": ["Chinese"]
    }
    friend_filter = build_food_search_filter(real_base_filter, friend_criteria, use_base_filter=False)
    print(f"Friend filter: {friend_filter}")
    
    # Test 4: Build search filter with override_preferences=True
    print("\n4. Building search filter with override_preferences=True:")
    override_search_criteria = {
        "cuisine_type": ["Italian"],
        "max_price": 10.0,
        "dietary_preferences": ["vegan"]
    }
    override_filter = build_food_search_filter(real_base_filter, override_search_criteria, use_base_filter=True, override_preferences=True)
    print(f"Override filter: {override_filter}")
    
    print("\n✅ Filter builder testing completed!")