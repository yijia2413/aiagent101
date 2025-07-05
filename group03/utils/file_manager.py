import os
import json
from typing import Dict, Any

class FileManager:
    """Utility class for managing project files"""
    
    def __init__(self, project_root: str = "generated_project"):
        self.project_root = project_root
    
    def create_project_structure(self, code_files: Dict[str, str]) -> str:
        """Create project directory structure and write files"""
        try:
            # Create project root directory
            if not os.path.exists(self.project_root):
                os.makedirs(self.project_root)
            
            # Write all code files
            for filename, content in code_files.items():
                file_path = os.path.join(self.project_root, filename)
                
                # Create subdirectories if needed
                dir_path = os.path.dirname(file_path)
                if dir_path and not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                
                # Write file content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return f"项目文件已成功创建在 {self.project_root} 目录中"
            
        except Exception as e:
            return f"创建项目文件时出错: {str(e)}"
    
    def get_project_files(self) -> Dict[str, str]:
        """Get all files in the project directory"""
        files = {}
        if os.path.exists(self.project_root):
            for root, dirs, filenames in os.walk(self.project_root):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, self.project_root)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            files[relative_path] = f.read()
                    except Exception as e:
                        files[relative_path] = f"Error reading file: {str(e)}"
        return files
    
    def save_report(self, report_type: str, content: str) -> str:
        """Save a report to file"""
        try:
            reports_dir = os.path.join(self.project_root, "reports")
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            filename = f"{report_type}_report.md"
            file_path = os.path.join(reports_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"报告已保存到 {file_path}"
            
        except Exception as e:
            return f"保存报告时出错: {str(e)}"
    
    def get_main_html_file(self) -> str:
        """Get the path to the main HTML file for opening in browser"""
        possible_names = ["index.html", "main.html", "app.html"]
        
        for name in possible_names:
            file_path = os.path.join(self.project_root, name)
            if os.path.exists(file_path):
                return os.path.abspath(file_path)
        
        # If no standard name found, return the first HTML file
        for root, dirs, filenames in os.walk(self.project_root):
            for filename in filenames:
                if filename.endswith('.html'):
                    return os.path.abspath(os.path.join(root, filename))
        
        return ""
