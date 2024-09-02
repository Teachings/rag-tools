import requests
from termcolor import colored

# Your Serper.dev API key
api_key = '7f172e017e05d15c40b94f0a3995b8af4b83d2d4'

# Define the query and API URL
query = "Python programming"
url = "https://google.serper.dev/search"

# Headers with API key
headers = {
    'X-API-KEY': api_key
}

# Request parameters
params = {
    'q': query,
    'num': 3  # Limiting to top 3 results
}

# Send the GET request to Serper API
response = requests.get(url, headers=headers, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()

    # Extract and print relevant information
    for result in data.get('organic', []):
        print(colored(f"Title: {result['title']}", 'cyan'))
        print(colored(f"URL: {result['link']}", 'yellow'))
        print(colored(f"Snippet: {result.get('snippet', 'No snippet available')}\n", 'green'))
else:
    # Print the error message if the request failed
    print(colored(f"Error: {response.status_code} - {response.text}", 'red'))
