from backend.database import execute_query_dict
import datetime

query = """
    SELECT * FROM exam_schedule_metadata 
    ORDER BY generation_date DESC LIMIT 1
"""
results = execute_query_dict(query)

if results:
    latest = results[0]
    print(f"Latest Schedule ID: {latest['id']}")
    print(f"Is Published: {latest['is_published']}")
    print(f"Generation Date: {latest['generation_date']}")
    
    if not latest['is_published']:
        print("\nWARNING: Latest schedule is NOT PUBLISHED. This is why professors cannot see it.")
else:
    print("No exam schedule metadata found.")
