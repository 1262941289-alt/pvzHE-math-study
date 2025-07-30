#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一搜索引擎
整合本地文件搜索和网络搜索功能
"""

from search_engine import FileSearchEngine, SearchResult
from web_search_extension import WebContentSearcher, WebSearchResult
from typing import List, Union, Optional
import argparse

class UnifiedSearchEngine:
    """统一搜索引擎"""
    
    def __init__(self, root_path: str = "."):
        self.file_searcher = FileSearchEngine(root_path)
        self.web_searcher = WebContentSearcher()
    
    def search_all(self, keyword: str, 
                   search_local: bool = True,
                   search_web: bool = False,
                   web_urls: Optional[List[str]] = None,
                   **kwargs) -> Dict[str, List]:
        """统一搜索接口"""
        results = {
            'local_files': [],
            'web_content': []
        }
        
        # 本地文件搜索
        if search_local:
            print("🔍 搜索本地文件...")
            local_results = self.file_searcher.search_keyword(keyword, **kwargs)
            results['local_files'] = local_results
            print(f"📁 本地文件找到 {len(local_results)} 个结果")
        
        # 网络内容搜索
        if search_web and web_urls:
            print("🌐 搜索网络内容...")
            web_results = self.web_searcher.search_multiple_urls(web_urls, keyword)
            results['web_content'] = web_results
            print(f"🌍 网络内容找到 {len(web_results)} 个结果")
        
        return results
    
    def format_unified_results(self, results: Dict[str, List]) -> str:
        """格式化统一搜索结果"""
        output = []
        
        # 本地文件结果
        if results['local_files']:
            output.append("📁 本地文件搜索结果:")
            output.append("=" * 50)
            for result in results['local_files'][:10]:  # 限制显示数量
                output.append(f"📄 {result.file_path}:{result.line_number}")
                output.append(f"   {result.line_content}")
                output.append("")
        
        # 网络内容结果
        if results['web_content']:
            output.append("🌐 网络内容搜索结果:")
            output.append("=" * 50)
            for result in results['web_content'][:10]:  # 限制显示数量
                output.append(f"🔗 {result.title}")
                output.append(f"   {result.url}")
                output.append(f"   {result.snippet}")
                output.append("")
        
        return "\n".join(output)

def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(description="统一搜索引擎")
    
    parser.add_argument('-k', '--keyword', required=True, help='搜索关键词')
    parser.add_argument('-p', '--path', default='.', help='本地搜索路径')
    parser.add_argument('--local', action='store_true', default=True, help='搜索本地文件')
    parser.add_argument('--web', action='store_true', help='搜索网络内容')
    parser.add_argument('--urls', nargs='+', help='要搜索的网址列表')
    parser.add_argument('-c', '--context', type=int, default=0, help='上下文行数')
    
    args = parser.parse_args()
    
    # 创建统一搜索引擎
    engine = UnifiedSearchEngine(args.path)
    
    # 执行搜索
    results = engine.search_all(
        keyword=args.keyword,
        search_local=args.local,
        search_web=args.web,
        web_urls=args.urls,
        context_lines=args.context
    )
    
    # 显示结果
    formatted_output = engine.format_unified_results(results)
    print(formatted_output)

if __name__ == "__main__":
    main()
