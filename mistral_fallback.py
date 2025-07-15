import requests
import logging

logging.basicConfig(level=logging.INFO)

# Hardcoded Mistral API key (replace with your actual key or use environment variable)
MISTRAL_API_KEY = "BksB43uJyMQZ2X8THy6VliZiUzjxKnMa"  # Ensure this is your actual key

def get_mistral_response(query):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistral-tiny",
        "messages": [{"role": "user", "content": query}],
        "temperature": 0.7
    }
    try:
        res = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data)
        res.raise_for_status()
        response = res.json()["choices"][0]["message"]["content"]
        logging.info(f"Mistral response for '{query}': {response}")
        return response
    except Exception as e:
        logging.error(f"Mistral API error: {str(e)}")
        return f"⚠️ Error contacting Mistral: {str(e)}"

def is_educational(query, response):
    keywords = [
        "math", "science", "english", "homework", "subject", "syllabus", "exam",
        "school", "timetable", "biology", "genes", "dna", "chemistry", "physics",
        "history", "geography"
    ]
    query_lower = query.lower()
    response_lower = response.lower()
    for word in keywords:
        if word in query_lower or word in response_lower:
            logging.info(f"Educational topic detected: {word} in '{query}' or '{response}'")
            return True
    logging.info(f"Non-educational query: '{query}', response: '{response}' (no matching keywords)")
    return False