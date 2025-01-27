#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from collections import deque
from datetime import datetime
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup, Tag


class WebCrawler:
    def __init__(self, start_url, max_depth=2, max_pages=100):
        self.start_url = start_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.output_file = self.generate_output_filename(start_url)
        self.visited = set()
        self.queue = deque()
        self.queue.append((start_url, 0))  # Each item is a tuple (url, depth)
        self.counter = 0  # Counts the number of pages crawled

    def generate_output_filename(self, url):
        netloc_parts = urlparse(url).netloc.split('.')
        base_url = netloc_parts[-2] if len(netloc_parts) > 1 else netloc_parts[0]  # Extract base of the URL
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base_url}_{current_time}.txt"
    
    async def fetch(self, session, url):
        headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/86.0.4240.75 Safari/537.36')
        }
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                response.raise_for_status()
                html = await response.text()
                return html
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def format_content(self, soup):
        # Remove all divs with data-elementor-type attribute
        for div in soup.find_all('div', attrs={'data-elementor-type': ['header', 'footer']}):
            div.decompose()
        for div in soup.find_all('div', class_=['header', 'footer']):
            div.decompose()
        for div in soup.find_all('div', id=['header', 'footer']):
            div.decompose()
        
        content = ''
        # Find the main content area; this may vary depending on the website
        # For example, on Wikipedia, the main content is within <div id="mw-content-text">
        # Adjust the selector based on the target website

        # For demonstration, we'll extract headings and paragraphs
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
            if isinstance(element, Tag):
                if element.name.startswith('h'):
                    # Format headings with '=' signs similar to the example
                    level = int(element.name[1])
                    heading_text = element.get_text(strip=True)
                    heading = '=' * level + ' ' + heading_text + ' ' + '=' * level
                    content += heading + '\n'
                elif element.name == 'p':
                    paragraph = element.get_text(strip=True)
                    if paragraph:
                        content += paragraph + '\n\n'
        return content.strip()

    async def crawl(self):
        async with aiohttp.ClientSession() as session:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                while self.queue and self.counter < self.max_pages:
                    url, depth = self.queue.popleft()
                    if url in self.visited or depth > self.max_depth:
                        continue
                    self.visited.add(url)
                    print(f"Crawling ({self.counter + 1}/{self.max_pages}): {url} at depth {depth}")
                    html = await self.fetch(session, url)
                    if html is None:
                        continue
                    self.counter += 1

                    # Process the page content
                    soup = BeautifulSoup(html, 'html.parser')

                    # Format the content
                    content = self.format_content(soup)

                    if content:
                        # Write the formatted content to the file
                        f.write(f"{content}\n\n")

                    # Find all links on the page
                    links = []
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        # Build absolute URL
                        next_url = urljoin(url, href)
                        # Remove URL fragment (the part after '#')
                        next_url = next_url.split('#')[0]
                        # Normalize the URL
                        next_url = next_url.rstrip('/')
                        # Check if next_url is within the same domain
                        if urlparse(next_url).netloc == urlparse(self.start_url).netloc:
                            if next_url not in self.visited:
                                links.append((next_url, depth + 1))

                    # Add new links to the queue
                    self.queue.extend(links)
        print("Crawling finished.")

    def start(self):
        asyncio.run(self.crawl())


if __name__ == "__main__":
    start_url = input("Enter the starting URL: ").strip()
    max_depth = int(input("Enter the maximum crawling depth (e.g., 2): ").strip())
    max_pages = int(input("Enter the maximum number of pages to crawl (e.g., 100): ").strip())

    crawler = WebCrawler(start_url, max_depth, max_pages)
    crawler.start()
    print("Crawling finished.")