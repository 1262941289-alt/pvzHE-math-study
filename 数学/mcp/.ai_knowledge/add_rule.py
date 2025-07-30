#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速添加规则脚本
使用方法: python add_rule.py "规则内容" [优先级] [分类]
"""

import sys
import os
from knowledge_manager import KnowledgeManager

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("python add_rule.py \"规则内容\" [优先级] [分类]")
        print("\n示例:")
        print("python add_rule.py \"总是使用中文回答\" 9 communication")
        print("python add_rule.py \"创作时检查一致性\" 8")
        print("python add_rule.py \"不要使用复杂语法\"")
        return
    
    content = sys.argv[1]
    priority = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    category = sys.argv[3] if len(sys.argv) > 3 else "general"
    
    km = KnowledgeManager()
    km.add_rule(content, priority, category)
    
    print(f"✅ 规则添加成功!")
    print(f"内容: {content}")
    print(f"优先级: {priority}")
    print(f"分类: {category}")

if __name__ == "__main__":
    main()
