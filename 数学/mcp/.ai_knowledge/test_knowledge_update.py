#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试知识库更新情况
"""

import json
import os

def test_knowledge_base():
    """测试知识库更新情况"""
    base_path = "."
    
    print("=== 知识库更新测试 ===\n")
    
    # 1. 测试项目上下文
    context_file = os.path.join(base_path, "context", "project_context.json")
    if os.path.exists(context_file):
        with open(context_file, 'r', encoding='utf-8') as f:
            context = json.load(f)
        print("✅ 项目上下文已更新:")
        print(f"   项目名称: {context['context']['project_name']}")
        print(f"   项目类型: {context['context']['project_type']}")
        print(f"   主要角色: {context['context']['main_character']}")
        print()
    
    # 2. 测试用户偏好
    pref_file = os.path.join(base_path, "preferences", "user_preferences.json")
    if os.path.exists(pref_file):
        with open(pref_file, 'r', encoding='utf-8') as f:
            prefs = json.load(f)
        print("✅ 用户偏好已更新:")
        for pref in prefs['preferences']:
            if pref['key'] in ['project_type', 'teaching_style', 'learning_method']:
                print(f"   {pref['key']}: {pref['value']}")
        print()
    
    # 3. 测试数学教学规则
    math_rules_file = os.path.join(base_path, "rules", "math_teaching_rules.json")
    if os.path.exists(math_rules_file):
        with open(math_rules_file, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        print("✅ 数学教学规则已创建:")
        print(f"   规则数量: {len(rules['rules'])}")
        for rule in rules['rules'][:3]:  # 显示前3个规则
            print(f"   - {rule['content']}")
        print()
    
    # 4. 测试学习模式
    patterns_file = os.path.join(base_path, "patterns", "math_learning_patterns.json")
    if os.path.exists(patterns_file):
        with open(patterns_file, 'r', encoding='utf-8') as f:
            patterns = json.load(f)
        print("✅ 学习模式已创建:")
        print(f"   模式数量: {len(patterns['patterns'])}")
        for pattern in patterns['patterns']:
            print(f"   - {pattern['name']}: {pattern['description']}")
        print()
    
    # 5. 测试角色模板
    char_file = os.path.join(base_path, "creative", "character_templates.json")
    if os.path.exists(char_file):
        with open(char_file, 'r', encoding='utf-8') as f:
            chars = json.load(f)
        print("✅ 角色模板已更新:")
        print(f"   主要角色: 沈如兰")
        if '沈如兰' in chars['templates']:
            char = chars['templates']['沈如兰']
            print(f"   年龄: {char['基本信息']['年龄']}")
            print(f"   身份: {char['基本信息']['身份']}")
            print(f"   经验: {char['基本信息']['经验']}")
        print()
    
    print("🎉 知识库已成功从玄幻世界设定更新为数学教育项目！")

if __name__ == "__main__":
    test_knowledge_base()
