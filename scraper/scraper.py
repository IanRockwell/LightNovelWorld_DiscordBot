import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

def make_request(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print("[scraper.make_request] Request Error:", e)
        return None

def get_novel_latest_chapter(url):
    try:
        response = make_request(url)
        if response is None:
            return None, None

        soup = BeautifulSoup(response.text, 'html.parser')
        latest_chapter_element = soup.find('p', class_='latest text1row')

        if latest_chapter_element:
            chapter_text = latest_chapter_element.text.strip()
            chapter_parts = chapter_text.split(': ', 1)
            if len(chapter_parts) == 2:
                chapter_number = int(chapter_parts[0].replace("Chapter ", ""))
                chapter_name = chapter_parts[1]
                return chapter_number, chapter_name
    except requests.exceptions.RequestException as e:
        print("[scraper.get_novel_latest_chapter] Request Error:", e)
    except AttributeError:
        print("[scraper.get_novel_latest_chapter] Element with class 'latest text1row' not found.")
    except Exception as e:
        print("[scraper.get_novel_latest_chapter] An error occurred:", e)

    return None, None

def get_novel_info(url):
    try:
        response = make_request(url)
        if response is None:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        novel_name_element = soup.find('h1', itemprop='name', class_='novel-title text2row')
        author_element = soup.find('span', itemprop='author')
        thumbnail_element = soup.find('div', class_='glass-background').find('img', alt=True)
        latest_chapter_element = soup.find('p', class_='latest text1row')

        novel_info = {
            'name': novel_name_element.text.strip() if novel_name_element else None,
            'author': author_element.text.strip() if author_element else None,
            'thumbnail_url': thumbnail_element['src'] if thumbnail_element and 'src' in thumbnail_element.attrs else None,
            'latest_chapter': latest_chapter_element.text.strip() if latest_chapter_element else None
        }

        return novel_info

    except requests.exceptions.RequestException as e:
        print("[scraper.get_novel_info] Request Error:", e)
    except AttributeError:
        print("[scraper.get_novel_info] Element not found.")
    except Exception as e:
        print("[scraper.get_novel_info] An error occurred:", e)

    return None

"""
Novel info example

    novel_url = 'https://www.lightnovelworld.com/novel/city-of-witches'
    novel_info = scraper.get_novel_info(novel_url)

    if novel_info:
        print("Novel Name:", novel_info['name'])
        print("Author:", novel_info['author'])
        print("Thumbnail URL:", novel_info['thumbnail_url'])
        print("Latest Chapter:", novel_info['latest_chapter'])
"""
