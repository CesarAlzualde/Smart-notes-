"""
Test script to verify the database import fix.
"""
import sys
print("Testing imports...")

try:
    from app.database import get_session
    print("✅ Successfully imported get_session from app.database")
except Exception as e:
    print(f"❌ Error importing get_session: {e}")
    
try:
    from app.services.enhanced_concept_map_service import EnhancedConceptMapService
    print("✅ Successfully imported EnhancedConceptMapService")
except Exception as e:
    print(f"❌ Error importing EnhancedConceptMapService: {e}")
    
print("Import test complete.")
