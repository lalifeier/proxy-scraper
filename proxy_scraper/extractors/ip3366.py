import logging
from typing import List

from bs4 import BeautifulSoup

from proxy_scraper.extractors.base import ProxyScraperBase
from proxy_scraper.proxy import Proxy

logger = logging.getLogger(__name__)

class IP3366(ProxyScraperBase):
    def get_urls(self):
        return [
            'http://www.ip3366.net/free/?stype=1',
            'http://www.ip3366.net/free/?stype=2'
        ]

    def extract_proxies(self, content: str) -> List[Proxy]:
        proxies = []
        if not content:
            return proxies

        logger.debug("Parsing content to extract proxies...")
        soup = BeautifulSoup(content, 'html.parser')
        rows = soup.select('table tbody tr')
        for row in rows:
            cols = row.select('td')
            if len(cols) >= 5:
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                protocol = cols[3].text.strip().lower()

                proxy = Proxy(ip, port, protocol, '')
                proxies.append(proxy)
                logger.debug(f"Extracted proxy: {proxy}")

        return proxies
