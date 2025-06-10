#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图表生成模块
使用Diagrams库生成架构图
"""

import os
import tempfile
import logging
import shutil
import subprocess
from typing import Dict, Any, List, Optional

from diagrams import Diagram, Cluster, Edge
import diagrams.aws.compute as compute
import diagrams.aws.database as database
import diagrams.aws.network as network
import diagrams.aws.storage as storage
import diagrams.aws.security as security
import diagrams.aws.integration as integration
import diagrams.aws.management as management

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiagramGenerator:
    """架构图生成器"""
    
    def __init__(self):
        """初始化图表生成器"""
        # 检查Graphviz是否已安装
        self._check_graphviz()
        
        # AWS服务映射表，将服务类型映射到Diagrams库中的类
        self.service_map = {
            # 计算服务
            "EC2": compute.EC2,
            "Lambda": compute.Lambda,
            "ECS": compute.ECS,
            "Fargate": compute.Fargate,
            "EKS": compute.EKS,
            "ElasticBeanstalk": compute.ElasticBeanstalk,
            
            # 数据库服务
            "RDS": database.RDS,
            "DynamoDB": database.Dynamodb,
            "ElastiCache": database.ElastiCache,
            "Aurora": database.Aurora,
            "Redshift": database.Redshift,
            
            # 网络服务
            "VPC": network.VPC,
            "ELB": network.ELB,
            "ALB": network.ALB,
            "NLB": network.NLB,
            "CloudFront": network.CloudFront,
            "Route53": network.Route53,
            "APIGateway": network.APIGateway,
            
            # 存储服务
            "S3": storage.S3,
            "EFS": storage.EFS,
            "EBS": storage.EBS,
            
            # 安全服务
            "IAM": security.IAM,
            "Cognito": security.Cognito,
            "WAF": security.WAF,
            "Shield": security.Shield,
            
            # 集成服务
            "SQS": integration.SQS,
            "SNS": integration.SNS,
            "EventBridge": integration.Eventbridge,
            
            # 管理服务
            "CloudWatch": management.Cloudwatch,
            "CloudTrail": management.Cloudtrail,
            "CloudFormation": management.Cloudformation,
        }
    
    def _check_graphviz(self):
        """检查Graphviz是否已安装"""
        try:
            # 检查dot命令是否可用
            dot_path = shutil.which("dot")
            if not dot_path:
                logger.warning("未找到Graphviz的dot命令，架构图生成可能会失败")
                logger.warning("请安装Graphviz: https://graphviz.org/download/")
                logger.warning("Windows用户可以使用: choco install graphviz 或下载安装程序")
                logger.warning("安装后请确保将Graphviz的bin目录添加到系统PATH环境变量中")
            else:
                logger.info(f"找到Graphviz: {dot_path}")
        except Exception as e:
            logger.warning(f"检查Graphviz时出错: {str(e)}")
    
    def generate_diagram(self, architecture_data: Dict[str, Any]) -> str:
        """
        生成架构图
        
        Args:
            architecture_data: 架构设计数据
            
        Returns:
            str: 生成的图表文件路径
        """
        # 创建临时目录用于存储生成的图表
        temp_dir = tempfile.gettempdir()
        output_filename = "architecture_diagram"
        output_path = os.path.join(temp_dir, output_filename)
        
        # 从架构数据中提取节点和连接信息
        diagram_desc = architecture_data.get("diagram_description", {})
        
        # 如果没有diagram_description，尝试生成一个
        if not diagram_desc or not diagram_desc.get("nodes"):
            logger.info("未找到架构图描述，尝试从组件列表生成")
            diagram_desc = self._generate_diagram_description(architecture_data)
        
        nodes_data = diagram_desc.get("nodes", [])
        connections_data = diagram_desc.get("connections", [])
        
        logger.info(f"生成架构图: {len(nodes_data)}个节点, {len(connections_data)}个连接")
        
        # 创建节点字典，用于后续连接
        nodes = {}
        
        try:
            # 检查Graphviz是否可用
            self._verify_graphviz()
            
            # 使用Diagrams库生成图表
            with Diagram("AWS架构图", filename=output_path, show=False):
                # 创建节点
                for node_data in nodes_data:
                    node_id = node_data.get("id")
                    node_type = node_data.get("type")
                    node_name = node_data.get("name", node_id)
                    
                    logger.info(f"创建节点: {node_id}, 类型: {node_type}, 名称: {node_name}")
                    
                    # 获取对应的Diagrams类
                    service_class = self._get_service_class(node_type)
                    
                    if service_class:
                        # 创建节点
                        node = service_class(node_name)
                        nodes[node_id] = node
                
                # 创建连接
                for conn_data in connections_data:
                    from_id = conn_data.get("from")
                    to_id = conn_data.get("to")
                    label = conn_data.get("label", "")
                    
                    logger.info(f"创建连接: {from_id} -> {to_id}, 标签: {label}")
                    
                    if from_id in nodes and to_id in nodes:
                        # 创建连接
                        if label:
                            nodes[from_id] >> Edge(label=label) >> nodes[to_id]
                        else:
                            nodes[from_id] >> nodes[to_id]
            
            # Diagrams库会自动添加.png扩展名，所以这里不需要再添加
            final_path = output_path + ".png"
            logger.info(f"架构图生成完成: {final_path}")
            return final_path
        except Exception as e:
            logger.error(f"生成架构图时发生错误: {str(e)}")
            self._handle_graphviz_error(e)
            raise
    
    def _verify_graphviz(self):
        """验证Graphviz是否可用"""
        try:
            # 尝试运行dot命令
            result = subprocess.run(["dot", "-V"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Graphviz测试失败")
                raise RuntimeError("Graphviz不可用，请确保已正确安装")
            logger.info(f"Graphviz版本: {result.stderr.strip()}")
        except FileNotFoundError:
            logger.error("未找到Graphviz")
            raise RuntimeError("未找到Graphviz，请安装Graphviz并确保其在系统PATH中")
    
    def _handle_graphviz_error(self, error):
        """处理Graphviz错误"""
        error_str = str(error)
        if "failed to execute" in error_str and "dot" in error_str:
            logger.error("Graphviz执行失败，请确保已安装Graphviz并添加到系统PATH")
            logger.error("Windows安装指南: https://graphviz.org/download/")
            logger.error("1. 下载并安装Graphviz")
            logger.error("2. 将安装目录下的bin文件夹添加到系统PATH环境变量")
            logger.error("3. 重启应用程序")
    
    def _get_service_class(self, service_type: str):
        """
        获取服务对应的Diagrams类
        
        Args:
            service_type: 服务类型
            
        Returns:
            class: Diagrams库中的类
        """
        # 尝试直接匹配
        if service_type in self.service_map:
            return self.service_map[service_type]
        
        # 尝试模糊匹配
        for key, value in self.service_map.items():
            if key.lower() in service_type.lower():
                return value
        
        # 默认返回EC2
        logger.warning(f"未找到服务类型 {service_type} 对应的Diagrams类，使用EC2作为默认值")
        return compute.EC2
    
    def _generate_diagram_description(self, architecture_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从架构数据生成架构图描述
        
        Args:
            architecture_data: 架构设计数据
            
        Returns:
            Dict: 架构图描述
        """
        # 初始化节点和连接
        nodes = []
        connections = []
        
        # 从组件列表生成节点
        if "components" in architecture_data:
            for i, component in enumerate(architecture_data["components"]):
                node_id = f"node_{i}"
                node_type = component.get("service_type", "EC2")
                node_name = component.get("name", f"Component {i}")
                
                # 确保service_type是有效的
                if node_type not in self.service_map:
                    # 尝试找到最接近的服务类型
                    for key in self.service_map.keys():
                        if key.lower() in node_type.lower():
                            node_type = key
                            break
                    else:
                        node_type = "EC2"  # 默认使用EC2
                
                nodes.append({
                    "id": node_id,
                    "type": node_type,
                    "name": node_name
                })
            
            # 生成简单的连接（每个节点连接到下一个节点）
            for i in range(len(nodes) - 1):
                connections.append({
                    "from": nodes[i]["id"],
                    "to": nodes[i + 1]["id"],
                    "label": ""
                })
        
        logger.info(f"自动生成架构图描述: {len(nodes)}个节点, {len(connections)}个连接")
        
        return {
            "nodes": nodes,
            "connections": connections
        }