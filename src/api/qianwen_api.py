#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
千问API调用模块
提供与阿里千问大模型API的交互功能
"""

import os
import json
import logging
import re
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QianwenAPI:
    """千问API客户端类"""
    
    def __init__(self):
        """初始化千问API客户端"""
        self.api_key = os.getenv("QIANWEN_API_KEY")
        self.api_url = os.getenv("QIANWEN_API_URL", 
                               "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
        
        if not self.api_key:
            raise ValueError("未设置千问API密钥，请在.env文件中设置QIANWEN_API_KEY")
    
    def generate_architecture(self, requirements: str) -> Dict[str, Any]:
        """
        根据需求生成架构设计
        
        Args:
            requirements: 用户输入的系统需求描述
            
        Returns:
            Dict: 包含架构设计的响应
        """
        # 检查是否是调整架构的请求
        is_adjustment = "基于以下历史交互和当前架构" in requirements and "新的调整需求" in requirements
        
        if is_adjustment:
            prompt = self._create_adjustment_prompt(requirements)
            logger.info("调用千问API调整架构设计")
        else:
            prompt = self._create_architecture_prompt(requirements)
            logger.info("调用千问API生成架构设计")
            
        return self._call_api(prompt)
    
    def _create_architecture_prompt(self, requirements: str) -> str:
        """
        创建架构设计的提示词
        
        Args:
            requirements: 用户输入的系统需求描述
            
        Returns:
            str: 格式化的提示词
        """
        prompt = """作为一名资深的AWS解决方案架构师，请根据以下系统需求设计一个合理的AWS架构方案。
请考虑AWS Well-Architected Framework的六大支柱（卓越运营、安全性、可靠性、性能效率、成本优化和可持续性）。

系统需求:
{0}

请提供以下内容:
1. 架构概述：简要描述整体架构设计
2. 架构组件：列出所有使用的AWS服务及其用途
3. 架构图：使用文本描述架构图的组件和连接关系，以便后续生成可视化图表
4. 设计决策：解释关键设计决策及其理由
5. 最佳实践：应用了哪些AWS最佳实践

对于架构图描述，请使用以下格式，以便Python Diagrams库可以正确生成图表:
- nodes: 包含所有节点信息的数组，每个节点包含id、type和name
  - id: 节点唯一标识符
  - type: AWS服务类型，必须是以下之一: EC2, Lambda, ECS, Fargate, EKS, ElasticBeanstalk, RDS, Dynamodb, ElastiCache, Aurora, Redshift, VPC, ELB, ALB, NLB, CloudFront, Route53, APIGateway, S3, EFS, EBS, IAM, Cognito, WAF, Shield, SQS, SNS, Eventbridge, Cloudwatch, Cloudtrail, Cloudformation
  - name: 节点显示名称
- connections: 包含所有连接信息的数组，每个连接包含from、to和label
  - from: 源节点的id
  - to: 目标节点的id
  - label: 连接的标签（可选）

请直接返回JSON格式结果，不要使用Markdown代码块，包含以下字段:
- architecture_overview: 架构概述
- components: 架构组件列表，每个组件包含name、service_type、description字段
- diagram_description: 架构图描述，包含nodes和connections
- design_decisions: 设计决策列表
- best_practices: 应用的最佳实践列表

示例架构图描述格式:
{{
  "diagram_description": {{
    "nodes": [
      {{"id": "web", "type": "EC2", "name": "Web服务器"}},
      {{"id": "db", "type": "RDS", "name": "数据库"}},
      {{"id": "s3", "type": "S3", "name": "静态资源"}}
    ],
    "connections": [
      {{"from": "web", "to": "db", "label": "读写数据"}},
      {{"from": "web", "to": "s3", "label": "存取文件"}}
    ]
  }}
}}
""".format(requirements)
        
        return prompt
    
    def _create_adjustment_prompt(self, requirements: str) -> str:
        """
        创建架构调整的提示词
        
        Args:
            requirements: 包含历史交互、当前架构和新需求的文本
            
        Returns:
            str: 格式化的提示词
        """
        prompt = """作为一名资深的AWS解决方案架构师，请根据以下信息调整现有的AWS架构方案。
请考虑AWS Well-Architected Framework的六大支柱（卓越运营、安全性、可靠性、性能效率、成本优化和可持续性）。

{0}

请提供调整后的架构设计，包含以下内容:
1. 架构概述：简要描述调整后的整体架构设计
2. 架构组件：列出所有使用的AWS服务及其用途，包括新增、修改或删除的组件
3. 架构图：使用文本描述架构图的组件和连接关系，以便后续生成可视化图表
4. 设计决策：解释关键设计决策及其理由，特别是与原架构的差异
5. 最佳实践：应用了哪些AWS最佳实践

对于架构图描述，请使用以下格式，以便Python Diagrams库可以正确生成图表:
- nodes: 包含所有节点信息的数组，每个节点包含id、type和name
  - id: 节点唯一标识符
  - type: AWS服务类型，必须是以下之一: EC2, Lambda, ECS, Fargate, EKS, ElasticBeanstalk, RDS, Dynamodb, ElastiCache, Aurora, Redshift, VPC, ELB, ALB, NLB, CloudFront, Route53, APIGateway, S3, EFS, EBS, IAM, Cognito, WAF, Shield, SQS, SNS, Eventbridge, Cloudwatch, Cloudtrail, Cloudformation
  - name: 节点显示名称
- connections: 包含所有连接信息的数组，每个连接包含from、to和label
  - from: 源节点的id
  - to: 目标节点的id
  - label: 连接的标签（可选）

请直接返回JSON格式结果，不要使用Markdown代码块，包含以下字段:
- architecture_overview: 架构概述
- components: 架构组件列表，每个组件包含name、service_type、description字段
- diagram_description: 架构图描述，包含nodes和connections
- design_decisions: 设计决策列表
- best_practices: 应用的最佳实践列表
""".format(requirements)
        
        return prompt
    
    def _call_api(self, prompt: str) -> Dict[str, Any]:
        """
        调用千问API
        
        Args:
            prompt: 提示词
            
        Returns:
            Dict: API响应
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "qwen-max",
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.8,
                "result_format": "json"
            }
        }
        
        try:
            logger.info("发送请求到千问API")
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            logger.info("收到千问API响应")
            return self._parse_response(response.json())
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            return {"error": str(e)}
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析API响应
        
        Args:
            response: API原始响应
            
        Returns:
            Dict: 解析后的响应
        """
        try:
            # 根据千问API的实际响应格式进行解析
            logger.info("解析API响应")
            if "output" in response and "text" in response["output"]:
                text = response["output"]["text"]
                logger.info(f"API返回文本: {text[:100]}...")  # 只记录前100个字符
                
                # 检查是否是Markdown代码块格式
                json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                if json_match:
                    logger.info("检测到Markdown代码块格式的JSON")
                    json_text = json_match.group(1)
                    try:
                        result = json.loads(json_text)
                        logger.info("成功解析JSON响应")
                        return result
                    except json.JSONDecodeError as e:
                        logger.warning(f"从Markdown代码块解析JSON失败: {str(e)}")
                
                # 尝试直接解析整个文本
                try:
                    result = json.loads(text)
                    logger.info("成功解析JSON响应")
                    return result
                except json.JSONDecodeError as e:
                    logger.warning(f"直接解析JSON失败: {str(e)}")
                    
                    # 如果解析失败，返回原始内容
                    return {"content": text}
            
            return response
        except Exception as e:
            logger.error(f"解析响应失败: {str(e)}")
            return {"error": f"解析响应失败: {str(e)}", "raw_response": response}