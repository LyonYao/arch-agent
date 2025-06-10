#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
架构生成模块
生成架构设计方案
"""

import logging
import json
import re
from typing import Dict, Any, List
from src.api.qianwen_api import QianwenAPI
from src.core.requirement_analyzer import RequirementAnalyzer
from src.core.aws_best_practices import AWSBestPractices

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArchitectureGenerator:
    """架构生成器"""
    
    def __init__(self):
        """初始化架构生成器"""
        self.api_client = QianwenAPI()
        self.requirement_analyzer = RequirementAnalyzer()
        self.best_practices = AWSBestPractices()
    
    def generate(self, requirements: str) -> Dict[str, Any]:
        """
        生成架构设计
        
        Args:
            requirements: 用户输入的需求
            
        Returns:
            Dict: 架构设计结果
        """
        # 分析需求
        logger.info("开始分析需求")
        analysis_result = self.requirement_analyzer.analyze(requirements)
        logger.info(f"需求分析结果: 系统类型={analysis_result.get('system_type')}, 复杂度={analysis_result.get('complexity')}")
        
        # 调用API生成架构
        logger.info("调用千问API生成架构设计")
        architecture = self.api_client.generate_architecture(requirements)
        
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
        enhanced_architecture = self._enhance_architecture(architecture, analysis_result)
        
        return enhanced_architecture
    
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