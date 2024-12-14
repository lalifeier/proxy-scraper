import logging
import re
from typing import Dict, List

import aiohttp

from proxy_scraper.config import CONFIG
from proxy_scraper.extractors.base import ProxyScraperBase
from proxy_scraper.proxy import Proxy

logger = logging.getLogger(__name__)

PROXY_DIR = CONFIG["proxy_dir"]


class TxtProxyScraper(ProxyScraperBase):
    def __init__(self):
        super().__init__()

    def get_urls(self) -> Dict[str, List[str]]:
        return {
            "http": [
                "https://api.openproxylist.xyz/http.txt",
                "https://www.proxy-list.download/api/v1/get?type=http",
                # "https://multiproxy.org/txt_all/proxy.txt",
                # "https://multiproxy.org/txt_anon/proxy.txt",
                "https://proxyspace.pro/http.txt",
                "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt",
                "https://github.com/Anonym0usWork1221/Free-Proxies/raw/main/proxy_files/http_proxies.txt",
                "https://github.com/officialputuid/KangProxy/raw/KangProxy/http/http.txt",
                "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
                "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&country=all&ssl=all&anonymity=all"
            ],
            "https": [
                "https://www.proxy-list.download/api/v1/get?type=https",
                "https://proxyspace.pro/https.txt",
                "https://github.com/Anonym0usWork1221/Free-Proxies/raw/main/proxy_files/https_proxies.txt",
                "https://github.com/officialputuid/KangProxy/raw/KangProxy/https/https.txt"
            ],
            "socks4": [
                "https://api.openproxylist.xyz/socks4.txt",
                "https://www.proxy-list.download/api/v1/get?type=socks4",
                "https://github.com/Anonym0usWork1221/Free-Proxies/raw/main/proxy_files/socks4_proxies.txt",
                "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt",
                "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt",
                "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&country=all&ssl=all&anonymity=all"
            ],
            "socks5": [
                "https://api.openproxylist.xyz/socks5.txt",
                "https://www.proxy-list.download/api/v1/get?type=socks5",
                "https://github.com/Anonym0usWork1221/Free-Proxies/raw/main/proxy_files/socks5_proxies.txt",
                "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
                "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
                "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&country=all&ssl=all&anonymity=all"
            ]
        }

    async def scrape(self):
        urls_by_type = self.get_urls()
        unique_proxies_by_type = {proxy_type: set() for proxy_type in urls_by_type.keys()}

        for proxy_type, urls in urls_by_type.items():
            for url in urls:
                logger.info(f"Scraping {proxy_type} proxies from {url}...")
                content = await self.fetch_content(url)
                if content:
                    proxies = self.extract_proxies(content, proxy_type)
                    unique_proxies_by_type[proxy_type].update(proxies)

        for proxy_type, proxies in unique_proxies_by_type.items():
            if proxies:
                valid_proxies = await self.validator.validate_proxies(list(proxies))
                self.writer.save_raw_proxies(valid_proxies)

    async def fetch_content(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    def extract_proxies(self, content: str, proxy_type: str) -> List[Proxy]:
        proxies = []
        if content:
            lines = content.strip().split("\n")
            for line in lines:
                ip_port = line.strip()
                if re.match(r'^(\d{1,3}\.){3}\d{1,3}:\d+$', ip_port):
                    ip, port = ip_port.split(":")
                    proxies.append(Proxy(ip, port, proxy_type, ""))
        return proxies
