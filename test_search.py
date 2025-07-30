#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索引擎测试脚本
用于验证搜索引擎的各项功能
"""

from search_engine import FileSearchEngine, SearchResultFormatter
import os
import tempfile
from pathlib import Path

def create_test_files():
    """创建测试文件"""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # 创建测试文件
    test_files = {
        "math.md": """# 数学基础

## 函数的概念
函数是数学中的基本概念，表示两个集合之间的对应关系。

### 原函数与导数
如果函数F(x)的导数等于f(x)，则称F(x)为f(x)的原函数。

### 不定积分
不定积分是求原函数的过程，记作∫f(x)dx。
""",
        
        "calculus.py": """def derivative(f, x, h=1e-7):
    \"\"\"计算函数的导数\"\"\"
    return (f(x + h) - f(x)) / h

def integral_simpson(f, a, b, n=1000):
    \"\"\"使用辛普森法则计算定积分\"\"\"
    h = (b - a) / n
    result = f(a) + f(b)
    
    for i in range(1, n):
        x = a + i * h
        if i % 2 == 0:
            result += 2 * f(x)
        else:
            result += 4 * f(x)
    
    return result * h / 3

class Function:
    \"\"\"函数类\"\"\"
    def __init__(self, expr):
        self.expr = expr
    
    def evaluate(self, x):
        return eval(self.expr.replace('x', str(x)))
""",
        
        "config.json": """{
    "server": {
        "host": "localhost",
        "port": 8080,
        "debug": true
    },
    "database": {
        "host": "localhost",
        "port": 3306,
        "name": "testdb"
    }
}""",
        
        "notes.txt": """学习笔记

1. 微积分基础
   - 极限的概念
   - 导数的定义
   - 积分的应用

2. 线性代数
   - 矩阵运算
   - 向量空间
   - 特征值和特征向量

3. 概率论
   - 随机变量
   - 概率分布
   - 统计推断
"""
    }
    
    for filename, content in test_files.items():
        file_path = test_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return test_dir

def test_keyword_search():
    """测试关键词搜索"""
    print("🔍 测试关键词搜索...")
    
    engine = FileSearchEngine("test_files")
    results = engine.search_keyword("函数", context_lines=1)
    
    print(f"找到 {len(results)} 个结果")
    for result in results[:3]:  # 只显示前3个结果
        print(f"  📁 {result.file_path}:{result.line_number}")
        print(f"     {result.line_content}")
    print()

def test_regex_search():
    """测试正则表达式搜索"""
    print("🔍 测试正则表达式搜索...")
    
    engine = FileSearchEngine("test_files")
    results = engine.search_regex(r"def\s+\w+", context_lines=1)
    
    print(f"找到 {len(results)} 个Python函数定义")
    for result in results:
        print(f"  📁 {result.file_path}:{result.line_number}")
        print(f"     {result.match_text}")
    print()

def test_multiple_keywords():
    """测试多关键词搜索"""
    print("🔍 测试多关键词搜索...")
    
    engine = FileSearchEngine("test_files")
    
    # AND搜索
    results_and = engine.search_multiple_keywords(["函数", "导数"], operator="AND")
    print(f"AND搜索找到 {len(results_and)} 个结果")
    
    # OR搜索
    results_or = engine.search_multiple_keywords(["函数", "矩阵"], operator="OR")
    print(f"OR搜索找到 {len(results_or)} 个结果")
    print()

def test_fuzzy_search():
    """测试模糊搜索"""
    print("🔍 测试模糊搜索...")
    
    engine = FileSearchEngine("test_files")
    results = engine.fuzzy_search("积分计算", threshold=0.3)
    
    print(f"找到 {len(results)} 个相似结果")
    for result in results[:3]:
        print(f"  📁 {result.file_path}:{result.line_number}")
        print(f"     {result.match_text}")
        print(f"     {result.line_content}")
    print()

def test_file_filtering():
    """测试文件过滤"""
    print("🔍 测试文件过滤...")
    
    engine = FileSearchEngine("test_files")
    
    # 只搜索Python文件
    results_py = engine.search_keyword("def", extensions=["py"])
    print(f"Python文件中找到 {len(results_py)} 个结果")
    
    # 只搜索文档文件
    results_docs = engine.search_keyword("函数", extensions=["md", "txt"])
    print(f"文档文件中找到 {len(results_docs)} 个结果")
    print()

def test_output_formats():
    """测试输出格式"""
    print("🔍 测试输出格式...")
    
    engine = FileSearchEngine("test_files")
    results = engine.search_keyword("函数", context_lines=1)
    
    # 控制台格式
    console_output = SearchResultFormatter.format_console(results[:2])
    print("控制台格式预览:")
    print(console_output[:200] + "..." if len(console_output) > 200 else console_output)
    
    # JSON格式
    json_output = SearchResultFormatter.format_json(results[:1])
    print("\nJSON格式预览:")
    print(json_output[:200] + "..." if len(json_output) > 200 else json_output)
    
    # HTML格式
    html_output = SearchResultFormatter.format_html(results[:1])
    print(f"\nHTML格式长度: {len(html_output)} 字符")
    print()

def test_case_sensitivity():
    """测试大小写敏感"""
    print("🔍 测试大小写敏感...")
    
    engine = FileSearchEngine("test_files")
    
    # 大小写敏感
    results_sensitive = engine.search_keyword("Function", case_sensitive=True)
    print(f"大小写敏感搜索找到 {len(results_sensitive)} 个结果")
    
    # 忽略大小写
    results_insensitive = engine.search_keyword("Function", case_sensitive=False)
    print(f"忽略大小写搜索找到 {len(results_insensitive)} 个结果")
    print()

def test_whole_word():
    """测试全词匹配"""
    print("🔍 测试全词匹配...")
    
    engine = FileSearchEngine("test_files")
    
    # 部分匹配
    results_partial = engine.search_keyword("port", whole_word=False)
    print(f"部分匹配找到 {len(results_partial)} 个结果")
    
    # 全词匹配
    results_whole = engine.search_keyword("port", whole_word=True)
    print(f"全词匹配找到 {len(results_whole)} 个结果")
    print()

def cleanup_test_files():
    """清理测试文件"""
    import shutil
    test_dir = Path("test_files")
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("🧹 测试文件已清理")

def main():
    """主测试函数"""
    print("🚀 开始搜索引擎功能测试\n")
    print("=" * 50)
    
    try:
        # 创建测试文件
        test_dir = create_test_files()
        print(f"📁 测试文件已创建在: {test_dir}")
        print()
        
        # 运行各项测试
        test_keyword_search()
        test_regex_search()
        test_multiple_keywords()
        test_fuzzy_search()
        test_file_filtering()
        test_output_formats()
        test_case_sensitivity()
        test_whole_word()
        
        print("=" * 50)
        print("✅ 所有测试完成！")
        
        # 询问是否保留测试文件
        keep_files = input("\n是否保留测试文件？(y/N): ").lower().strip()
        if keep_files != 'y':
            cleanup_test_files()
        else:
            print("📁 测试文件保留在 test_files/ 目录中")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        cleanup_test_files()

if __name__ == "__main__":
    main()
