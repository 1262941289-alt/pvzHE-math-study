#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI助手知识库管理器
用于管理规则、偏好、模式和上下文信息
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class KnowledgeManager:
    def __init__(self, base_path: str = ".ai_knowledge"):
        self.base_path = base_path
        self.config_path = os.path.join(base_path, "config", "system.json")
        self.rules_path = os.path.join(base_path, "rules")
        self.preferences_path = os.path.join(base_path, "preferences") 
        self.patterns_path = os.path.join(base_path, "patterns")
        self.context_path = os.path.join(base_path, "context")
        
        self._ensure_directories()
        self.config = self._load_config()
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        dirs = [
            self.base_path,
            os.path.join(self.base_path, "config"),
            self.rules_path,
            self.preferences_path,
            self.patterns_path,
            self.context_path
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def _load_config(self) -> Dict:
        """加载系统配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_all_rules(self) -> List[Dict]:
        """加载所有规则"""
        rules = []
        for filename in os.listdir(self.rules_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.rules_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'rules' in data:
                        rules.extend(data['rules'])
        return rules
    
    def load_all_preferences(self) -> List[Dict]:
        """加载所有偏好设置"""
        preferences = []
        for filename in os.listdir(self.preferences_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.preferences_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'preferences' in data:
                        preferences.extend(data['preferences'])
        return preferences
    
    def add_rule(self, content: str, priority: int = 5, category: str = "general"):
        """添加新规则"""
        rules_file = os.path.join(self.rules_path, "user_rules.json")
        
        # 加载现有规则或创建新文件
        if os.path.exists(rules_file):
            with open(rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                "id": "user_rules",
                "type": "user_defined",
                "category": category,
                "title": "用户自定义规则",
                "rules": [],
                "created_at": datetime.now().isoformat()
            }
        
        # 添加新规则
        new_rule = {
            "id": f"user_rule_{len(data['rules']) + 1:03d}",
            "content": content,
            "priority": priority,
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        
        data['rules'].append(new_rule)
        data['updated_at'] = datetime.now().isoformat()
        
        # 保存文件
        with open(rules_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"规则已添加: {content}")
    
    def add_preference(self, key: str, value: str, weight: float = 1.0, description: str = ""):
        """添加新偏好"""
        pref_file = os.path.join(self.preferences_path, "user_preferences.json")
        
        # 加载现有偏好
        with open(pref_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 添加新偏好
        new_pref = {
            "key": key,
            "value": value,
            "weight": weight,
            "description": description
        }
        
        data['preferences'].append(new_pref)
        data['updated_at'] = datetime.now().isoformat()
        
        # 保存文件
        with open(pref_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"偏好已添加: {key} = {value}")
    
    def get_active_rules(self) -> List[str]:
        """获取所有激活的规则内容"""
        rules = self.load_all_rules()
        return [rule['content'] for rule in rules if rule.get('active', True)]
    
    def get_preferences_dict(self) -> Dict[str, str]:
        """获取偏好设置字典"""
        preferences = self.load_all_preferences()
        return {pref['key']: pref['value'] for pref in preferences}

    def detect_rule_conflicts(self) -> List[Dict]:
        """检测规则冲突"""
        rules = self.load_all_rules()
        conflicts = []

        for i, rule1 in enumerate(rules):
            for j, rule2 in enumerate(rules[i+1:], i+1):
                # 简单的关键词冲突检测
                if self._rules_conflict(rule1['content'], rule2['content']):
                    conflicts.append({
                        'rule1': rule1,
                        'rule2': rule2,
                        'type': 'content_conflict'
                    })

        return conflicts

    def _rules_conflict(self, content1: str, content2: str) -> bool:
        """检测两个规则是否冲突"""
        # 简单的冲突检测逻辑
        negative_words = ['不要', '禁止', '避免', '不能']
        positive_words = ['要', '必须', '应该', '需要']

        content1_negative = any(word in content1 for word in negative_words)
        content2_negative = any(word in content2 for word in negative_words)

        # 如果一个是否定，一个是肯定，且涉及相同主题，可能冲突
        if content1_negative != content2_negative:
            # 提取关键词进行比较
            keywords1 = set(content1.replace('不要', '').replace('要', '').split())
            keywords2 = set(content2.replace('不要', '').replace('要', '').split())

            # 如果有共同关键词，可能存在冲突
            return len(keywords1.intersection(keywords2)) > 0

        return False

    def learn_from_interaction(self, user_input: str, ai_response: str, feedback: str = ""):
        """从交互中学习"""
        learning_data = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "feedback": feedback,
            "context": self.get_current_context()
        }

        # 保存学习数据
        learning_file = os.path.join(self.base_path, "learning", "interactions.jsonl")
        os.makedirs(os.path.dirname(learning_file), exist_ok=True)

        with open(learning_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(learning_data, ensure_ascii=False) + '\n')

    def get_current_context(self) -> Dict:
        """获取当前上下文"""
        context_file = os.path.join(self.context_path, "project_context.json")
        if os.path.exists(context_file):
            with open(context_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def search_character_with_engine(self, character_name: str) -> List[Dict]:
        """使用搜索引擎查找角色信息"""
        import subprocess
        import sys

        search_results = []
        search_engine_path = os.path.join(os.getcwd(), "搜索", "search_engine.py")

        if not os.path.exists(search_engine_path):
            print("搜索引擎未找到，使用基础搜索方法")
            return self._basic_character_search(character_name)

        try:
            # 使用搜索引擎进行多模式搜索
            search_commands = [
                # 精确搜索角色名
                [sys.executable, search_engine_path, "-k", character_name, "-e", "md", "--json"],
                # 模糊搜索（处理可能的别名）
                [sys.executable, search_engine_path, "-f", character_name, "-t", "0.7", "-e", "md", "--json"],
                # 正则搜索（查找可能的格式变体）
                [sys.executable, search_engine_path, "-r", f".*{re.escape(character_name)}.*", "-e", "md", "--json"]
            ]

            for cmd in search_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0 and result.stdout.strip():
                        try:
                            json_result = json.loads(result.stdout)
                            if json_result and len(json_result) > 0:
                                search_results.extend(json_result)
                        except json.JSONDecodeError:
                            continue
                except subprocess.TimeoutExpired:
                    continue
                except Exception as e:
                    print(f"搜索命令执行失败: {e}")
                    continue

            # 去重和排序
            unique_results = {}
            for result in search_results:
                key = f"{result.get('file_path', '')}:{result.get('line_number', 0)}"
                if key not in unique_results:
                    unique_results[key] = result

            return list(unique_results.values())

        except Exception as e:
            print(f"搜索引擎调用失败: {e}")
            return self._basic_character_search(character_name)

    def _basic_character_search(self, character_name: str) -> List[Dict]:
        """基础角色搜索方法（备用）"""
        results = []

        # 搜索主要角色文档
        character_files = [
            "08-苏青云侍女团按种族分类版.md",
            "02-人物设定与苏家资料.md",
            "07-器灵.md",
            "12-苏家三位长辈女性的极度溺爱设定.md",
            "04-剧情规划与NPC设定.md"
        ]

        for filename in character_files:
            file_path = os.path.join(os.getcwd(), filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            if character_name in line:
                                results.append({
                                    'file_path': filename,
                                    'line_number': i,
                                    'line_content': line.strip(),
                                    'match_text': character_name
                                })
                except Exception as e:
                    print(f"读取文件 {filename} 失败: {e}")

        return results

    def find_character_info(self, character_name: str) -> Dict:
        """查找角色完整信息"""
        print(f"正在搜索角色: {character_name}")

        # 使用搜索引擎查找
        search_results = self.search_character_with_engine(character_name)

        if not search_results:
            return {
                "found": False,
                "character_name": character_name,
                "message": f"未找到角色 '{character_name}' 的信息",
                "suggestion": "请检查角色名称拼写，或告诉我该角色在哪个文档中"
            }

        # 分析搜索结果，提取角色信息
        character_info = {
            "found": True,
            "character_name": character_name,
            "locations": [],
            "basic_info": {},
            "detailed_info": []
        }

        for result in search_results:
            location_info = {
                "file": result.get('file_path', ''),
                "line": result.get('line_number', 0),
                "content": result.get('line_content', ''),
                "context": {
                    "before": result.get('context_before', []),
                    "after": result.get('context_after', [])
                }
            }
            character_info["locations"].append(location_info)

            # 尝试提取基本信息
            content = result.get('line_content', '')
            if '境界' in content or '年龄' in content or '职位' in content:
                character_info["basic_info"]["power_level"] = self._extract_power_level(content)
                character_info["basic_info"]["age"] = self._extract_age(content)
                character_info["basic_info"]["position"] = self._extract_position(content)

        return character_info

    def _extract_power_level(self, content: str) -> str:
        """提取境界信息"""
        import re
        power_match = re.search(r'境界[：:]\s*([^|]+)', content)
        return power_match.group(1).strip() if power_match else ""

    def _extract_age(self, content: str) -> str:
        """提取年龄信息"""
        import re
        age_match = re.search(r'年龄[：:]\s*([^|]+)', content)
        return age_match.group(1).strip() if age_match else ""

    def _extract_position(self, content: str) -> str:
        """提取职位信息"""
        import re
        position_match = re.search(r'职位[：:]\s*([^|]+)', content)
        return position_match.group(1).strip() if position_match else ""

    def interactive_add_rule(self):
        """交互式添加规则"""
        print("\n=== 添加新规则 ===")
        content = input("请输入规则内容: ")
        if not content.strip():
            print("规则内容不能为空")
            return

        try:
            priority = int(input("请输入优先级 (1-10, 默认5): ") or "5")
            priority = max(1, min(10, priority))
        except ValueError:
            priority = 5

        category = input("请输入规则分类 (默认general): ") or "general"
        description = input("请输入规则描述 (可选): ")

        self.add_rule(content, priority, category, description)
        print("✅ 规则添加成功！")

    def add_rule(self, content: str, priority: int = 5, category: str = "general", description: str = ""):
        """添加新规则（增强版）"""
        rules_file = os.path.join(self.rules_path, "user_rules.json")

        # 加载现有规则或创建新文件
        if os.path.exists(rules_file):
            with open(rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                "id": "user_rules",
                "type": "user_defined",
                "category": "custom_rules",
                "title": "用户自定义规则",
                "rules": [],
                "created_at": datetime.now().isoformat()
            }

        # 添加新规则
        new_rule = {
            "id": f"user_rule_{len(data['rules']) + 1:03d}",
            "content": content,
            "priority": priority,
            "active": True,
            "category": category,
            "description": description,
            "created_at": datetime.now().isoformat()
        }

        data['rules'].append(new_rule)
        data['updated_at'] = datetime.now().isoformat()

        # 保存文件
        with open(rules_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"规则已添加: {content}")

    def list_all_rules(self):
        """列出所有规则（按优先级排序）"""
        rules = self.load_all_rules()
        rules.sort(key=lambda x: x.get('priority', 0), reverse=True)

        print("\n=== 所有规则列表 ===")
        for rule in rules:
            status = "✅" if rule.get('active', True) else "❌"
            priority = rule.get('priority', 0)
            category = rule.get('category', 'general')
            print(f"{status} [P{priority}] [{category}] {rule['content']}")
            if rule.get('description'):
                print(f"    描述: {rule['description']}")

        return rules

if __name__ == "__main__":
    import sys

    km = KnowledgeManager()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "add":
            km.interactive_add_rule()
        elif command == "list":
            km.list_all_rules()
        elif command == "rules":
            print("=== 当前激活的规则 ===")
            for rule in km.get_active_rules():
                print(f"- {rule}")
        elif command == "prefs":
            print("=== 当前偏好设置 ===")
            for key, value in km.get_preferences_dict().items():
                print(f"- {key}: {value}")
        else:
            print("可用命令: add, list, rules, prefs")
    else:
        # 默认显示概览
        print("=== 当前激活的规则 ===")
        for rule in km.get_active_rules():
            print(f"- {rule}")

        print("\n=== 当前偏好设置 ===")
        for key, value in km.get_preferences_dict().items():
            print(f"- {key}: {value}")

        print("\n💡 使用提示:")
        print("- python knowledge_manager.py add    # 添加新规则")
        print("- python knowledge_manager.py list   # 查看所有规则")
        print("- python knowledge_manager.py rules  # 查看激活规则")
        print("- python knowledge_manager.py prefs  # 查看偏好设置")
