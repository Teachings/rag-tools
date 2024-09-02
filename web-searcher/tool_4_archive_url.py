import requests
from termcolor import colored

# Function to get the archive.org URL using the Wayback Machine API
def get_wayback_url(original_url):
    api_url = f"http://archive.org/wayback/available?url={original_url}"
    response = requests.get(api_url)
    data = response.json()
    
    if data.get("archived_snapshots"):
        wayback_url = data["archived_snapshots"]["closest"]["url"]
        return wayback_url
    else:
        print(colored(f"Cached page not found: {original_url}", 'red'))
        return None

# Function to display the archive URL or a message if not found
def display_archive_url(original_url):
    archive_url = get_wayback_url(original_url)
    
    if archive_url:
        print(colored(f"Original URL: {original_url}", 'cyan'))
        print(colored(f"Archive URL: {archive_url}", 'yellow'))
        # Optionally, fetch the cached page
        archive_response = requests.get(archive_url)
        if archive_response.status_code == 200:
            print(colored(f"Cached page available: {archive_url}", 'green'))
        else:
            print(colored(f"Cached page not found: {archive_url}", 'red'))
    else:
        print(colored("No archived version available.", 'red'))

# # Entry point of the tool
# if __name__ == "__main__":
#     url = input("Enter the URL to find its archived version: ").strip()
#     display_archive_url(url)
