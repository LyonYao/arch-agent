# 修改src/utils/prompt_manager.py

import os
from typing import Dict, Any

class PromptManager:
    """提示词管理器，负责加载和提供提示词模板"""
    
    _instance = None
    _prompts = {}
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(PromptManager, cls).__new__(cls)
            cls._instance._load_prompts()
        return cls._instance
    
    def _load_prompts(self):
        """加载提示词配置"""
        try:
            # 获取项目根目录
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            prompts_dir = os.path.join(root_dir, "config", "prompts")
            
            self._prompts = {}
            
            if os.path.exists(prompts_dir):
                # 遍历模型目录
                for model_name in os.listdir(prompts_dir):
                    model_dir = os.path.join(prompts_dir, model_name)
                    if os.path.isdir(model_dir):
                        self._prompts[model_name] = {}
                        
                        # 遍历提示词文件
                        for prompt_file in os.listdir(model_dir):
                            if prompt_file.endswith(".md"):
                                prompt_type = os.path.splitext(prompt_file)[0]
                                file_path = os.path.join(model_dir, prompt_file)
                                
                                with open(file_path, "r", encoding="utf-8") as f:
                                    self._prompts[model_name][prompt_type] = f.read()
            else:
                print(f"警告: 提示词目录不存在: {prompts_dir}")
        except Exception as e:
            print(f"加载提示词配置失败: {str(e)}")
            self._prompts = {}
    
    def get_prompt(self, model_type: str, prompt_type: str, default: str = "") -> str:
        """
        获取指定模型和类型的提示词
        
        Args:
            model_type: 模型类型，如 'qianwen', 'gemini'
            prompt_type: 提示词类型，如 'architecture', 'adjustment'
            default: 默认提示词，如果找不到指定的提示词则返回此值
            
        Returns:
            str: 提示词模板
        """
        return self._prompts.get(model_type, {}).get(prompt_type, default)
