import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def scrape_all_book_covers(base_url, save_directory):
    """
    Scrapes all book cover images from books.toscrape.com by navigating
    through the catalogue pages.

    Args:
        base_url (str): The starting URL of the website's catalogue.
        save_directory (str): The local directory to save the images.
    """
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    current_page_url = base_url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    while current_page_url:
        print(f"\n--- Scraping Catalogue Page: {current_page_url} ---")
        
        try:
            # 1. Fetch the catalogue page
            page_response = requests.get(current_page_url, headers=headers)
            page_response.raise_for_status()
            soup = BeautifulSoup(page_response.content, 'html.parser')

            # 2. Find all links to individual book pages
            # The links are within the <h3> tag of each <article class="product_pod">
            book_articles = soup.find_all('article', class_='product_pod')
            if not book_articles:
                print("No book articles found on this page.")
                break

            for article in book_articles:
                # Get the relative URL of the book's page
                book_relative_url = article.find('h3').find('a')['href']
                # Construct the absolute URL for the book's page
                book_absolute_url = urljoin(current_page_url, book_relative_url)
                
                # 3. Go to the book's page to find the full-size image
                download_full_size_image(book_absolute_url, save_directory, headers)
                
                # Implement rate limiting between requests
                time.sleep(1)

            # 4. Find the "next" button to go to the next catalogue page
            next_button = soup.find('li', class_='next')
            if next_button and next_button.find('a'):
                next_page_relative_url = next_button.find('a')['href']
                current_page_url = urljoin(current_page_url, next_page_relative_url)
            else:
                print("\n--- No more pages found. Scraping complete. ---")
                current_page_url = None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {current_page_url}: {e}")
            break

def download_full_size_image(book_page_url, save_directory, headers):
    """
    Visits a single book's page, finds the full-size image URL, and downloads it.
    """
    try:
        # Visit the book's dedicated page
        book_response = requests.get(book_page_url, headers=headers)
        book_response.raise_for_status()
        book_soup = BeautifulSoup(book_response.content, 'html.parser')

        # Find the image source on the book's page
        # On books.toscrape, the main image is in a div with the class "item active"
        image_container = book_soup.find('div', class_='item active')
        if not image_container or not image_container.find('img'):
            print(f"Warning: Could not find image container on {book_page_url}")
            return
            
        img_relative_url = image_container.find('img')['src']
        
        # Construct the absolute URL for the image
        img_absolute_url = urljoin(book_page_url, img_relative_url)

        # Get the image content
        img_response = requests.get(img_absolute_url, stream=True, headers=headers)
        img_response.raise_for_status()

        # Extract filename and create a valid local path
        img_filename = os.path.basename(img_absolute_url)
        save_path = os.path.join(save_directory, img_filename)

        # Save the image to the local directory
        with open(save_path, 'wb') as f:
            for chunk in img_response.iter_content(1024):
                f.write(chunk)
        
        print(f"Successfully downloaded {img_filename} from {book_page_url}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {book_page_url}: {e}")
    except IOError as e:
        print(f"Error saving image for {book_page_url}: {e}")
    except (TypeError, KeyError) as e:
        print(f"Error parsing HTML on {book_page_url}: {e}")


if __name__ == '__main__':
    # Start at the beginning of the book catalogue
    url_to_scrape = 'http://books.toscrape.com/catalogue/category/books_1/index.html'
    output_directory = 'images'
    
    scrape_all_book_covers(url_to_scrape, output_directory)
    print(f"\nAll book covers have been saved to '{output_directory}'.")