#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络搜索扩展模块
扩展本地搜索引擎，支持网络内容搜索
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import time

@dataclass
class WebSearchResult:
    """网络搜索结果"""
    url: str
    title: str
    content: str
    match_text: str
    snippet: str

class WebContentSearcher:
    """网络内容搜索器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_url(self, url: str, keyword: str, context_chars: int = 100) -> List[WebSearchResult]:
        """搜索单个网页内容"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 获取文本内容
            text = soup.get_text()
            title = soup.title.string if soup.title else "无标题"
            
            # 搜索关键词
            results = []
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                    
                if keyword.lower() in line.lower():
                    # 创建上下文片段
                    start = max(0, line.lower().find(keyword.lower()) - context_chars//2)
                    end = min(len(line), start + context_chars)
                    snippet = line[start:end]
                    
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(line):
                        snippet = snippet + "..."
                    
                    result = WebSearchResult(
                        url=url,
                        title=title,
                        content=line,
                        match_text=keyword,
                        snippet=snippet
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ 搜索网页失败 {url}: {e}")
            return []
    
    def search_multiple_urls(self, urls: List[str], keyword: str, 
                           delay: float = 1.0) -> List[WebSearchResult]:
        """搜索多个网页"""
        all_results = []
        
        for url in urls:
            print(f"🔍 搜索: {url}")
            results = self.search_url(url, keyword)
            all_results.extend(results)
            
            # 添加延迟避免被封
            if delay > 0:
                time.sleep(delay)
        
        return all_results

class DatabaseSearcher:
    """数据库搜索器（示例）"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def search_database(self, keyword: str, tables: List[str] = None) -> List[Dict]:
        """搜索数据库内容（需要根据具体数据库类型实现）"""
        # 这里是示例代码，需要根据实际数据库类型实现
        print("🔍 数据库搜索功能需要根据具体数据库类型实现")
        return []

class CloudFileSearcher:
    """云文件搜索器（示例）"""
    
    def __init__(self, api_key: str, service_type: str):
        self.api_key = api_key
        self.service_type = service_type
    
    def search_cloud_files(self, keyword: str) -> List[Dict]:
        """搜索云端文件（需要API支持）"""
        print("🔍 云文件搜索需要相应的API密钥和权限")
        return []

# 使用示例
def demo_web_search():
    """演示网络搜索功能"""
    searcher = WebContentSearcher()
    
    # 搜索指定网页
    urls = [
        "https://docs.python.org/3/",
        "https://flask.palletsprojects.com/",
    ]
    
    keyword = "function"
    results = searcher.search_multiple_urls(urls, keyword)
    
    print(f"🎯 找到 {len(results)} 个网络搜索结果:")
    for result in results[:5]:  # 只显示前5个
        print(f"📄 {result.title}")
        print(f"🔗 {result.url}")
        print(f"📝 {result.snippet}")
        print("-" * 50)

if __name__ == "__main__":
    print("🌐 网络搜索扩展模块")
    print("⚠️  注意：网络搜索需要网络连接，请遵守网站的robots.txt规则")
    
    # 运行演示
    demo_web_search()
