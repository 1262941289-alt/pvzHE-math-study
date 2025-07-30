#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用信息查找器 - 支持角色、地点、物品等所有信息的搜索
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from knowledge_manager import KnowledgeManager

class UniversalFinder:
    """通用信息查找器"""
    
    def __init__(self):
        self.km = KnowledgeManager()
        self.search_engine_path = os.path.join(os.getcwd(), "搜索", "search_engine.py")
        
        # 信息类型映射
        self.info_types = {
            "角色": {
                "files": [
                    "08-苏青云侍女团按种族分类版.md",
                    "02-人物设定与苏家资料.md", 
                    "07-器灵.md",
                    "12-苏家三位长辈女性的极度溺爱设定.md",
                    "04-剧情规划与NPC设定.md",
                    "0-苏青云宠物体系设定.md"
                ],
                "keywords": ["姓名", "种族", "境界", "年龄", "职位", "侍女", "护卫", "器灵"]
            },
            "地点": {
                "files": [
                    "10-地点大百科.md",
                    "01-世界观与境界体系.md",
                    "05-修仙界真实设定.md"
                ],
                "keywords": ["城市", "宗门", "秘境", "山脉", "海域", "大陆", "区域", "坊市"]
            },
            "物品": {
                "files": [
                    "13物品大百科.md",
                    "03-功法武技与妖兽百科.md",
                    "07-器灵.md"
                ],
                "keywords": ["法宝", "丹药", "功法", "武技", "神器", "灵材", "宝物"]
            },
            "势力": {
                "files": [
                    "09-势力大百科.md",
                    "05-修仙界真实设定.md",
                    "02-人物设定与苏家资料.md"
                ],
                "keywords": ["宗门", "家族", "联盟", "组织", "势力", "门派"]
            },
            "妖兽": {
                "files": [
                    "03-功法武技与妖兽百科.md",
                    "08-苏青云侍女团按种族分类版.md",
                    "0-苏青云宠物体系设定.md"
                ],
                "keywords": ["妖兽", "神兽", "灵兽", "血脉", "种族", "妖族"]
            }
        }
    
    def find_info(self, query: str, info_type: str = "auto", detailed: bool = True) -> dict:
        """查找信息"""
        print(f"🔍 正在搜索: {query} (类型: {info_type})")
        
        # 自动判断信息类型
        if info_type == "auto":
            info_type = self._detect_info_type(query)
            print(f"📋 自动识别类型: {info_type}")
        
        # 多模式搜索策略
        search_strategies = [
            self._exact_search,      # 精确搜索
            self._fuzzy_search,      # 模糊搜索  
            self._regex_search,      # 正则搜索
            self._context_search     # 上下文搜索
        ]
        
        all_results = []
        target_files = self.info_types.get(info_type, {}).get("files", [])
        
        for strategy in search_strategies:
            try:
                results = strategy(query, target_files)
                if results:
                    all_results.extend(results)
                    print(f"✅ {strategy.__name__} 找到 {len(results)} 个结果")
                else:
                    print(f"❌ {strategy.__name__} 未找到结果")
            except Exception as e:
                print(f"⚠️ {strategy.__name__} 执行失败: {e}")
        
        if not all_results:
            return self._no_results_response(query, info_type)
        
        # 处理和分析结果
        return self._analyze_results(query, info_type, all_results, detailed)
    
    def _detect_info_type(self, query: str) -> str:
        """自动检测信息类型"""
        # 检查是否包含特定关键词
        for info_type, config in self.info_types.items():
            keywords = config.get("keywords", [])
            if any(keyword in query for keyword in keywords):
                return info_type
        
        # 默认按优先级检测
        detection_order = ["角色", "地点", "物品", "势力", "妖兽"]
        
        for info_type in detection_order:
            # 简单的启发式检测
            if info_type == "角色" and any(char in query for char in ["姓名", "人", "者", "师", "君", "仙"]):
                return info_type
            elif info_type == "地点" and any(char in query for char in ["城", "山", "海", "域", "境", "地"]):
                return info_type
            elif info_type == "物品" and any(char in query for char in ["宝", "器", "丹", "法", "技", "剑"]):
                return info_type
        
        return "角色"  # 默认为角色搜索
    
    def _exact_search(self, query: str, target_files: list = None) -> list:
        """精确搜索"""
        if not os.path.exists(self.search_engine_path):
            return []

        cmd = [
            sys.executable, self.search_engine_path,
            "-k", query,
            "-e", "md",
            "-c", "3",  # 显示3行上下文
            "--json"
        ]

        return self._run_search_command(cmd)
    
    def _fuzzy_search(self, query: str, target_files: list = None) -> list:
        """模糊搜索"""
        if not os.path.exists(self.search_engine_path):
            return []

        cmd = [
            sys.executable, self.search_engine_path,
            "-f", query,  # 模糊搜索
            "-t", "0.7",  # 相似度阈值
            "-e", "md",
            "-c", "2",
            "--json"
        ]

        return self._run_search_command(cmd)
    
    def _regex_search(self, query: str, target_files: list = None) -> list:
        """正则表达式搜索"""
        if not os.path.exists(self.search_engine_path):
            return []
        
        # 构建正则表达式，匹配可能的格式
        patterns = [
            f"####.*{query}.*",      # 标题格式
            f"\\*\\*{query}\\*\\*",  # 粗体格式
            f"- .*{query}.*:",       # 列表格式
            f"{query}[：:]",         # 冒号格式
        ]
        
        results = []

        for pattern in patterns:
            cmd = [
                sys.executable, self.search_engine_path,
                "-r", pattern,
                "-e", "md",
                "-c", "2",
                "--json"
            ]
            results.extend(self._run_search_command(cmd))
        
        return results
    
    def _context_search(self, query: str, target_files: list = None) -> list:
        """上下文搜索"""
        if not os.path.exists(self.search_engine_path):
            return []
        
        # 相关搜索词
        related_terms = [
            f"{query}（",     # 带括号的格式
            f"{query}族",     # 种族格式
            f"{query}宗",     # 宗门格式
            f"{query}城",     # 城市格式
            f"{query}山",     # 山脉格式
        ]
        
        results = []

        for term in related_terms:
            cmd = [
                sys.executable, self.search_engine_path,
                "-k", term,
                "-e", "md",
                "-c", "1",
                "--json"
            ]
            results.extend(self._run_search_command(cmd))
        
        return results
    
    def _run_search_command(self, cmd: list) -> list:
        """执行搜索命令"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                try:
                    json_result = json.loads(result.stdout)
                    return json_result if isinstance(json_result, list) else []
                except json.JSONDecodeError:
                    return []
            return []
        except (subprocess.TimeoutExpired, Exception):
            return []
    
    def _analyze_results(self, query: str, info_type: str, results: list, detailed: bool) -> dict:
        """分析搜索结果"""
        # 去重
        unique_results = {}
        for result in results:
            key = f"{result.get('file_path', '')}:{result.get('line_number', 0)}"
            if key not in unique_results:
                unique_results[key] = result
        
        results = list(unique_results.values())
        
        # 按文件分组
        files_info = {}
        for result in results:
            file_path = result.get('file_path', '')
            if file_path not in files_info:
                files_info[file_path] = []
            files_info[file_path].append(result)
        
        # 提取信息详情
        info_details = self._extract_info_details(results, info_type)
        
        return {
            "found": True,
            "query": query,
            "info_type": info_type,
            "total_matches": len(results),
            "files_found": list(files_info.keys()),
            "info_details": info_details,
            "search_results": results if detailed else [],
            "summary": self._generate_summary(query, info_type, files_info, info_details)
        }
    
    def _extract_info_details(self, results: list, info_type: str) -> dict:
        """提取信息详细内容"""
        details = {}
        
        if info_type == "角色":
            details = {"境界": "", "年龄": "", "职位": "", "种族": "", "特征": []}
        elif info_type == "地点":
            details = {"位置": "", "特色": "", "势力": "", "重要性": "", "描述": []}
        elif info_type == "物品":
            details = {"类型": "", "品级": "", "功能": "", "来源": "", "特性": []}
        elif info_type == "势力":
            details = {"类型": "", "实力": "", "领袖": "", "地盘": "", "特点": []}
        elif info_type == "妖兽":
            details = {"种族": "", "血脉": "", "境界": "", "特性": "", "能力": []}
        
        # 从搜索结果中提取信息
        for result in results:
            content = result.get('line_content', '')
            
            # 通用信息提取
            import re
            for key in details.keys():
                if isinstance(details[key], str) and not details[key]:
                    pattern = f'{key}[：:]\s*([^|]+)'
                    match = re.search(pattern, content)
                    if match:
                        details[key] = match.group(1).strip()
        
        return {k: v for k, v in details.items() if v}
    
    def _generate_summary(self, query: str, info_type: str, files_info: dict, info_details: dict) -> str:
        """生成搜索摘要"""
        summary = f"找到{info_type} '{query}' 的信息:\n"
        summary += f"- 出现在 {len(files_info)} 个文件中\n"
        
        if info_details:
            summary += f"- 基本信息:\n"
            for key, value in info_details.items():
                summary += f"  * {key}: {value}\n"
        
        summary += "- 主要文件:\n"
        for file_path in files_info.keys():
            summary += f"  * {file_path}\n"
        
        return summary
    
    def _no_results_response(self, query: str, info_type: str) -> dict:
        """未找到结果的响应"""
        return {
            "found": False,
            "query": query,
            "info_type": info_type,
            "message": f"未找到{info_type} '{query}' 的信息",
            "suggestions": [
                "检查名称拼写",
                "尝试使用别名或简称",
                f"确认该{info_type}是否在项目文档中",
                f"告诉AI该{info_type}在哪个文档中"
            ]
        }

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("使用方法: python universal_finder.py <查询内容> [信息类型] [--simple]")
        print("信息类型: 角色, 地点, 物品, 势力, 妖兽, auto(自动)")
        print("示例: python universal_finder.py 妙音 角色")
        print("      python universal_finder.py 千流郡 地点")
        print("      python universal_finder.py 九天神韵 auto --simple")
        return
    
    query = sys.argv[1]
    info_type = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "--simple" else "auto"
    detailed = "--simple" not in sys.argv
    
    finder = UniversalFinder()
    result = finder.find_info(query, info_type, detailed)
    
    if result["found"]:
        print("\n" + "="*50)
        print(result["summary"])
        if detailed and result.get("search_results"):
            print("\n详细搜索结果:")
            for i, res in enumerate(result["search_results"][:5], 1):
                print(f"\n{i}. {res.get('file_path', '')}:{res.get('line_number', '')}")
                print(f"   {res.get('line_content', '')}")
    else:
        print(f"\n❌ {result['message']}")
        print("\n建议:")
        for suggestion in result.get("suggestions", []):
            print(f"- {suggestion}")

if __name__ == "__main__":
    main()
