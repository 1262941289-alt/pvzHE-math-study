#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的行跳转工具
支持多种编辑器的精确行跳转功能
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple

class AdvancedLineJumper:
    """高级行跳转工具"""
    
    def __init__(self):
        self.system = platform.system()
        self.available_editors = self._detect_editors()
    
    def _detect_editors(self) -> Dict[str, Dict]:
        """检测系统中可用的编辑器"""
        editors = {
            'vscode': {
                'commands': ['code', 'code-insiders'],
                'line_format': '-g "{file}:{line}"',
                'name': 'Visual Studio Code'
            },
            'cursor': {
                'commands': ['cursor'],
                'line_format': '-g "{file}:{line}"',
                'name': 'Cursor'
            },
            'codium': {
                'commands': ['codium'],
                'line_format': '-g "{file}:{line}"',
                'name': 'VSCodium'
            },
            'sublime': {
                'commands': ['subl', 'sublime_text'],
                'line_format': '"{file}:{line}"',
                'name': 'Sublime Text'
            },
            'atom': {
                'commands': ['atom'],
                'line_format': '"{file}:{line}"',
                'name': 'Atom'
            },
            'vim': {
                'commands': ['vim', 'nvim'],
                'line_format': '+{line} "{file}"',
                'name': 'Vim/NeoVim'
            },
            'emacs': {
                'commands': ['emacs'],
                'line_format': '+{line} "{file}"',
                'name': 'Emacs'
            },
            'notepadpp': {
                'commands': ['notepad++', 'npp'],
                'line_format': '"{file}" -n{line}',
                'name': 'Notepad++'
            }
        }
        
        available = {}
        for editor_id, editor_info in editors.items():
            for cmd in editor_info['commands']:
                if shutil.which(cmd):
                    available[editor_id] = {
                        'command': cmd,
                        'line_format': editor_info['line_format'],
                        'name': editor_info['name']
                    }
                    break
        
        return available
    
    def list_available_editors(self) -> List[str]:
        """列出可用的编辑器"""
        return [f"{info['name']} ({editor_id})" for editor_id, info in self.available_editors.items()]
    
    def jump_to_line(self, file_path: str, line_number: int, editor: str = 'auto') -> Tuple[bool, str]:
        """跳转到文件的指定行"""
        abs_path = os.path.abspath(file_path)
        
        if not os.path.exists(abs_path):
            return False, f"文件不存在: {abs_path}"
        
        if editor == 'auto':
            # 自动选择最佳编辑器
            editor = self._choose_best_editor()
        
        if editor not in self.available_editors:
            return False, f"编辑器不可用: {editor}"
        
        editor_info = self.available_editors[editor]
        cmd = editor_info['command']
        line_format = editor_info['line_format']
        
        # 构建命令
        full_cmd = f'{cmd} {line_format.format(file=abs_path, line=line_number)}'
        
        try:
            subprocess.run(full_cmd, shell=True, check=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"已在 {editor_info['name']} 中打开 {file_path}:{line_number}"
        except subprocess.CalledProcessError as e:
            return False, f"无法打开编辑器: {e}"
    
    def _choose_best_editor(self) -> str:
        """选择最佳的编辑器"""
        # 优先级顺序
        priority = ['vscode', 'cursor', 'codium', 'sublime', 'notepadpp', 'atom', 'vim', 'emacs']
        
        for editor in priority:
            if editor in self.available_editors:
                return editor
        
        # 如果没有找到，返回第一个可用的
        if self.available_editors:
            return list(self.available_editors.keys())[0]
        
        return None
    
    def open_file_location(self, file_path: str) -> Tuple[bool, str]:
        """打开文件所在位置"""
        abs_path = os.path.abspath(file_path)
        folder_path = os.path.dirname(abs_path)
        
        if not os.path.exists(folder_path):
            return False, f"文件夹不存在: {folder_path}"
        
        try:
            if self.system == "Windows":
                subprocess.run(f'explorer /select,"{abs_path}"', shell=True, check=True)
            elif self.system == "Darwin":  # macOS
                subprocess.run(f'open -R "{abs_path}"', shell=True, check=True)
            else:  # Linux
                subprocess.run(f'xdg-open "{folder_path}"', shell=True, check=True)
            
            return True, f"已打开文件位置: {folder_path}"
        except subprocess.CalledProcessError as e:
            return False, f"无法打开文件位置: {e}"
    
    def create_desktop_shortcut(self, file_path: str, line_number: int, 
                               shortcut_name: str = None) -> Tuple[bool, str]:
        """创建桌面快捷方式直接跳转到指定行"""
        if not shortcut_name:
            filename = os.path.basename(file_path)
            shortcut_name = f"{filename}_line_{line_number}"
        
        abs_path = os.path.abspath(file_path)
        
        if self.system == "Windows":
            return self._create_windows_shortcut(abs_path, line_number, shortcut_name)
        elif self.system == "Darwin":
            return self._create_macos_shortcut(abs_path, line_number, shortcut_name)
        else:
            return self._create_linux_shortcut(abs_path, line_number, shortcut_name)
    
    def _create_windows_shortcut(self, file_path: str, line_number: int, name: str) -> Tuple[bool, str]:
        """创建Windows快捷方式"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, f"{name}.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            
            # 使用最佳编辑器
            editor = self._choose_best_editor()
            if editor:
                editor_info = self.available_editors[editor]
                cmd = editor_info['command']
                line_format = editor_info['line_format']
                
                shortcut.Targetpath = shutil.which(cmd)
                shortcut.Arguments = line_format.format(file=file_path, line=line_number).replace(cmd + ' ', '')
                shortcut.WorkingDirectory = os.path.dirname(file_path)
                shortcut.save()
                
                return True, f"快捷方式已创建: {shortcut_path}"
            else:
                return False, "没有可用的编辑器"
                
        except ImportError:
            return False, "需要安装 pywin32 和 winshell: pip install pywin32 winshell"
        except Exception as e:
            return False, f"创建快捷方式失败: {e}"
    
    def _create_macos_shortcut(self, file_path: str, line_number: int, name: str) -> Tuple[bool, str]:
        """创建macOS快捷方式"""
        try:
            desktop = os.path.expanduser("~/Desktop")
            script_path = os.path.join(desktop, f"{name}.command")
            
            editor = self._choose_best_editor()
            if editor:
                editor_info = self.available_editors[editor]
                cmd = editor_info['command']
                line_format = editor_info['line_format']
                
                script_content = f"""#!/bin/bash
{cmd} {line_format.format(file=file_path, line=line_number)}
"""
                
                with open(script_path, 'w') as f:
                    f.write(script_content)
                
                os.chmod(script_path, 0o755)
                return True, f"快捷方式已创建: {script_path}"
            else:
                return False, "没有可用的编辑器"
                
        except Exception as e:
            return False, f"创建快捷方式失败: {e}"
    
    def _create_linux_shortcut(self, file_path: str, line_number: int, name: str) -> Tuple[bool, str]:
        """创建Linux快捷方式"""
        try:
            desktop = os.path.expanduser("~/Desktop")
            shortcut_path = os.path.join(desktop, f"{name}.desktop")
            
            editor = self._choose_best_editor()
            if editor:
                editor_info = self.available_editors[editor]
                cmd = editor_info['command']
                line_format = editor_info['line_format']
                
                desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={name}
Comment=Jump to {file_path}:{line_number}
Exec={cmd} {line_format.format(file=file_path, line=line_number)}
Icon=text-editor
Terminal=false
Categories=Development;
"""
                
                with open(shortcut_path, 'w') as f:
                    f.write(desktop_content)
                
                os.chmod(shortcut_path, 0o755)
                return True, f"快捷方式已创建: {shortcut_path}"
            else:
                return False, "没有可用的编辑器"
                
        except Exception as e:
            return False, f"创建快捷方式失败: {e}"

def main():
    """命令行主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="高级行跳转工具")
    parser.add_argument('file', nargs='?', help='文件路径')
    parser.add_argument('line', nargs='?', type=int, help='行号')
    parser.add_argument('-e', '--editor', default='auto', help='指定编辑器 (auto/vscode/sublime/vim等)')
    parser.add_argument('--list-editors', action='store_true', help='列出可用编辑器')
    parser.add_argument('--open-folder', action='store_true', help='打开文件所在文件夹')
    parser.add_argument('--create-shortcut', help='创建桌面快捷方式')
    
    args = parser.parse_args()
    
    jumper = AdvancedLineJumper()
    
    if args.list_editors:
        print("🔧 可用编辑器:")
        editors = jumper.list_available_editors()
        if editors:
            for i, editor in enumerate(editors, 1):
                print(f"  {i}. {editor}")
        else:
            print("  ❌ 未检测到支持的编辑器")
        return
    
    if args.open_folder:
        if not args.file:
            print("❌ 需要指定文件路径")
            return
        success, message = jumper.open_file_location(args.file)
        print("✅" if success else "❌", message)
        return

    if args.create_shortcut:
        if not args.file or not args.line:
            print("❌ 需要指定文件路径和行号")
            return
        success, message = jumper.create_desktop_shortcut(args.file, args.line, args.create_shortcut)
        print("✅" if success else "❌", message)
        return

    # 执行跳转
    if not args.file or not args.line:
        print("❌ 需要指定文件路径和行号")
        return

    success, message = jumper.jump_to_line(args.file, args.line, args.editor)
    print("✅" if success else "❌", message)

if __name__ == "__main__":
    main()
