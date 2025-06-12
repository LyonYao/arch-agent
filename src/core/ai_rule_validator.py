#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI架构规则验证模块
使用AI验证架构设计是否符合公司架构设计规则
"""

import os
import json
from typing import Dict, Any, List, Tuple, Optional

from src.api.qianwen_api import QianwenAPI
from src.utils.logger import get_logger

# 获取日志记录器
logger = get_logger(__name__)

class AIRuleValidator:
    """AI架构规则验证器"""
    
    def __init__(self, rules_dir: str = None, api_client: QianwenAPI = None):
        """
        初始化AI规则验证器
        
        Args:
            rules_dir: 规则文件目录，如果为None则使用默认目录
            api_client: 千问API客户端，如果为None则创建新实例
        """
        logger.warning("初始化AI规则验证器")
        
        # 设置规则目录
        if rules_dir is None:
            # 默认规则目录
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.rules_dir = os.path.join(base_dir, "resources", "aws_patterns")
            logger.warning(f"使用默认规则目录: {self.rules_dir}")
        else:
            self.rules_dir = rules_dir
            logger.warning(f"使用指定规则目录: {self.rules_dir}")
        
        # 检查目录是否存在
        if os.path.exists(self.rules_dir):
            logger.warning(f"规则目录存在: {self.rules_dir}")
        else:
            logger.warning(f"规则目录不存在，将创建: {self.rules_dir}")
            os.makedirs(self.rules_dir, exist_ok=True)
        
        # 初始化API客户端
        self.api_client = api_client or QianwenAPI()
        
        # 加载规则
        logger.warning("开始加载规则...")
        self.rules = self._load_rules()
        logger.warning(f"已加载 {len(self.rules)} 条架构规则")
    
    def _load_rules(self) -> List[Dict[str, Any]]:
        """
        加载所有规则文件
        
        Returns:
            List[Dict]: 规则列表
        """
        rules = []
        
        try:
            # 检查目录是否存在
            if not os.path.exists(self.rules_dir):
                logger.error(f"规则目录不存在: {self.rules_dir}")
                return rules
                
            # 检查目录是否可读
            if not os.access(self.rules_dir, os.R_OK):
                logger.error(f"规则目录不可读: {self.rules_dir}")
                return rules
                
            # 列出目录内容
            try:
                dir_contents = os.listdir(self.rules_dir)
                logger.warning(f"目录内容: {dir_contents}")
            except Exception as e:
                logger.error(f"无法列出目录内容: {str(e)}")
                return rules
            
            # 遍历规则目录中的所有.md文件
            logger.warning(f"正在加载规则: {self.rules_dir}")
            file_cnt = 0
            for filename in dir_contents:
                if filename.endswith(".md"):
                    file_cnt += 1
                    file_path = os.path.join(self.rules_dir, filename)
                    try:
                        # 读取规则文件内容
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # 提取规则名称（文件的第一个标题）
                        import re
                        name_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                        name = name_match.group(1) if name_match else os.path.basename(file_path)
                        
                        rules.append({
                            "name": name,
                            "content": content,
                            "file_path": file_path
                        })
                        logger.warning(f"已加载规则: {name} ({file_path})")
                    except Exception as e:
                        logger.error(f"加载规则文件 {file_path} 失败: {str(e)}")
            logger.warning(f"共加载 {file_cnt} 个规则文件")
        except Exception as e:
            logger.error(f"加载规则失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
        return rules
    
    def validate_architecture(self, architecture: Dict[str, Any], requirements: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        使用AI验证架构是否符合规则
        
        Args:
            architecture: 架构设计数据
            requirements: 用户需求
            
        Returns:
            Tuple[bool, List]: (是否全部通过, 违反的规则列表)
        """
        if not self.rules:
            logger.warning("没有加载任何规则，跳过验证")
            return True, []
        
        violations = []
        
        # 将架构转换为JSON字符串
        architecture_json = json.dumps(architecture, ensure_ascii=False, indent=2)
        
        # 对每条规则进行验证
        for rule in self.rules:
            logger.warning(f"使用AI验证规则: {rule['name']}")
            
            # 构建验证提示
            prompt = self._create_validation_prompt(rule, architecture_json, requirements)
            
            # 调用AI进行验证
            response = self.api_client._call_api(prompt)
            
            # 解析验证结果
            if "error" in response:
                logger.error(f"验证规则 {rule['name']} 时发生错误: {response['error']}")
                continue
                
            try:
                # 尝试从响应中提取验证结果
                validation_result = self._extract_validation_result(response)
                
                if not validation_result["is_valid"]:
                    violations.append({
                        "rule": rule["name"],
                        "description": validation_result.get("description", ""),
                        "reason": validation_result.get("reason", "不符合规则要求")
                    })
                    logger.warning(f"架构违反规则: {rule['name']} - {validation_result.get('reason', '不符合规则要求')}")
                else:
                    logger.info(f"架构符合规则: {rule['name']}")
            except Exception as e:
                logger.error(f"解析验证结果失败: {str(e)}")
                continue
        
        return len(violations) == 0, violations
    
    def _create_validation_prompt(self, rule: Dict[str, Any], architecture_json: str, requirements: str) -> str:
        """
        创建验证提示
        
        Args:
            rule: 规则
            architecture_json: 架构设计JSON字符串
            requirements: 用户需求
            
        Returns:
            str: 验证提示
        """
        prompt = f"""作为AWS解决方案架构师，请评估以下架构设计是否符合指定的架构规则。

## 架构规则
{rule['content']}

## 用户需求
{requirements}

## 架构设计
```json
{architecture_json}
```

请分析上述架构设计是否符合架构规则的要求。请提供详细的分析，并以JSON格式返回结果，包含以下字段：
- is_valid: 布尔值，表示架构是否符合规则
- description: 字符串，简要描述验证结果
- reason: 字符串，如果不符合规则，说明原因；如果符合规则，说明符合的方面

请直接返回JSON格式结果，不要添加其他说明。
"""
        return prompt
    
    def _extract_validation_result(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        从响应中提取验证结果
        
        Args:
            response: AI响应
            
        Returns:
            Dict: 验证结果
        """
        # 如果响应是字符串，尝试解析JSON
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except json.JSONDecodeError:
                pass
        
        # 如果响应包含content字段，尝试解析content
        if "content" in response and isinstance(response["content"], str):
            try:
                import re
                # 尝试从Markdown代码块中提取JSON
                json_match = re.search(r'```json\s*(.*?)\s*```', response["content"], re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)
                    return json.loads(json_text)
                
                # 尝试直接解析content
                return json.loads(response["content"])
            except (json.JSONDecodeError, AttributeError):
                pass
        
        # 如果响应直接包含验证结果字段
        if "is_valid" in response:
            return response
        
        # 默认返回验证失败
        logger.error(f"无法从响应中提取验证结果: {response}")
        return {
            "is_valid": False,
            "description": "无法解析验证结果",
            "reason": "验证过程出现错误"
        }
    
    def generate_improvement_prompt(self, architecture: Dict[str, Any], violations: List[Dict[str, Any]], requirements: str) -> str:
        """
        生成改进提示
        
        Args:
            architecture: 架构设计数据
            violations: 违反的规则列表
            requirements: 用户需求
            
        Returns:
            str: 改进提示
        """
        # 将架构转换为JSON字符串
        architecture_json = json.dumps(architecture, ensure_ascii=False, indent=2)
        
        prompt = """请根据以下反馈调整架构设计，确保符合公司架构规则：

## 原始需求
{0}

## 当前架构设计
```json
{1}
```

## 需要改进的地方
{2}

请调整架构设计，解决上述问题，同时保持原有架构的基本结构和满足用户需求。
请提供完整的调整后架构设计，包括架构概述、组件列表、架构图描述、设计决策和最佳实践。
请直接返回JSON格式结果，不要添加其他说明。
""".format(
            requirements,
            architecture_json,
            "\n".join([f"{i+1}. {v['rule']}: {v['reason']}" for i, v in enumerate(violations)])
        )
        
        return prompt