#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证线性方程组文档中蓝色注释的格式和指向性
"""

import re
import os

def test_annotation_format():
    """测试蓝色注释的格式和指向性"""
    
    file_path = "第22讲-线性方程组.md"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 测试项目
    tests = []
    
    # 1. 检查蓝色注释标记格式
    blue_annotations = re.findall(r'\*\*🔵 蓝色注释\*\*', content)
    tests.append({
        'name': '蓝色注释标记格式',
        'result': len(blue_annotations) > 0,
        'details': f'找到 {len(blue_annotations)} 个蓝色注释标记'
    })
    
    # 2. 检查箭头指向符号
    arrow_patterns = [r'←', r'→', r'↑', r'↓']
    arrow_count = 0
    for pattern in arrow_patterns:
        arrows = re.findall(pattern, content)
        arrow_count += len(arrows)
    
    tests.append({
        'name': '箭头指向符号',
        'result': arrow_count > 0,
        'details': f'找到 {arrow_count} 个箭头指向符号'
    })
    
    # 3. 检查关键数学概念的注释
    key_concepts = [
        '系数矩阵',
        '增广矩阵', 
        '向量线性组合',
        '列向量',
        '常数向量',
        '本质问题',
        '基本方法',
        '行互换变换',
        '行倍乘变换',
        '行倍加变换',
        '线性组合系数'
    ]
    
    concept_coverage = []
    for concept in key_concepts:
        if concept in content:
            concept_coverage.append(concept)
    
    tests.append({
        'name': '关键概念覆盖',
        'result': len(concept_coverage) >= len(key_concepts) * 0.8,
        'details': f'覆盖了 {len(concept_coverage)}/{len(key_concepts)} 个关键概念'
    })
    
    # 4. 检查注释与数学公式的邻近性
    matrix_patterns = [
        r'\|a₁₁.*a₁ₙ\|',
        r'x₁a₁.*xₙaₙ = β',
        r'αⱼ = \|a₁ⱼ\|'
    ]
    
    formula_annotation_pairs = 0
    for pattern in matrix_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            # 检查公式附近是否有蓝色注释
            start = max(0, match.start() - 200)
            end = min(len(content), match.end() + 200)
            nearby_text = content[start:end]
            if '🔵 蓝色注释' in nearby_text:
                formula_annotation_pairs += 1
    
    tests.append({
        'name': '公式与注释邻近性',
        'result': formula_annotation_pairs > 0,
        'details': f'找到 {formula_annotation_pairs} 个公式-注释配对'
    })
    
    # 5. 检查排版质量
    layout_issues = []
    
    # 检查是否有过长的行
    lines = content.split('\n')
    long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
    if long_lines:
        layout_issues.append(f'过长行: {len(long_lines)} 行')
    
    # 检查空行使用
    consecutive_empty = 0
    max_consecutive_empty = 0
    for line in lines:
        if line.strip() == '':
            consecutive_empty += 1
            max_consecutive_empty = max(max_consecutive_empty, consecutive_empty)
        else:
            consecutive_empty = 0
    
    if max_consecutive_empty > 3:
        layout_issues.append(f'过多连续空行: {max_consecutive_empty}')
    
    tests.append({
        'name': '排版质量',
        'result': len(layout_issues) == 0,
        'details': f'发现问题: {layout_issues}' if layout_issues else '排版良好'
    })
    
    # 输出测试结果
    print("=" * 60)
    print("🔍 蓝色注释格式测试结果")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        status = "✅ 通过" if test['result'] else "❌ 失败"
        print(f"{status} {test['name']}: {test['details']}")
        if test['result']:
            passed += 1
    
    print("=" * 60)
    print(f"📊 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！蓝色注释格式优化成功！")
        return True
    else:
        print("⚠️  部分测试未通过，需要进一步优化")
        return False

def test_specific_annotations():
    """测试特定注释的指向性"""
    
    file_path = "第22讲-线性方程组.md"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n" + "=" * 60)
    print("🎯 特定注释指向性测试")
    print("=" * 60)
    
    # 检查特定的注释-内容配对
    specific_tests = [
        {
            'content': 'A = |a₁₁  a₁₂  ...  a₁ₙ|',
            'annotation': '由未知数的系数构成',
            'description': '系数矩阵定义'
        },
        {
            'content': 'x₁a₁ + x₂a₂ + ... + xₙaₙ = β',
            'annotation': '向量线性组合',
            'description': '线性组合表达式'
        },
        {
            'content': '(线性变一) 两个方程互换',
            'annotation': '行互换变换',
            'description': '基本行变换'
        }
    ]
    
    for test in specific_tests:
        content_found = test['content'] in content
        annotation_found = test['annotation'] in content
        
        if content_found and annotation_found:
            # 检查它们是否在合理距离内
            content_pos = content.find(test['content'])
            annotation_pos = content.find(test['annotation'])
            distance = abs(content_pos - annotation_pos)
            
            if distance < 300:  # 300字符内认为是邻近的
                print(f"✅ {test['description']}: 内容与注释邻近 (距离: {distance})")
            else:
                print(f"⚠️  {test['description']}: 内容与注释距离较远 (距离: {distance})")
        else:
            missing = []
            if not content_found:
                missing.append("内容")
            if not annotation_found:
                missing.append("注释")
            print(f"❌ {test['description']}: 缺少 {', '.join(missing)}")

if __name__ == "__main__":
    print("🧪 开始测试蓝色注释格式...")
    
    success = test_annotation_format()
    test_specific_annotations()
    
    if success:
        print("\n🎊 测试完成！文档格式符合要求。")
    else:
        print("\n🔧 测试完成！建议进一步优化文档格式。")
