import requests
from termcolor import colored

# Define the query and the SearxNG API URL
query = "Python programming"
base_url = "http://192.168.1.10:4000/search"  # Replace with your SearxNG instance URL

# Prepare the query parameters
params = {
    "q": query,
    "format": "json"
}

# Send the GET request to SearxNG API
response = requests.get(base_url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()

    # Extract and print relevant information
    for result in data.get("results", [])[:3]:  # Limiting to the top 3 results
        print(colored(f"Title: {result['title']}", 'cyan'))
        print(colored(f"URL: {result['url']}", 'yellow'))
        print(colored(f"Snippet: {result.get('content', 'No snippet available')}\n", 'green'))
else:
    # Print the error message if the request failed
    print(colored(f"Error: {response.status_code} - {response.text}", 'red'))
