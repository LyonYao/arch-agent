#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
架构验证模块
负责验证架构设计并与大模型交互进行改进
"""

from typing import Dict, Any, List, Tuple, Optional

from src.api.base_api import BaseAPIClient
from src.core.ai_rule_validator import AIRuleValidator
from src.utils.logger import get_logger

# 获取日志记录器
logger = get_logger(__name__)

class ArchitectureValidator:
    """架构验证器"""
    
    def __init__(self, api_client=None, max_iterations: int = 3):
        """
        初始化架构验证器
        
        Args:
            api_client: API客户端，如果为None则创建新实例
            max_iterations: 最大迭代次数
        """
        # 使用APIFactory创建API客户端，确保使用当前选择的模型
        from src.api.api_factory import APIFactory
        self.api_client = api_client or APIFactory.create_api_client()
        self.rule_validator = AIRuleValidator(api_client=self.api_client)
        self.max_iterations = max_iterations
        logger.info(f"架构验证器初始化完成，使用模型: {self.api_client.model_name}，最大迭代次数: {self.max_iterations}")
    
    def validate(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证架构设计
        
        Args:
            architecture: 架构设计
            
        Returns:
            Dict[str, Any]: 验证结果，包含valid和message字段
        """
        # 检查规则验证器是否有规则
        if not self.rule_validator.rules:
            logger.warning("AI规则验证器没有加载任何规则，跳过验证过程")
            return {"valid": True, "message": "没有加载任何规则，跳过验证"}
            
        # 验证架构
        is_valid, violations = self.rule_validator.validate_architecture(architecture, "")
        
        if is_valid:
            return {"valid": True, "message": "架构验证通过"}
        else:
            violation_messages = [f"{v['rule']}: {v['reason']}" for v in violations]
            return {
                "valid": False, 
                "message": "架构验证失败:\n" + "\n".join(violation_messages)
            }
    
    def validate_and_improve(self, architecture: Dict[str, Any], requirements: str, 
                            callback=None) -> Tuple[Dict[str, Any], List[Dict[str, Any]], int]:
        """
        验证架构并进行改进
        
        Args:
            architecture: 初始架构设计
            requirements: 用户需求
            callback: 回调函数，用于更新进度
            
        Returns:
            Tuple[Dict, List, int]: (改进后的架构, 违反的规则列表, 迭代次数)
        """
        current_architecture = architecture
        iterations = 0
        final_violations = []
        
        # 检查规则验证器是否有规则
        if not self.rule_validator.rules:
            logger.warning("AI规则验证器没有加载任何规则，跳过验证过程")
            return current_architecture, [], iterations
            
        # 进行多轮验证和改进
        while iterations < self.max_iterations:
            # 验证当前架构
            logger.warning(f"===== 开始第 {iterations + 1} 轮AI架构规则验证 =====")
            is_valid, violations = self.rule_validator.validate_architecture(current_architecture, requirements)
            
            # 如果没有违反规则，则返回当前架构
            if is_valid:
                logger.warning(f"===== AI架构验证通过，无需改进 =====")
                return current_architecture, [], iterations
            
            # 记录当前违反的规则
            final_violations = violations
            logger.warning(f"===== 发现 {len(violations)} 个规则违反 =====")
            for i, v in enumerate(violations):
                logger.warning(f"违反 {i+1}: {v['rule']} - {v['reason']}")
            
            # 如果达到最大迭代次数，则停止
            if iterations >= self.max_iterations - 1:
                logger.warning(f"===== 达到最大迭代次数 {self.max_iterations}，停止改进 =====")
                break
            
            # 生成改进提示
            improvement_prompt = self.rule_validator.generate_improvement_prompt(
                current_architecture, violations, requirements)
            logger.warning(f"生成改进提示: {improvement_prompt[:200]}...")
            
            # 调用API进行改进
            logger.warning(f"===== 开始第 {iterations + 1} 轮AI架构改进 =====")
            if callback:
                callback(f"正在进行第 {iterations + 1} 轮AI架构规则验证和改进...\n\n发现 {len(violations)} 个问题需要修正：\n" + 
                         "\n".join([f"- {v['rule']}: {v['reason']}" for v in violations]))
            
            # 调用千问API生成改进后的架构
            improved_architecture = self.api_client.generate_architecture(improvement_prompt)
            
            # 检查API调用是否成功
            if "error" in improved_architecture:
                logger.error(f"API调用失败: {improved_architecture['error']}")
                break
            
            # 更新当前架构
            current_architecture = improved_architecture
            iterations += 1
            
            if callback:
                callback(f"完成第 {iterations} 轮架构改进。")
        
        # 返回最终架构、违反的规则和迭代次数
        return current_architecture, final_violations, iterations