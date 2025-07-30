#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第22讲-线性方程组 文档测试脚本
验证文档内容的完整性和教学质量
"""

import os
import re
from datetime import datetime

def test_lecture_22():
    """测试第22讲线性方程组文档"""
    
    print("=" * 60)
    print("🧪 第22讲-线性方程组 文档测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    file_path = os.path.join(os.path.dirname(__file__), "第22讲-线性方程组.md")
    
    if not os.path.exists(file_path):
        print("❌ 文档文件不存在")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    test_results = {}
    
    # 1. 测试文档结构
    print("📋 1. 测试文档结构...")
    required_sections = [
        "如兰老师的温柔开场",
        "基础知识结构",
        "齐次线性方程组",
        "非齐次线性方程组",
        "两个方程组的公共解",
        "同解方程组",
        "求解方法总结",
        "夫妻生活化例子",
        "重要定理总结",
        "解题技巧",
        "典型例题",
        "学习小贴士"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)
    
    if not missing_sections:
        test_results["文档结构"] = True
        print("   ✅ 文档结构完整")
        print(f"   📚 包含 {len(required_sections)} 个主要章节")
    else:
        test_results["文档结构"] = False
        print(f"   ❌ 缺少章节: {', '.join(missing_sections)}")
    print()
    
    # 2. 测试数学内容
    print("📐 2. 测试数学内容...")
    math_concepts = [
        "线性方程组",
        "矩阵表示",
        "Ax = b",
        "rank",
        "高斯消元法",
        "克拉默法则",
        "齐次线性方程组",
        "非齐次线性方程组",
        "基础解系",
        "解的结构",
        "公共解",
        "同解方程组",
        "特解",
        "通解"
    ]
    
    found_concepts = []
    for concept in math_concepts:
        if concept in content:
            found_concepts.append(concept)
    
    concept_coverage = len(found_concepts) / len(math_concepts)
    if concept_coverage >= 0.8:
        test_results["数学内容"] = True
        print("   ✅ 数学概念覆盖充分")
        print(f"   🎯 概念覆盖率: {concept_coverage:.1%}")
    else:
        test_results["数学内容"] = False
        print(f"   ❌ 数学概念覆盖不足: {concept_coverage:.1%}")
    print()
    
    # 3. 测试沈如兰教学风格
    print("🌸 3. 测试沈如兰教学风格...")
    teaching_elements = [
        "亲爱的",
        "老公", 
        "宝贝",
        "如兰的",
        "温柔",
        "我们",
        "夫妻",
        "生活化",
        "妈妈"
    ]
    
    style_count = 0
    for element in teaching_elements:
        style_count += len(re.findall(element, content))
    
    if style_count >= 20:
        test_results["教学风格"] = True
        print("   ✅ 沈如兰教学风格突出")
        print(f"   💕 风格元素出现次数: {style_count}")
    else:
        test_results["教学风格"] = False
        print(f"   ❌ 教学风格不够突出: {style_count} 次")
    print()
    
    # 4. 测试生活化例子
    print("💕 4. 测试生活化例子...")
    life_examples = [
        "家庭",
        "预算",
        "收支",
        "分工",
        "爱意",
        "默契",
        "生活",
        "感情"
    ]
    
    example_count = 0
    for example in life_examples:
        example_count += len(re.findall(example, content))
    
    if example_count >= 10:
        test_results["生活化例子"] = True
        print("   ✅ 生活化例子丰富")
        print(f"   🏠 生活化元素: {example_count} 次")
    else:
        test_results["生活化例子"] = False
        print(f"   ❌ 生活化例子不足: {example_count} 次")
    print()
    
    # 5. 测试数学公式
    print("🔢 5. 测试数学公式...")
    formula_patterns = [
        r'x₁|x₂|xₙ',  # 下标
        r'a₁₁|a₁₂',   # 系数
        r'det\(',      # 行列式
        r'rank\(',     # 秩
        r'Ax = b',     # 矩阵方程
        r'=|≠|<|>'     # 数学符号
    ]
    
    formula_count = 0
    for pattern in formula_patterns:
        formula_count += len(re.findall(pattern, content))
    
    if formula_count >= 20:
        test_results["数学公式"] = True
        print("   ✅ 数学公式表达规范")
        print(f"   📊 公式元素: {formula_count} 个")
    else:
        test_results["数学公式"] = False
        print(f"   ❌ 数学公式不够规范: {formula_count} 个")
    print()

    # 6. 测试新增内容
    print("🆕 6. 测试新增内容...")
    new_concepts = [
        "基础解系",
        "解的结构定理",
        "公共解",
        "同解方程组",
        "特解",
        "通解",
        "自由变量",
        "线性无关"
    ]

    new_concept_count = 0
    for concept in new_concepts:
        if concept in content:
            new_concept_count += 1

    new_coverage = new_concept_count / len(new_concepts)
    if new_coverage >= 0.8:
        test_results["新增内容"] = True
        print("   ✅ 新增内容覆盖充分")
        print(f"   🎯 新概念覆盖率: {new_coverage:.1%}")
    else:
        test_results["新增内容"] = False
        print(f"   ❌ 新增内容覆盖不足: {new_coverage:.1%}")
    print()
    
    # 6. 测试情感表达
    print("💖 6. 测试情感表达...")
    emotional_phrases = [
        "我爱你",
        "相信你",
        "支持你", 
        "心疼",
        "骄傲",
        "美好",
        "温暖",
        "甜蜜"
    ]
    
    emotion_count = 0
    for phrase in emotional_phrases:
        emotion_count += len(re.findall(phrase, content))
    
    if emotion_count >= 5:
        test_results["情感表达"] = True
        print("   ✅ 情感表达充分")
        print(f"   💝 情感元素: {emotion_count} 次")
    else:
        test_results["情感表达"] = False
        print(f"   ❌ 情感表达不足: {emotion_count} 次")
    print()

    # 7. 测试例题质量
    print("📚 7. 测试例题质量...")
    example_patterns = [
        r'例题\d+',
        r'解题过程',
        r'如兰的.*解释',
        r'步骤',
        r'方法',
        r'齐次',
        r'非齐次',
        r'参数'
    ]

    example_count = 0
    for pattern in example_patterns:
        example_count += len(re.findall(pattern, content))

    if example_count >= 12:
        test_results["例题质量"] = True
        print("   ✅ 例题内容丰富")
        print(f"   📖 例题元素: {example_count} 个")
    else:
        test_results["例题质量"] = False
        print(f"   ❌ 例题内容不够丰富: {example_count} 个")
    print()

    # 8. 测试内容完整性
    print("🔍 8. 测试内容完整性...")
    incomplete_patterns = [
        r'^\s*-\s*$',  # 空的列表项
        r'^\s*\*\*.*\*\*\s*$',  # 只有标题没有内容的行
        r'由未知数\s*$',  # 未完成的句子
        r'^\s*\d+\.\s*$'  # 空的编号项
    ]

    incomplete_count = 0
    incomplete_lines = []
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        for pattern in incomplete_patterns:
            if re.match(pattern, line):
                incomplete_count += 1
                incomplete_lines.append(f"第{i}行: {line.strip()}")

    if incomplete_count == 0:
        test_results["内容完整性"] = True
        print("   ✅ 内容完整，无遗漏")
    else:
        test_results["内容完整性"] = False
        print(f"   ❌ 发现不完整内容: {incomplete_count} 处")
        for line_info in incomplete_lines[:3]:  # 只显示前3个
            print(f"     {line_info}")
    print()

    # 9. 测试文档长度和质量
    print("📏 9. 测试文档质量...")
    word_count = len(content)
    line_count = len(content.split('\n'))

    if word_count >= 3000 and line_count >= 150:
        test_results["文档质量"] = True
        print("   ✅ 文档内容充实")
        print(f"   📝 字符数: {word_count}")
        print(f"   📄 行数: {line_count}")
    else:
        test_results["文档质量"] = False
        print(f"   ❌ 文档内容不够充实")
        print(f"   📝 字符数: {word_count} (需要≥3000)")
        print(f"   📄 行数: {line_count} (需要≥150)")
    print()

    # 10. 生成测试报告
    print("📊 10. 测试结果汇总...")
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"   ✅ 通过测试: {passed_tests}/{total_tests}")
    print(f"   📈 成功率: {success_rate:.1f}%")
    print()
    
    # 详细结果
    print("📋 详细测试结果:")
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
    print()
    
    if success_rate >= 90:
        print("🎉 第22讲文档质量优秀！沈如兰的教学风格完美体现。")
    elif success_rate >= 70:
        print("👍 第22讲文档质量良好，但还有改进空间。")
    else:
        print("⚠️ 第22讲文档需要进一步完善。")
    
    print()
    print("=" * 60)
    print("🌸 第22讲-线性方程组 测试完成")
    print("=" * 60)
    
    return success_rate >= 80

def test_specific_content():
    """测试特定内容的详细情况"""
    print("\n🔍 特定内容详细测试...")
    
    file_path = os.path.join(os.path.dirname(__file__), "第22讲-线性方程组.md")
    if not os.path.exists(file_path):
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 测试三重身份体现
    print("\n👩‍❤️‍👨 测试三重身份体现...")
    wife_elements = ["老公", "亲爱的", "我们", "夫妻"]
    mother_elements = ["宝贝", "妈妈", "心疼", "相信你"]
    teacher_elements = ["概念", "定理", "方法", "技巧"]
    
    wife_count = sum(len(re.findall(elem, content)) for elem in wife_elements)
    mother_count = sum(len(re.findall(elem, content)) for elem in mother_elements)
    teacher_count = sum(len(re.findall(elem, content)) for elem in teacher_elements)
    
    print(f"   💕 妻子身份元素: {wife_count} 次")
    print(f"   🤱 母亲身份元素: {mother_count} 次")
    print(f"   👩‍🏫 教师身份元素: {teacher_count} 次")
    
    if wife_count >= 10 and mother_count >= 5 and teacher_count >= 15:
        print("   ✅ 三重身份融合完美")
    else:
        print("   ⚠️ 某些身份体现不够充分")
    
    print("\n✨ 特定内容测试完成")

if __name__ == "__main__":
    # 运行主测试
    success = test_lecture_22()
    
    # 运行详细测试
    test_specific_content()
    
    # 最终结论
    if success:
        print("\n🌟 第22讲-线性方程组文档测试通过！")
        print("💕 沈如兰老师准备好教授线性方程组了！")
    else:
        print("\n📝 第22讲文档需要进一步优化。")
