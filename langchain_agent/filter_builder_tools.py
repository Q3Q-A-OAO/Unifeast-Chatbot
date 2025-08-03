"""
Filter Builder Tools for LangChain Agent
========================================

Tools for building intelligent filters that combine user preferences with search criteria.
"""

import logging
from typing import Dict, List, Optional, Any
from langchain.tools import tool

logger = logging.getLogger(__name__)

@tool("build_default_user_filter")
def build_default_user_filter(user_id: str) -> Dict[str, Any]:
    """
    Build a base filter from user's profile preferences (allergies, dietary preferences, budget).
    This should be called once at the start of a conversation and stored in session memory.
    
    Args:
        user_id: The user's ID to retrieve their profile from DynamoDB
    
    Returns:
        Base filter dictionary with user's default preferences that should be applied to all searches
        unless explicitly overridden.
    
    Note: This tool should be used in combination with get_item to retrieve the user's profile first.
    The agent will transform user_identity + budget into the appropriate price field filter.
    """
    try:
        logger.info(f"Building default filter for user: {user_id}")
        
        # Return a template structure that the agent can fill in
        # The agent will replace these with actual values from the user's profile
        base_filter = {
            "description": f"Base filter template for user {user_id}",
            "user_profile": {
                "milk_allergy": False,  # Will be set based on user's milk_allergy
                "eggs_allergy": False,  # Will be set based on user's eggs_allergy
                "peanuts_allergy": False,  # Will be set based on user's peanuts_allergy
                "tree_nuts_allergy": False,  # Will be set based on user's tree_nuts_allergy
                "shellfish_allergy": False,  # Will be set based on user's shellfish_allergy
                "other_allergies": [],  # Will be set based on user's other_allergies
                "dietary_preferences": [],  # Will be set based on user's dietary_preferences
                "user_identity": "student",  # Will be "student" or "staff"
                "budget": None  # Will be set based on user's budget (None if no budget set)
            },
            "instructions": "Replace the placeholder values with actual user profile data from get_item result. The agent will transform user_identity + budget into the appropriate price field filter."
        }
        
        return base_filter
        
    except Exception as e:
        logger.error(f"Failed to build default user filter: {e}")
        return {"error": f"Failed to build default user filter: {str(e)}"}

@tool("build_food_search_filter")
def build_food_search_filter(
    base_filter: Dict[str, Any],
    search_criteria: Dict[str, Any],
    use_base_filter: bool = True
) -> Dict[str, Any]:
    """
    Build a final search filter by combining base user filter with search-specific criteria.
    
    Args:
        base_filter: The base filter from build_default_user_filter (user's preferences)
        search_criteria: New filters from the current search query (cuisine, price, etc.)
        use_base_filter: Whether to include the base filter (True) or ignore it (False)
    
    Returns:
        Combined filter dictionary ready for Pinecone search (flat structure)
    
    Example search_criteria:
        - {"cuisine_type": ["Indian", "Chinese"]}
        - {"max_price": 8.0}
        - {"dietary_preferences": ["vegetarian"]}
    
    Note: The agent should build search_criteria based on user's chat input.
    Location, period plan, category, and food type should be handled through semantic search.
    """
    try:
        logger.info(f"Building food search filter - use_base_filter: {use_base_filter}")
        logger.info(f"Search criteria: {search_criteria}")
        
        final_filter = {}
        
        if use_base_filter and base_filter:
            user_profile = base_filter.get("user_profile", {})
            
            # Add allergy filters (only if user has the allergy)
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
            
            # Add other allergies filter
            other_allergies = user_profile.get("other_allergies", [])
            if other_allergies:
                final_filter["other_allergies"] = {"$nin": other_allergies}
            
            # Add dietary preferences filter
            dietary_preferences = user_profile.get("dietary_preferences", [])
            if dietary_preferences:
                final_filter["dietary_preferences"] = {"$in": dietary_preferences}
            
            # Transform user_identity + budget into price filter
            user_identity = user_profile.get("user_identity", "student")
            budget = user_profile.get("budget")
            
            if budget is not None:
                if user_identity == "student":
                    final_filter["student_price"] = {"$lte": budget}
                elif user_identity == "staff":
                    final_filter["staff_price"] = {"$lte": budget}
        
        # Add search-specific criteria
        if search_criteria:
            # Handle cuisine type
            if "cuisine_type" in search_criteria:
                final_filter["cuisine_type"] = {"$in": search_criteria["cuisine_type"]}
            
            # Handle price override
            if "max_price" in search_criteria:
                # Determine which price field to use based on user_identity
                user_identity = base_filter.get("user_profile", {}).get("user_identity", "student")
                if user_identity == "student":
                    final_filter["student_price"] = {"$lte": search_criteria["max_price"]}
                elif user_identity == "staff":
                    final_filter["staff_price"] = {"$lte": search_criteria["max_price"]}
            
            # Handle dietary preferences override
            if "dietary_preferences" in search_criteria:
                final_filter["dietary_preferences"] = {"$in": search_criteria["dietary_preferences"]}
        
        logger.info(f"Final combined filter: {final_filter}")
        return final_filter
        
    except Exception as e:
        logger.error(f"Failed to build food search filter: {e}")
        return {"error": f"Failed to build food search filter: {str(e)}"}

# Separate test functions without @tool decorator for direct testing
def test_build_default_user_filter(user_id: str) -> Dict[str, Any]:
    """Test version without @tool decorator"""
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

def test_build_food_search_filter(
    base_filter: Dict[str, Any],
    search_criteria: Dict[str, Any],
    use_base_filter: bool = True
) -> Dict[str, Any]:
    """Test version without @tool decorator"""
    try:
        logger.info(f"Building food search filter - use_base_filter: {use_base_filter}")
        logger.info(f"Search criteria: {search_criteria}")
        
        final_filter = {}
        
        if use_base_filter and base_filter:
            user_profile = base_filter.get("user_profile", {})
            
            # Add allergy filters (only if user has the allergy)
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
            
            # Add other allergies filter
            other_allergies = user_profile.get("other_allergies", [])
            if other_allergies:
                final_filter["other_allergies"] = {"$nin": other_allergies}
            
            # Add dietary preferences filter
            dietary_preferences = user_profile.get("dietary_preferences", [])
            if dietary_preferences:
                final_filter["dietary_preferences"] = {"$in": dietary_preferences}
            
            # Transform user_identity + budget into price filter
            user_identity = user_profile.get("user_identity", "student")
            budget = user_profile.get("budget")
            
            if budget is not None:
                if user_identity == "student":
                    final_filter["student_price"] = {"$lte": budget}
                elif user_identity == "staff":
                    final_filter["staff_price"] = {"$lte": budget}
        
        # Add search-specific criteria
        if search_criteria:
            # Handle cuisine type
            if "cuisine_type" in search_criteria:
                final_filter["cuisine_type"] = {"$in": search_criteria["cuisine_type"]}
            
            # Handle price override
            if "max_price" in search_criteria:
                # Determine which price field to use based on user_identity
                user_identity = base_filter.get("user_profile", {}).get("user_identity", "student")
                if user_identity == "student":
                    final_filter["student_price"] = {"$lte": search_criteria["max_price"]}
                elif user_identity == "staff":
                    final_filter["staff_price"] = {"$lte": search_criteria["max_price"]}
            
            # Handle dietary preferences override
            if "dietary_preferences" in search_criteria:
                final_filter["dietary_preferences"] = {"$in": search_criteria["dietary_preferences"]}
        
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
    base_filter = test_build_default_user_filter("test_user_123")
    print(f"Base filter structure: {base_filter}")
    
    # Test 2: Build search filter with base filter
    print("\n2. Building search filter with base filter:")
    search_criteria = {
        "cuisine_type": ["Indian"],
        "max_price": 8.0,
        "dietary_preferences": ["vegetarian"]
    }
    final_filter = test_build_food_search_filter(base_filter, search_criteria, use_base_filter=True)
    print(f"Final filter: {final_filter}")
    
    # Test 3: Build search filter without base filter (for friend)
    print("\n3. Building search filter without base filter (for friend):")
    friend_criteria = {
        "cuisine_type": ["Chinese"]
    }
    friend_filter = test_build_food_search_filter(base_filter, friend_criteria, use_base_filter=False)
    print(f"Friend filter: {friend_filter}")
    
    print("\n✅ Filter builder testing completed!")