#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
架构生成模块
生成架构设计方案
"""

import os
import json
import re
from typing import Dict, Any, List
from src.api.qianwen_api import QianwenAPI
from src.core.requirement_analyzer import RequirementAnalyzer
from src.core.aws_best_practices import AWSBestPractices
from src.core.architecture_validator import ArchitectureValidator
from src.utils.logger import get_logger

# 获取日志记录器
logger = get_logger(__name__)

class ArchitectureGenerator:
    """架构生成器"""
    
    def __init__(self):
        """初始化架构生成器"""
        self.api_client = QianwenAPI()
        self.requirement_analyzer = RequirementAnalyzer()
        self.best_practices = AWSBestPractices()
        self.architecture_validator = ArchitectureValidator(api_client=self.api_client)
        logger.info ("架构生成器初始化完成，准备生成架构设计")
        logger.info(f"使用的千问API模型: {self.api_client.model}")
    
    def generate(self, requirements: str, stream_callback=None) -> Dict[str, Any]:
        """
        生成架构设计
        
        Args:
            requirements: 用户输入的需求
            stream_callback: 流式响应回调函数，用于实时显示生成结果
            
        Returns:
            Dict: 架构设计结果
        """
        # 分析需求
        logger.info("开始分析需求")
        analysis_result = self.requirement_analyzer.analyze(requirements)
        logger.info(f"需求分析结果: 系统类型={analysis_result.get('system_type')}, 复杂度={analysis_result.get('complexity')}")
        
        # 如果提供了回调函数，通知用户开始生成
        if stream_callback:
            stream_callback("开始生成架构设计...\n")
        
        # 调用API生成架构
        logger.info("调用千问API生成架构设计")
        architecture = self.api_client.generate_architecture(requirements, stream_callback)
        
        # 如果API调用失败，返回错误信息
        if "error" in architecture:
            logger.error(f"API调用失败: {architecture['error']}")
            return architecture
        
        # 如果返回的是content字段，尝试解析其中的JSON
        if "content" in architecture and isinstance(architecture["content"], str):
            logger.info("检测到content字段，尝试解析其中的JSON")
            architecture = self._extract_json_from_content(architecture["content"])
        
        # 增强架构设计
        logger.info("增强架构设计")
        if stream_callback:
            stream_callback("\n\n正在优化架构设计...\n")
        
        enhanced_architecture = self._enhance_architecture(architecture, analysis_result)
        
        # 验证架构是否符合公司规则
        logger.warning("===== 开始验证架构是否符合公司规则 =====")
        if stream_callback:
            stream_callback("\n\n正在验证架构是否符合公司规则...\n")
        
        # 打印当前规则文件列表
        rules_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                               "resources", "aws_patterns")
        if os.path.exists(rules_dir):
            rule_files = [f for f in os.listdir(rules_dir) if f.endswith('.md')]
            logger.warning(f"找到 {len(rule_files)} 个规则文件: {', '.join(rule_files)}")
            
            # 强制进行一次验证，确保验证逻辑正常工作
            is_valid, violations = self.architecture_validator.rule_validator.validate_architecture(
                enhanced_architecture, requirements)
            logger.warning(f"初步验证结果: 通过={is_valid}, 违规数={len(violations)}")
            if violations:
                for v in violations:
                    logger.warning(f"违规: {v['rule']} - {v['reason']}")
        else:
            logger.error(f"规则目录不存在: {rules_dir}")
        
        validated_architecture, violations, iterations = self.architecture_validator.validate_and_improve(
            enhanced_architecture, requirements, stream_callback)
        
        # 如果有违反规则，记录日志
        if violations:
            logger.warning(f"===== 架构验证完成，发现 {len(violations)} 个问题，经过 {iterations} 轮改进 =====")
            for i, v in enumerate(violations):
                logger.warning(f"剩余违反 {i+1}: {v['rule']} - {v['reason']}")
                
            if stream_callback:
                stream_callback(f"\n\n架构验证完成，发现 {len(violations)} 个问题，经过 {iterations} 轮改进")
                if violations:
                    violation_text = "\n".join([f"- {v['rule']}: {v['reason']}" for v in violations])
                    stream_callback(f"\n\n剩余问题:\n{violation_text}")
        else:
            logger.warning("===== 架构验证通过，符合所有公司规则！=====")
            if stream_callback:
                stream_callback("\n\n架构验证通过，符合所有公司规则！")
        
        if stream_callback:
            stream_callback("\n架构设计生成完成！")
        
        return validated_architecture
    
    def _extract_json_from_content(self, content: str) -> Dict[str, Any]:
        """
        从内容中提取JSON
        
        Args:
            content: 内容文本
            
        Returns:
            Dict: 提取的JSON对象
        """
        # 尝试从Markdown代码块中提取JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            logger.info("从Markdown代码块中提取JSON")
            json_text = json_match.group(1)
            try:
                return json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.warning(f"从Markdown代码块解析JSON失败: {str(e)}")
        
        # 尝试直接解析整个文本
        try:
            logger.info("尝试直接解析整个文本为JSON")
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning("直接解析JSON失败")
            
            # 如果无法解析，返回原始内容
            return {"content": content}
    
    def _enhance_architecture(self, architecture: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        增强架构设计
        
        Args:
            architecture: 原始架构设计
            analysis: 需求分析结果
            
        Returns:
            Dict: 增强后的架构设计
        """
        # 如果架构中没有最佳实践，添加最佳实践
        if "best_practices" not in architecture or not architecture["best_practices"]:
            logger.info("添加AWS最佳实践")
            system_type = analysis.get("system_type", "通用系统")
            best_practices = self.best_practices.get_best_practices(system_type, analysis)
            architecture["best_practices"] = best_practices
        
        # 确保架构图描述存在
        if "diagram_description" not in architecture or not architecture["diagram_description"].get("nodes"):
            logger.info("生成架构图描述")
            architecture["diagram_description"] = self._generate_diagram_description(architecture)
        else:
            logger.info(f"架构图描述已存在: {len(architecture['diagram_description'].get('nodes', []))}个节点")
        
        return architecture
    
    def _generate_diagram_description(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成架构图描述
        
        Args:
            architecture: 架构设计
            
        Returns:
            Dict: 架构图描述
        """
        # 初始化节点和连接
        nodes = []
        connections = []
        
        # 从组件列表生成节点
        if "components" in architecture:
            logger.info(f"从{len(architecture['components'])}个组件生成架构图描述")
            
            # 创建节点映射表，用于后续创建连接
            component_map = {}
            
            for i, component in enumerate(architecture["components"]):
                node_id = f"node_{i}"
                node_type = component.get("service_type", "EC2")
                node_name = component.get("name", f"Component {i}")
                
                # 存储组件名称到节点ID的映射
                component_map[node_name.lower()] = node_id
                
                nodes.append({
                    "id": node_id,
                    "type": node_type,
                    "name": node_name
                })
            
            # 尝试从组件描述中推断连接关系
            for i, component in enumerate(architecture["components"]):
                node_id = f"node_{i}"
                description = component.get("description", "")
                
                # 查找描述中提到的其他组件
                for other_name, other_id in component_map.items():
                    if other_id != node_id and other_name in description.lower():
                        # 创建连接
                        connections.append({
                            "from": node_id,
                            "to": other_id,
                            "label": ""
                        })
            
            # 如果没有找到连接，创建简单的链式连接
            if not connections and len(nodes) > 1:
                logger.info("未找到连接关系，创建简单的链式连接")
                for i in range(len(nodes) - 1):
                    connections.append({
                        "from": nodes[i]["id"],
                        "to": nodes[i + 1]["id"],
                        "label": ""
                    })
        
        logger.info(f"生成了{len(nodes)}个节点和{len(connections)}个连接")
        
        return {
            "nodes": nodes,
            "connections": connections
        }