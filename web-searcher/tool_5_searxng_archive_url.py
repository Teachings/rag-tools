import requests
from termcolor import colored

# Configurable constant for the number of results to process
RESULTS_LIMIT = 3  # Change this value to the number of top results you want to process

# Function to get search results from SearxNG
def get_search_results(query):
    # Define the base URL and parameters for the SearxNG API
    base_url = "http://localhost:4000/search"  # Replace with your SearxNG instance URL
    params = {
        "q": query,
        "format": "json"
    }

    # Send the GET request to SearxNG API
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # Check for request errors
    return response.json()

# Function to get the archive.org URL using the Wayback Machine API
def get_wayback_url(original_url):
    api_url = f"http://archive.org/wayback/available?url={original_url}"
    response = requests.get(api_url)
    data = response.json()
    
    if data.get("archived_snapshots"):
        wayback_url = data["archived_snapshots"]["closest"]["url"]
        return wayback_url
    else:
        return None

# Function to process and display the search results
def process_search_results(query):
    search_results = get_search_results(query)
    
    if search_results.get("results"):
        # Loop over the results, up to the limit set by RESULTS_LIMIT
        for i, result in enumerate(search_results["results"]):
            if i >= RESULTS_LIMIT:
                break
            original_url = result["url"]
            archive_url = get_wayback_url(original_url)
            
            print(colored(f"Original URL: {original_url}", 'cyan'))
            if archive_url:
                print(colored(f"Archive URL: {archive_url}", 'yellow'))
                # Optionally, fetch the cached page
                archive_response = requests.get(archive_url)
                if archive_response.status_code == 200:
                    print(colored(f"Cached page available: {archive_url}", 'green'))
                else:
                    print(colored(f"Cached page not found: {archive_url}", 'red'))
            else:
                print(colored("No archived version available.", 'red'))
            
            print(colored("-" * 40, 'white'))
    else:
        print(colored("No results found.", 'red'))

# Entry point of the script
def main():
    query = "indiankanoon 65b latest cases for tape recorder usage"  # Replace with your search query
    process_search_results(query)

if __name__ == "__main__":
    main()
