#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色查找器 - 结合搜索引擎的智能角色搜索工具
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from knowledge_manager import KnowledgeManager

class CharacterFinder:
    """智能角色查找器"""
    
    def __init__(self):
        self.km = KnowledgeManager()
        self.search_engine_path = os.path.join(os.getcwd(), "搜索", "search_engine.py")
        
    def find_character(self, character_name: str, detailed: bool = True) -> dict:
        """查找角色信息"""
        print(f"🔍 正在搜索角色: {character_name}")
        
        # 多模式搜索策略
        search_strategies = [
            self._exact_search,      # 精确搜索
            self._fuzzy_search,      # 模糊搜索  
            self._regex_search,      # 正则搜索
            self._context_search     # 上下文搜索
        ]
        
        all_results = []
        for strategy in search_strategies:
            try:
                results = strategy(character_name)
                if results:
                    all_results.extend(results)
                    print(f"✅ {strategy.__name__} 找到 {len(results)} 个结果")
                else:
                    print(f"❌ {strategy.__name__} 未找到结果")
            except Exception as e:
                print(f"⚠️ {strategy.__name__} 执行失败: {e}")
        
        if not all_results:
            return self._no_results_response(character_name)
        
        # 处理和分析结果
        return self._analyze_results(character_name, all_results, detailed)
    
    def _exact_search(self, character_name: str) -> list:
        """精确搜索"""
        if not os.path.exists(self.search_engine_path):
            return []
            
        cmd = [
            sys.executable, self.search_engine_path,
            "-k", character_name,
            "-e", "md",
            "-c", "3",  # 显示3行上下文
            "--json"
        ]
        
        return self._run_search_command(cmd)
    
    def _fuzzy_search(self, character_name: str) -> list:
        """模糊搜索"""
        if not os.path.exists(self.search_engine_path):
            return []
            
        cmd = [
            sys.executable, self.search_engine_path,
            "-f", character_name,
            "-t", "0.7",  # 相似度阈值
            "-e", "md",
            "-c", "2",
            "--json"
        ]
        
        return self._run_search_command(cmd)
    
    def _regex_search(self, character_name: str) -> list:
        """正则表达式搜索"""
        if not os.path.exists(self.search_engine_path):
            return []
        
        # 构建正则表达式，匹配可能的格式
        patterns = [
            f"####.*{character_name}.*",  # 标题格式
            f"\\*\\*{character_name}\\*\\*",  # 粗体格式
            f"- .*{character_name}.*:",   # 列表格式
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
    
    def _context_search(self, character_name: str) -> list:
        """上下文搜索 - 搜索可能的相关词汇"""
        if not os.path.exists(self.search_engine_path):
            return []
        
        # 相关搜索词
        related_terms = [
            f"{character_name}（",  # 带括号的格式
            f"{character_name}族",   # 种族格式
            f"{character_name}团",   # 团体格式
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
    
    def _analyze_results(self, character_name: str, results: list, detailed: bool) -> dict:
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
        
        # 提取角色信息
        character_info = self._extract_character_details(results)
        
        return {
            "found": True,
            "character_name": character_name,
            "total_matches": len(results),
            "files_found": list(files_info.keys()),
            "character_details": character_info,
            "search_results": results if detailed else [],
            "summary": self._generate_summary(character_name, files_info, character_info)
        }
    
    def _extract_character_details(self, results: list) -> dict:
        """提取角色详细信息"""
        details = {
            "境界": "",
            "年龄": "", 
            "职位": "",
            "种族": "",
            "特征": []
        }
        
        for result in results:
            content = result.get('line_content', '')
            
            # 提取境界
            if '境界' in content and not details["境界"]:
                import re
                match = re.search(r'境界[：:]\s*([^|]+)', content)
                if match:
                    details["境界"] = match.group(1).strip()
            
            # 提取年龄
            if '年龄' in content and not details["年龄"]:
                import re
                match = re.search(r'年龄[：:]\s*([^|]+)', content)
                if match:
                    details["年龄"] = match.group(1).strip()
            
            # 提取职位
            if '职位' in content and not details["职位"]:
                import re
                match = re.search(r'职位[：:]\s*([^|]+)', content)
                if match:
                    details["职位"] = match.group(1).strip()
            
            # 提取种族信息
            if ('族' in content or '（' in content) and not details["种族"]:
                import re
                match = re.search(r'（([^）]+)）', content)
                if match:
                    details["种族"] = match.group(1).strip()
        
        return {k: v for k, v in details.items() if v}
    
    def _generate_summary(self, character_name: str, files_info: dict, character_info: dict) -> str:
        """生成搜索摘要"""
        summary = f"找到角色 '{character_name}' 的信息:\n"
        summary += f"- 出现在 {len(files_info)} 个文件中\n"
        
        if character_info:
            summary += "- 基本信息:\n"
            for key, value in character_info.items():
                summary += f"  * {key}: {value}\n"
        
        summary += "- 主要文件:\n"
        for file_path in files_info.keys():
            summary += f"  * {file_path}\n"
        
        return summary
    
    def _no_results_response(self, character_name: str) -> dict:
        """未找到结果的响应"""
        return {
            "found": False,
            "character_name": character_name,
            "message": f"未找到角色 '{character_name}' 的信息",
            "suggestions": [
                "检查角色名称拼写",
                "尝试使用角色的别名或称号",
                "确认角色是否在项目文档中",
                "告诉AI该角色在哪个文档中"
            ]
        }

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("使用方法: python character_finder.py <角色名称> [--simple]")
        print("示例: python character_finder.py 妙音")
        print("      python character_finder.py 苏无霜 --simple")
        return
    
    character_name = sys.argv[1]
    detailed = "--simple" not in sys.argv
    
    finder = CharacterFinder()
    result = finder.find_character(character_name, detailed)
    
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
