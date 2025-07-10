import json
import pymongo

client = pymongo.MongoClient("mongodb+srv://purple:pdfl3ydpewMD9s9m@autoagentevalutationclu.jnz84ae.mongodb.net/?retryWrites=true&w=majority&appName=autoAgentEvalutationCluster")
db = client["auto_agent_evaluation"]
collection = db["roles_doc"]

with open("roles.json", "r") as f:
    raw_data = json.load(f)

# Fix the format
data = []
for role_name, details in raw_data.items():
    details["name"] = role_name
    data.append(details)
print(details)
print(f"Inserting {len(data)} roles...")

collection.delete_many({})
collection.insert_many(data)

print("✅ Done seeding roles.")