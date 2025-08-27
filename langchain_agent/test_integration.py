"""
Integration Test: Filter Builder + Pinecone Search
=================================================

Test the complete workflow from user preferences to food recommendations.
"""

import os
from dotenv import load_dotenv
from filter_builder_tools import build_default_user_filter, build_food_search_filter
from pinecone_search_tool import search_food_recommendations_test

# Load environment variables from current directory
load_dotenv(".env")

def test_complete_workflow():
    """Test the complete workflow from user input to food recommendations."""
    print("🧪 Testing Complete Workflow: Filter Builder → Pinecone Search")
    print("=" * 70)
    
    # Step 1: Get user profile from DynamoDB (simulated)
    print("\n1. 📋 User Profile (from DynamoDB):")
    user_profile = {
        "Item": {
            "budget": {"N": "15"},
            "dietary_preferences": {"S": "vegetarian"},
            "eggs_allergy": {"BOOL": False},  # Changed to False - less strict
            "milk_allergy": {"BOOL": True},
            "other_allergies": {
                "L": [
                    {"S": "banana"}  # Removed noodles - less strict
                ]
            },
            "peanuts_allergy": {"BOOL": False},  # Changed to False - less strict
            "shellfish_allergy": {"BOOL": True},
            "tree_nuts_allergy": {"BOOL": False},
            "user_identity": {"S": "student"},
            "period_plan": {"S": "I always want to eat hot food"}
        }
    }
    print(f"User: Student with £15 budget, vegetarian, fewer allergies")
    
    # Step 2: Build search query filter
    print("\n2. 🔧 Building Search Query Filter:")
    search_query_filter = {
        "budget": float(user_profile["Item"]["budget"]["N"]),
        "dietary_preferences": [user_profile["Item"]["dietary_preferences"]["S"]],
        "eggs_allergy": user_profile["Item"]["eggs_allergy"]["BOOL"],
        "milk_allergy": user_profile["Item"]["milk_allergy"]["BOOL"],
        "other_allergies": [item["S"] for item in user_profile["Item"]["other_allergies"]["L"]],
        "peanuts_allergy": user_profile["Item"]["peanuts_allergy"]["BOOL"],
        "shellfish_allergy": user_profile["Item"]["shellfish_allergy"]["BOOL"],
        "tree_nuts_allergy": user_profile["Item"]["tree_nuts_allergy"]["BOOL"],
        "user_identity": user_profile["Item"]["user_identity"]["S"],
        "period_plan": user_profile["Item"]["period_plan"]["S"]
    }
    
    base_filter = {
        "description": f"Base filter for user {search_query_filter['user_identity']}",
        "user_profile": search_query_filter
    }
    print(f"Base filter created with user preferences")
    
    # Step 3: User search criteria
    print("\n3. 🎯 User Search Criteria:")
    search_criteria = {
        "max_price": 5.0  # Looking for affordable drinks
    }
    print(f"User wants: Cold drinks under £5")
    
    # Step 4: Build final filter
    print("\n4. 🔍 Building Final Filter:")
    final_filter = build_food_search_filter(
        base_filter, 
        search_criteria, 
        use_base_filter=True,
        override_preferences=False
    )
    print(f"Final filter: {final_filter}")
    
    # Step 5: Search Pinecone
    print("\n5. 🔎 Searching Pinecone:")
    query_text = "So hot! Really need some cold drinks, I'm so sleepy right now"
    
    search_results = search_food_recommendations_test(
        query_text=query_text,
        filter_dict=final_filter,
        top_k=5
    )
    
    # Step 6: Display results
    print("\n6. 📋 Search Results:")
    if "error" in search_results:
        print(f"❌ Error: {search_results['error']}")
    else:
        print(f"✅ Found {search_results['total_results']} food items")
        for i, item in enumerate(search_results['food_items'], 1):
            metadata = item['metadata']
            print(f"  {i}. {metadata.get('dish_name', 'Unknown')}")
            print(f"     Price: £{metadata.get('student_price', 'N/A')}")
            print(f"     Restaurant: {metadata.get('restaurant_name', 'N/A')}")
            print(f"     Score: {item['score']:.3f}")
            print()
    
    print("✅ Complete workflow test finished!")

if __name__ == "__main__":
    test_complete_workflow() 