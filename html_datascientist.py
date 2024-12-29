import requests

# Step 1: Define the URL of the webpage you want to download
url = 'https://www.ambitionbox.com/jobs/data-scientist-jobs-prf'  # Replace this with the URL of your choice
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }

# Step 2: Use requests to fetch the page content
try:
    response = requests.get(url,headers=headers)  # Send a GET request to the webpage
    response.raise_for_status()  # Raise an error for invalid responses (e.g., 404, 500)

    # Step 3: Save the HTML content to a file
    with open('htmlexample.html', 'w', encoding='utf-8') as file:
        file.write(response.text)  # Write the HTML content to the file
    
    print("HTML content saved successfully in 'htmlexample.html'.")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
