#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
架构规则验证模块
用于验证生成的架构是否符合公司架构设计规则
"""

import os
import re
import json
from typing import Dict, Any, List, Tuple, Optional

from src.utils.logger import get_logger

# 获取日志记录器
logger = get_logger(__name__)

class RuleValidator:
    """架构规则验证器"""
    
    def __init__(self, rules_dir: str = None):
        """
        初始化规则验证器
        
        Args:
            rules_dir: 规则文件目录，如果为None则使用默认目录
        """
        logger.warning("初始化规则验证器")
        
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
                        # 解析规则文件
                        rule = self._parse_rule_file(file_path)
                        if rule:
                            rules.append(rule)
                            logger.warning(f"已加载规则: {rule['name']} ({file_path})")
                    except Exception as e:
                        logger.error(f"解析规则文件 {file_path} 失败: {str(e)}")
            logger.warning(f"共加载 {file_cnt} 个规则文件")
        except Exception as e:
            logger.error(f"加载规则失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
        return rules
    
    def _parse_rule_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析规则文件
        
        Args:
            file_path: 规则文件路径
            
        Returns:
            Dict: 规则字典
        """
        logger.warning(f"解析规则文件: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.info(f"文件内容长度: {len(content)} 字符")
        except Exception as e:
            logger.error(f"读取文件失败: {str(e)}")
            raise
            
        # 提取规则名称（文件的第一个标题）
        name_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        name = name_match.group(1) if name_match else os.path.basename(file_path)
        
        # 提取规则描述（名称后的第一段文本）
        description_match = re.search(r"^#\s+.+\n\n(.+?)(?=\n\n|\n#|$)", content, re.DOTALL)
        description = description_match.group(1).strip() if description_match else ""
        
        # 提取规则条件（## 规则条件 部分）
        conditions_match = re.search(r"^##\s+规则条件\s*\n(.*?)(?=\n##|$)", content, re.DOTALL | re.MULTILINE)
        conditions_text = conditions_match.group(1).strip() if conditions_match else ""
        
        # 解析条件列表
        conditions = []
        if conditions_text:
            for line in conditions_text.split("\n"):
                line = line.strip()
                if line.startswith("- ") or line.startswith("* "):
                    conditions.append(line[2:].strip())
        
        # 提取验证方法（## 验证方法 部分）
        validation_match = re.search(r"^##\s+验证方法\s*\n(.*?)(?=\n##|$)", content, re.DOTALL | re.MULTILINE)
        validation = validation_match.group(1).strip() if validation_match else ""
        
        return {
            "name": name,
            "description": description,
            "conditions": conditions,
            "validation": validation,
            "file_path": file_path
        }
    
    def validate_architecture(self, architecture: Dict[str, Any], requirements: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        验证架构是否符合规则
        
        Args:
            architecture: 架构设计数据
            requirements: 用户需求
            
        Returns:
            Tuple[bool, List]: (是否全部通过, 违反的规则列表)
        """
        violations = []
        
        # 检查每条规则
        for rule in self.rules:
            # 检查规则是否适用于当前架构
            if self._is_rule_applicable(rule, architecture, requirements):
                # 验证规则
                is_valid, reason = self._validate_rule(rule, architecture)
                if not is_valid:
                    violations.append({
                        "rule": rule["name"],
                        "description": rule["description"],
                        "reason": reason
                    })
                    logger.warning(f"架构违反规则: {rule['name']} - {reason}")
                else:
                    logger.info(f"架构符合规则: {rule['name']}")
        
        return len(violations) == 0, violations
    
    def _is_rule_applicable(self, rule: Dict[str, Any], architecture: Dict[str, Any], requirements: str) -> bool:
        """
        检查规则是否适用于当前架构
        
        Args:
            rule: 规则
            architecture: 架构设计数据
            requirements: 用户需求
            
        Returns:
            bool: 是否适用
        """
        # 默认所有规则都适用
        # 可以根据需要实现更复杂的逻辑，例如根据架构类型、服务组合等判断
        return True
    
    def _validate_rule(self, rule: Dict[str, Any], architecture: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证架构是否符合规则
        
        Args:
            rule: 规则
            architecture: 架构设计数据
            
        Returns:
            Tuple[bool, str]: (是否通过, 不通过原因)
        """
        # 检查架构组件
        if "components" in architecture:
            components = architecture["components"]
            
            # 检查每个条件
            for condition in rule["conditions"]:
                # 安全性规则检查
                if "安全" in condition or "IAM" in condition:
                    if not self._check_security_components(components, condition):
                        return False, f"不满足安全条件: {condition}"
                
                # 高可用性规则检查
                if "高可用" in condition or "多可用区" in condition:
                    if not self._check_high_availability(components, architecture, condition):
                        return False, f"不满足高可用条件: {condition}"
                
                # 成本优化规则检查
                if "成本" in condition or "优化" in condition:
                    if not self._check_cost_optimization(components, architecture, condition):
                        return False, f"不满足成本优化条件: {condition}"
                
                # 服务组合规则检查
                if "必须使用" in condition or "禁止使用" in condition:
                    if not self._check_service_requirements(components, condition):
                        return False, f"不满足服务要求: {condition}"
        
        return True, ""
    
    def _check_security_components(self, components: List[Dict[str, Any]], condition: str) -> bool:
        """检查安全相关组件"""
        # 检查是否包含IAM组件
        if "IAM" in condition and not any(c.get("service_type") == "IAM" for c in components):
            return False
        
        # 检查是否包含安全组件
        security_services = ["WAF", "Shield", "GuardDuty", "SecurityHub", "IAM"]
        if "安全组件" in condition and not any(c.get("service_type") in security_services for c in components):
            return False
            
        return True
    
    def _check_high_availability(self, components: List[Dict[str, Any]], architecture: Dict[str, Any], condition: str) -> bool:
        """检查高可用性"""
        # 检查是否提到多可用区
        overview = architecture.get("architecture_overview", "").lower()
        decisions = " ".join(architecture.get("design_decisions", [])).lower()
        
        if "多可用区" in condition and "多可用区" not in overview and "多可用区" not in decisions:
            return False
            
        return True
    
    def _check_cost_optimization(self, components: List[Dict[str, Any]], architecture: Dict[str, Any], condition: str) -> bool:
        """检查成本优化"""
        # 检查是否考虑了成本优化
        best_practices = " ".join(architecture.get("best_practices", [])).lower()
        decisions = " ".join(architecture.get("design_decisions", [])).lower()
        
        if "成本优化" in condition and "成本" not in best_practices and "成本" not in decisions:
            return False
            
        return True
    
    def _check_service_requirements(self, components: List[Dict[str, Any]], condition: str) -> bool:
        """检查服务要求"""
        # 检查必须使用的服务
        if "必须使用" in condition:
            required_service = re.search(r"必须使用\s+(\w+)", condition)
            if required_service:
                service_name = required_service.group(1)
                if not any(service_name.lower() in c.get("service_type", "").lower() for c in components):
                    return False
        
        # 检查禁止使用的服务
        if "禁止使用" in condition:
            forbidden_service = re.search(r"禁止使用\s+(\w+)", condition)
            if forbidden_service:
                service_name = forbidden_service.group(1)
                if any(service_name.lower() in c.get("service_type", "").lower() for c in components):
                    return False
                    
        return True
    
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
        prompt = "请根据以下反馈调整架构设计，确保符合公司架构规则：\n\n"
        
        # 添加原始需求
        prompt += f"原始需求：\n{requirements}\n\n"
        
        # 添加当前架构概述
        if "architecture_overview" in architecture:
            prompt += f"当前架构概述：\n{architecture['architecture_overview']}\n\n"
        
        # 添加违反的规则
        prompt += "需要改进的地方：\n"
        for i, violation in enumerate(violations, 1):
            prompt += f"{i}. {violation['rule']}: {violation['reason']}\n"
            if violation['description']:
                prompt += f"   说明: {violation['description']}\n"
        
        # 添加改进要求
        prompt += "\n请调整架构设计，解决上述问题，同时保持原有架构的基本结构和满足用户需求。"
        prompt += "\n请提供完整的调整后架构设计，包括架构概述、组件列表、架构图描述、设计决策和最佳实践。"
        
        return prompt