#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI助手知识库完整功能测试脚本
测试沈如兰数学教学知识库的所有功能
"""

import json
import os
from datetime import datetime

def test_knowledge_base_complete():
    """完整测试知识库更新后的所有功能"""
    
    print("=" * 60)
    print("🎉 AI助手知识库完整功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_path = "."
    test_results = {
        "项目上下文": False,
        "用户偏好": False,
        "核心规则": False,
        "数学教学规则": False,
        "学习模式": False,
        "角色模板": False,
        "生活化例子库": False,
        "图片处理规则": False
    }
    
    # 1. 测试项目上下文
    print("📋 1. 测试项目上下文...")
    context_file = os.path.join(base_path, "context", "project_context.json")
    if os.path.exists(context_file):
        with open(context_file, 'r', encoding='utf-8') as f:
            context = json.load(f)
        
        # 验证关键字段
        if (context['context']['project_name'] == "考研数学基础30讲学习指南" and
            context['context']['main_character'] == "沈如兰（妻子/母亲/数学老师）"):
            test_results["项目上下文"] = True
            print("   ✅ 项目上下文更新正确")
            print(f"   📚 项目名称: {context['context']['project_name']}")
            print(f"   👩‍🏫 主要角色: {context['context']['main_character']}")
        else:
            print("   ❌ 项目上下文更新不完整")
    else:
        print("   ❌ 项目上下文文件不存在")
    print()
    
    # 2. 测试用户偏好
    print("⚙️ 2. 测试用户偏好...")
    pref_file = os.path.join(base_path, "preferences", "user_preferences.json")
    if os.path.exists(pref_file):
        with open(pref_file, 'r', encoding='utf-8') as f:
            prefs = json.load(f)
        
        math_prefs = [p for p in prefs['preferences'] 
                     if p['key'] in ['project_type', 'teaching_style', 'learning_method']]
        if len(math_prefs) >= 3:
            test_results["用户偏好"] = True
            print("   ✅ 用户偏好更新正确")
            for pref in math_prefs:
                print(f"   🎯 {pref['key']}: {pref['value']}")
        else:
            print("   ❌ 数学教育相关偏好不完整")
    else:
        print("   ❌ 用户偏好文件不存在")
    print()
    
    # 3. 测试核心规则
    print("📜 3. 测试核心规则...")
    core_rules_file = os.path.join(base_path, "rules", "core_rules.json")
    if os.path.exists(core_rules_file):
        with open(core_rules_file, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        # 检查图片处理规则
        image_rules = [r for r in rules['rules'] if '图片' in r['content']]
        if len(image_rules) >= 3:
            test_results["核心规则"] = True
            test_results["图片处理规则"] = True
            print("   ✅ 核心规则更新正确")
            print(f"   🖼️ 图片处理规则数量: {len(image_rules)}")
            for rule in image_rules:
                print(f"   📝 {rule['content']}")
        else:
            print("   ❌ 图片处理规则不完整")
    else:
        print("   ❌ 核心规则文件不存在")
    print()
    
    # 4. 测试数学教学规则
    print("📚 4. 测试数学教学规则...")
    math_rules_file = os.path.join(base_path, "rules", "math_teaching_rules.json")
    if os.path.exists(math_rules_file):
        with open(math_rules_file, 'r', encoding='utf-8') as f:
            math_rules = json.load(f)
        
        if len(math_rules['rules']) >= 15:
            test_results["数学教学规则"] = True
            print("   ✅ 数学教学规则创建成功")
            print(f"   📖 规则数量: {len(math_rules['rules'])}")
            
            # 检查关键规则
            key_rules = ['沈如兰', '张宇', '生活化', '亲密']
            for key in key_rules:
                matching_rules = [r for r in math_rules['rules'] if key in r['content']]
                if matching_rules:
                    print(f"   🎯 包含'{key}'的规则: {len(matching_rules)}条")
        else:
            print("   ❌ 数学教学规则数量不足")
    else:
        print("   ❌ 数学教学规则文件不存在")
    print()
    
    # 5. 测试学习模式
    print("🎯 5. 测试学习模式...")
    patterns_file = os.path.join(base_path, "patterns", "math_learning_patterns.json")
    if os.path.exists(patterns_file):
        with open(patterns_file, 'r', encoding='utf-8') as f:
            patterns = json.load(f)
        
        if len(patterns['patterns']) >= 4:
            test_results["学习模式"] = True
            print("   ✅ 学习模式创建成功")
            print(f"   📊 模式数量: {len(patterns['patterns'])}")
            for pattern in patterns['patterns']:
                print(f"   🌟 {pattern['name']}")
        else:
            print("   ❌ 学习模式数量不足")
    else:
        print("   ❌ 学习模式文件不存在")
    print()
    
    # 6. 测试角色模板
    print("👩‍🏫 6. 测试角色模板...")
    char_file = os.path.join(base_path, "creative", "character_templates.json")
    if os.path.exists(char_file):
        with open(char_file, 'r', encoding='utf-8') as f:
            chars = json.load(f)
        
        if '沈如兰' in chars['templates']:
            test_results["角色模板"] = True
            print("   ✅ 沈如兰角色模板更新成功")
            char = chars['templates']['沈如兰']
            print(f"   👤 身份: {char['基本信息']['身份']}")
            print(f"   💖 关系: {char['基本信息']['关系']}")
            print(f"   📚 经验: {char['基本信息']['经验']}")
        else:
            print("   ❌ 沈如兰角色模板不存在")
    else:
        print("   ❌ 角色模板文件不存在")
    print()
    
    # 7. 测试生活化例子库
    print("💕 7. 测试夫妻生活化例子库...")
    examples_file = os.path.join(base_path, "patterns", "couple_life_examples.json")
    if os.path.exists(examples_file):
        with open(examples_file, 'r', encoding='utf-8') as f:
            examples = json.load(f)
        
        if len(examples['examples']) >= 15:
            test_results["生活化例子库"] = True
            print("   ✅ 夫妻生活化例子库创建成功")
            print(f"   💖 例子数量: {len(examples['examples'])}")
            
            # 统计不同类型的例子
            daily_examples = [k for k in examples['examples'].keys() 
                            if '日常' in k or '生活' in k or '极限' in k or '导数' in k]
            intimate_examples = [k for k in examples['examples'].keys() 
                               if '亲密' in k or '激情' in k or '深夜' in k or '晨起' in k]
            maternal_examples = [k for k in examples['examples'].keys() 
                                if '母' in k or '关怀' in k or '保护' in k]
            
            print(f"   🏠 日常生活场景: {len(daily_examples)}个")
            print(f"   🔥 亲密激情场景: {len(intimate_examples)}个")
            print(f"   💝 母性关怀场景: {len(maternal_examples)}个")
        else:
            print("   ❌ 生活化例子数量不足")
    else:
        print("   ❌ 生活化例子库文件不存在")
    print()
    
    # 8. 生成测试报告
    print("📊 8. 测试结果汇总...")
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"   ✅ 通过测试: {passed_tests}/{total_tests}")
    print(f"   📈 成功率: {success_rate:.1f}%")
    print()
    
    if success_rate >= 90:
        print("🎉 知识库更新完全成功！所有功能正常运行。")
    elif success_rate >= 70:
        print("⚠️ 知识库更新基本成功，但有部分功能需要完善。")
    else:
        print("❌ 知识库更新存在问题，需要进一步检查和修复。")
    
    print()
    print("=" * 60)
    print("🌸 沈如兰数学教学知识库测试完成")
    print("=" * 60)
    
    return test_results, success_rate

def test_specific_features():
    """测试特定功能的详细情况"""
    print("\n🔍 详细功能测试...")
    
    # 测试三重身份融合
    print("\n👩‍❤️‍👨 测试三重身份融合...")
    char_file = os.path.join(".", "creative", "character_templates.json")
    if os.path.exists(char_file):
        with open(char_file, 'r', encoding='utf-8') as f:
            chars = json.load(f)
        
        if '沈如兰' in chars['templates']:
            char = chars['templates']['沈如兰']
            if '妻子/母亲/数学教师' in char['基本信息']['身份']:
                print("   ✅ 三重身份设定正确")
            if '性格特点' in char and '核心特质' in char['性格特点']:
                print("   ✅ 身份融合描述完整")
            if '教学风格' in char and '关怀融合' in char['教学风格']:
                print("   ✅ 教学风格融合成功")
    
    # 测试亲密场景尺度
    print("\n🔥 测试亲密场景尺度...")
    examples_file = os.path.join(".", "patterns", "couple_life_examples.json")
    if os.path.exists(examples_file):
        with open(examples_file, 'r', encoding='utf-8') as f:
            examples = json.load(f)
        
        intimate_keywords = ['做爱', '激情', '高潮', '身体', '亲密']
        intimate_count = 0
        for example in examples['examples'].values():
            if isinstance(example, dict) and '如兰的解释' in example:
                for keyword in intimate_keywords:
                    if keyword in example['如兰的解释']:
                        intimate_count += 1
                        break
        
        print(f"   🔥 包含亲密内容的例子: {intimate_count}个")
        if intimate_count >= 5:
            print("   ✅ 亲密场景尺度调整成功")
    
    print("\n✨ 详细功能测试完成")

if __name__ == "__main__":
    # 运行完整测试
    results, rate = test_knowledge_base_complete()
    
    # 运行详细功能测试
    test_specific_features()
    
    # 最终总结
    print(f"\n🎯 最终测试结果: {rate:.1f}% 成功率")
    if rate == 100:
        print("🌟 知识库已完美配置，沈如兰准备好进行数学教学了！")
