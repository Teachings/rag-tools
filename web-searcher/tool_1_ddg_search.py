import requests
from termcolor import colored


# Define the query and API URL
query = "Python programming"
url = f"https://api.duckduckgo.com/?q={query}&format=json"

# Send the GET request to DuckDuckGo's API
response = requests.get(url)

# Parse the JSON response
data = response.json()

# Extract and print relevant information
related_topics = data.get("RelatedTopics", [])
for topic in related_topics[:3]:  # Slice to get only the first 3 topics
    if 'Text' in topic and 'FirstURL' in topic:
        print(colored(f"Title: {topic['Text']}", 'cyan'))
        print(colored(f"URL: {topic['FirstURL']}", 'yellow'))
        print()
