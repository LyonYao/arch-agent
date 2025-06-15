#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mermaid图表生成模块
生成Mermaid格式的架构图
"""

import logging
from typing import Dict, Any, List

from src.utils.logger import get_logger

# 获取日志记录器
logger = get_logger(__name__)

class MermaidGenerator:
    """Mermaid架构图生成器"""
    
    def generate_diagram(self, architecture_data: Dict[str, Any]) -> str:
        """
        生成Mermaid格式的架构图
        
        Args:
            architecture_data: 架构设计数据
            
        Returns:
            str: Mermaid格式的架构图代码
        """
        # 从架构数据中提取节点和连接信息
        diagram_desc = architecture_data.get("diagram_description", {})
        
        # 如果没有diagram_description，返回空图
        if not diagram_desc or not diagram_desc.get("nodes"):
            logger.warning("未找到架构图描述，生成空图")
            return "graph TD\n  A[\"架构图\"] --> B[\"无数据\"]"
        
        nodes_data = diagram_desc.get("nodes", [])
        connections_data = diagram_desc.get("connections", [])
        
        logger.info(f"生成Mermaid架构图: {len(nodes_data)}个节点, {len(connections_data)}个连接")
        
        # 生成Mermaid图表代码
        mermaid_code = ["graph TD"]
        
        # 添加节点
        for node in nodes_data:
            node_id = node.get("id", "")
            node_name = node.get("name", "")
            node_type = node.get("type", "")
            
            # 确保节点名称和类型是字符串
            node_name = str(node_name) if node_name else ""
            node_type = str(node_type) if node_type else ""
            
            # 创建节点标签
            node_label = f"{node_name}<br/>{node_type}" if node_type else node_name
            
            # 根据节点类型设置不同的形状
            if "Database" in node_type or "Aurora" in node_type or "RDS" in node_type or "DynamoDB" in node_type:
                # 数据库使用圆柱形 - 正确的语法是 nodeId[("label")]
                mermaid_code.append(f"  {node_id}[({node_label})]")
            elif "Lambda" in node_type or "Function" in node_type:
                # Lambda函数使用六边形 - 正确的语法是 nodeId[/"label"/]
                mermaid_code.append(f"  {node_id}[{node_label}]")
            elif "S3" in node_type or "Storage" in node_type:
                # 存储使用圆角矩形 - 正确的语法是 nodeId["label"]
                mermaid_code.append(f"  {node_id}[{node_label}]")
            elif "API" in node_type or "Gateway" in node_type:
                # API使用菱形 - 正确的语法是 nodeId{"label"}
                 mermaid_code.append("  %s{%s}" % (node_id, node_label))
            else:
                # 默认使用矩形 - 正确的语法是 nodeId["label"]
                mermaid_code.append(f"  {node_id}[{node_label}]")
        
        # 添加连接
        for conn in connections_data:
            from_id = conn.get("from", "")
            to_id = conn.get("to", "")
            label = conn.get("label", "")
            if label:
                mermaid_code.append(f"  {from_id} -->|{label}| {to_id}")
            else:
                mermaid_code.append(f"  {from_id} --> {to_id}")
        
        # 添加样式
        mermaid_code.append("  classDef aws fill:#FF9900,stroke:#232F3E,color:#232F3E;")
        node_ids = [node.get("id", "") for node in nodes_data if node.get("id")]
        if node_ids:
            mermaid_code.append("  class " + ",".join(node_ids) + " aws;")
        
        return "\n".join(mermaid_code)