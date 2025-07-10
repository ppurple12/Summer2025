import pandas as pd
import pprint as pp
import spacy
import re
from services.data.LoadingPipeline import load_all_files
from pprint import pprint
from rapidfuzz import fuzz
import hashlib
import json 
import unicodedata
from rapidfuzz.fuzz import partial_ratio

# loading NLP 
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 4_000_000  


import json
def extract_candidate_name_from_resume(text):
    skip_keywords = {
        'manager', 'email', 'sales', 'developer', 'location', 'phone', 'linkedin',
        'work experience', 'education', 'skills', 'certifications', 'license',
        'responsibilities', 'special skills', 'additional information', 'www.', 'http',
        'may', 'june', 'april', 'august', 'september', 'october', 'november', 'december',
        'present', 'resume', 'curriculum vitae', 'objective', 'profile'
    }

    for line in text.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue

        line_lower = line_clean.lower()
        # Skip lines containing any of these keywords (likely not a name)
        if any(kw in line_lower for kw in skip_keywords):
            continue

        # Check if line looks like a name
        if is_likely_name(line_clean) and name_confidence(line_clean) >= 0.7:
            return line_clean

    return None

def clean_name(name):
    return name.strip().lower()

def calculate_hash(data):
    serializable_data = make_json_serializable(data)
    json_str = json.dumps(serializable_data, sort_keys=True)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(i) for i in obj]
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    else:
        return obj
def normalize_name(name):
    return re.sub(r'\s+', ' ', name).strip().lower()

def clean_text(s):
    return re.sub(r'\s+', ' ', str(s)).strip()
def name_confidence(ent_text):
    if re.fullmatch(r"[A-Z][a-z]+ [A-Z][a-z]+", ent_text):
        return 1.0
    if re.fullmatch(r"[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+", ent_text):
        return 0.9
    if re.fullmatch(r"[A-Z][a-z]+", ent_text):
        return 0.5
    return 0.3

def token_overlap(name1, name2):
    tokens1 = set(name1.split())
    tokens2 = set(name2.split())
    return len(tokens1 & tokens2)


def is_likely_name(ent_text):
    tokens = ent_text.strip().split()
    if not (1 <= len(tokens) <= 4):
        return False

    # Keywords that indicate the entity is not a person
    job_terms = {
        "manager", "engineer", "school", "email", "limited", "training", "sales",
        "head", "cadet", "pvt", "customer", "knowledge", "october", "deck",
        "nagpur", "pune", "kolkata", "madhya", "pradesh", "contractor"
    }

    if any(word.lower() in job_terms for word in tokens):
        return False

    # Capitalized patterns (title case or full caps)
    capitalized = sum(1 for w in tokens if w[0].isupper() or w.isupper())
    return capitalized >= len(tokens) // 2

def name_confidence(ent_text):
    if re.fullmatch(r"[A-Z][a-z]+ [A-Z][a-z]+", ent_text):
        return 1.0
    if re.fullmatch(r"[A-Z][a-z]+", ent_text):
        return 0.7
    if re.fullmatch(r"[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+", ent_text):
        return 0.9
    return 0.3


def get_name_from_first_line(text):
    first_line = text.split('\n', 1)[0].strip()
    if not first_line:
        return None
    tokens = first_line.split()
    if tokens and tokens[0].isdigit():
        tokens = tokens[1:]
    if 2 <= len(tokens) <= 4 and all(t.istitle() or t.isupper() for t in tokens):
        return ' '.join(tokens).strip()
    return None


def detect_agents_ner(text, agents_list=None, id_list=None, fuzzy_threshold=85, debug=False):
    if not agents_list or not text:
        return [], []

    detected_names = []
    detected_ids = []
    seen = set()

    text_clean = clean_text(text)
    text_lower = text_clean.lower()

    # Normalize agents
    name_to_id = {
        name: agent_id
        for name, agent_id in zip(agents_list, id_list)
        if name
    }
    lower_name_map = {name.lower(): agent_id for name, agent_id in name_to_id.items()}

    # 1. Check first line for name
    first_line_name = get_name_from_first_line(text)
    if first_line_name:
        
        first_line_name_lower = first_line_name.lower()
        # Try exact or fuzzy match against agents
        for name_lower, agent_id in lower_name_map.items():
            if name_lower in seen:
                continue
             
            if name_lower == first_line_name_lower:
                if debug:
                    print(f"✅ First line exact match: '{first_line_name}' == '{name_lower}'")
                detected_names.append(name_lower)
                detected_ids.append(agent_id)
                seen.add(name_lower)
                break
            else:
                similarity = partial_ratio(first_line_name_lower, name_lower)
                token_ov = token_overlap(first_line_name_lower, name_lower)
                if similarity >= fuzzy_threshold and token_ov >= 1 and len(first_line_name_lower) > 4:
                    if debug:
                        print(f"🤝 First line fuzzy match: '{first_line_name_lower}' ≈ '{name_lower}' (score={similarity}, tokens_overlap={token_ov})")
                    detected_names.append(name_lower)
                    detected_ids.append(agent_id)
                    seen.add(name_lower)
                    break

    # 2. Proceed with usual NER detection on the full text
    doc = nlp(text_clean)

    for ent in doc.ents:
        ent_text = clean_text(ent.text)
        ent_text_lower = ent_text.lower()

        if debug:
            print(f"\n🔍 Entity: '{ent.text}' → Cleaned: '{ent_text_lower}'")

        if ent.label_ != "PERSON":
            if debug:
                print(f"❌ Skipping non-person entity: {ent.text}")
            continue

        if not is_likely_name(ent_text) or name_confidence(ent_text) < 0.7:
            if debug:
                print(f"❌ Skipping low confidence/unlikely name entity: {ent_text}")
            continue

        for name_lower, agent_id in lower_name_map.items():
            if name_lower in seen:
                continue

            if name_lower == ent_text_lower:
                if debug:
                    print(f"✅ Exact match: {ent_text} == {name_lower}")
                detected_names.append(name_lower)
                detected_ids.append(agent_id)
                seen.add(name_lower)
                break
            else:
                similarity = partial_ratio(ent_text_lower, name_lower)
                token_ov = token_overlap(ent_text_lower, name_lower)

                if similarity >= fuzzy_threshold and token_ov >= 1 and len(ent_text_lower) > 4:
                    if debug:
                        print(f"🤝 Fuzzy match: '{ent_text_lower}' ≈ '{name_lower}' (score={similarity}, tokens_overlap={token_ov})")
                    detected_names.append(name_lower)
                    detected_ids.append(agent_id)
                    seen.add(name_lower)
                    break
                else:
                    if debug:
                        print(f"❌ No good fuzzy match for: {ent_text_lower} vs {name_lower} (score={similarity}, tokens_overlap={token_ov})")

    # Backup fuzzy match against entire text (only for longer names)
    for name, agent_id in name_to_id.items():
        key = name.lower()
        if key in seen or len(key) < 5:
            continue

        similarity = partial_ratio(key, text_lower)
        if similarity >= fuzzy_threshold:
            if debug:
                print(f"🔁 Fallback match in full text: {name} (score={similarity})")
            detected_names.append(name)
            detected_ids.append(agent_id)
            seen.add(key)

    return detected_names, detected_ids

# preprocess the content 
def preprocess_text(text_dict):
    # Ensure that 'text_dict' is a dictionary
    if isinstance(text_dict, dict):
        # Process each key-value pair and concatenate their values into a single string
        cleaned_text = " ".join(
            str(value).lower() for value in text_dict.values()
        )
        
        return cleaned_text
 
# takes documents and formats them into required format
def format_data(data, agents=None, ids=None):
    structured_data = []

    for file in data:
        category = file["category"]
        text = file["text"]

        if isinstance(text, list):  # Already parsed rows from Excel/CSV
            document_entries = text  # List of dicts
            # Add hash to each entry
            document_entries = [
                {**entry, "_hash": calculate_hash(entry)} for entry in document_entries
            ]
            search_text = " ".join(" ".join(str(v) for v in row.values()) for row in text)
        elif isinstance(text, dict):
            document_entries = [text]
            document_entries = [
                {**entry, "_hash": calculate_hash(entry)} for entry in document_entries
            ]
            search_text = " ".join(str(v) for v in text.values())
            
        else:  # raw string
            preprocessed = str(text)
            # Wrap string in dict to add hash consistently
            document_entries = [{"text": preprocessed, "_hash": calculate_hash(preprocessed)}]
            search_text = preprocessed
        #search_text = re.sub(r'\s+', ' ', search_text).strip()
        
        detected_agents, detected_ids = detect_agents_ner(search_text, agents, ids, debug=False)
    
        for agent_name, agent_id in zip(detected_agents, detected_ids):
            existing_agent = next(
                (item for item in structured_data if item["agent_name"] == agent_name),
                None
            )

            if existing_agent:
                existing_agent["documents"].setdefault(category, []).extend(document_entries)
            else:
                structured_data.append({
                    "agent_name": agent_name,
                    "agent_id": agent_id,
                    "documents": {
                        category: document_entries
                    }
                })
        
    return structured_data
