#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
千问API调用模块
提供与阿里千问大模型API的交互功能
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from src.utils.logger import get_logger
from src.api.base_api import BaseAPIClient

# 获取日志记录器
logger = get_logger(__name__)

class QianwenAPI(BaseAPIClient):
    """千问API客户端类"""
    
    def __init__(self):
        """初始化千问API客户端"""
        self.api_key = os.getenv("QIANWEN_API_KEY")
        self._model = os.getenv("QIANWEN_MODEL", "qwen-plus")  # 默认使用qwen-plus模型
        
        if not self.api_key:
            raise ValueError("未设置千问API密钥，请在.env文件中设置QIANWEN_API_KEY")
            
        # 导入dashscope库
        try:
            import dashscope
            self.dashscope = dashscope
            # 设置API密钥
            dashscope.api_key = self.api_key
            logger.info("成功导入dashscope库")
        except ImportError:
            logger.warning("未找到dashscope库，将使用requests库作为备选方案")
            self.dashscope = None
            import requests
            self.requests = requests
            self.api_url = os.getenv("QIANWEN_API_URL", 
                                   "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
            
        logger.info(f"初始化千问API客户端，使用模型: {self._model}")
    
    @property
    def model_name(self) -> str:
        """获取当前使用的模型名称"""
        return self._model
    
    def generate_architecture(self, requirements: str, stream_callback=None) -> Dict[str, Any]:
        """
        根据需求生成架构设计
        
        Args:
            requirements: 用户输入的系统需求描述
            stream_callback: 流式响应回调函数，用于实时显示生成结果
            
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
            
        return self._call_api(prompt, stream_callback)
    
    def _create_architecture_prompt(self, requirements: str) -> str:
        """
        创建架构设计的提示词
        
        Args:
            requirements: 用户输入的系统需求描述
            
        Returns:
            str: 格式化的提示词
        """
        prompt = """作为AWS解决方案架构师，请根据以下需求设计简洁的AWS架构方案。考虑AWS Well-Architected Framework的关键原则。

系统需求:
{0}

请提供以下内容(简明扼要):
1. 架构概述：简要描述整体架构设计(50-100字)
2. 架构组件：列出核心AWS服务及用途(每项15-30字)
3. 架构图：使用文本描述架构图的组件和连接关系
4. 设计决策：3-5条关键设计决策(每条20-40字)
5. 最佳实践：3-5条应用的AWS最佳实践(每条15-30字)

重要：在components和diagram_description中的name字段不能包含方括号[]、圆括号()等特殊字符，以确保生成的图表正确显示。

对于架构组件，必须使用以下AWS服务类型之一作为service_type字段的值：
EC2, Lambda, ECS, Fargate, EKS, ElasticBeanstalk, RDS, DynamoDB, ElastiCache, Aurora, Redshift, 
VPC, ELB, ALB, NLB, CloudFront, Route53, APIGateway, S3, EFS, EBS, IAM, Cognito, WAF, Shield, 
SQS, SNS, EventBridge, CloudWatch, CloudTrail, CloudFormation

对于架构图描述，使用以下JSON格式:
- nodes: 节点数组，每个节点包含id、type和name，其中type必须是上述AWS服务类型之一
- connections: 连接数组，每个连接包含from、to和label

请直接返回JSON格式结果，包含以下字段:
- architecture_overview: 架构概述
- components: 架构组件列表，每个组件包含name、service_type、description字段
- diagram_description: 架构图描述，包含nodes和connections
- design_decisions: 设计决策列表
- best_practices: 最佳实践列表

示例格式:
{{
  "components": [
    {{
      "name": "Web服务器",
      "service_type": "EC2",
      "description": "运行Web应用的EC2实例"
    }},
    {{
      "name": "用户认证服务",
      "service_type": "Cognito",
      "description": "管理用户身份验证和授权"
    }}
  ],
  "diagram_description": {{
    "nodes": [
      {{"id": "web", "type": "EC2", "name": "Web服务器"}},
      {{"id": "auth", "type": "Cognito", "name": "用户认证服务"}}
    ],
    "connections": [
      {{"from": "web", "to": "auth", "label": "认证请求"}}
    ]
  }}
}}

注意：确保所有service_type和type字段都使用上述列出的AWS服务类型，不要使用"Service"或其他通用类型。
重要：在components和diagram_description中的name字段不能包含方括号[]、圆括号()等特殊字符，以确保生成的图表正确显示。""".format(requirements)
        
        return prompt
    
    def _create_adjustment_prompt(self, requirements: str) -> str:
        """
        创建架构调整的提示词
        
        Args:
            requirements: 包含历史交互、当前架构和新需求的文本
            
        Returns:
            str: 格式化的提示词
        """
        prompt = """作为AWS解决方案架构师，请根据以下信息简洁调整现有AWS架构方案。

{0}

请提供调整后的架构设计，包含以下内容(简明扼要):
1. 架构概述：简要描述调整后的架构设计(50-100字)
2. 架构组件：列出核心AWS服务，重点说明新增、修改或删除的组件
3. 架构图：使用文本描述架构图的组件和连接关系
4. 设计决策：3-5条关键设计决策，特别是与原架构的差异
5. 最佳实践：3-5条应用的AWS最佳实践

重要：在components和diagram_description中的name字段不能包含方括号[]、圆括号()等特殊字符，以确保生成的图表正确显示。

对于架构组件，必须使用以下AWS服务类型之一作为service_type字段的值：
EC2, Lambda, ECS, Fargate, EKS, ElasticBeanstalk, RDS, DynamoDB, ElastiCache, Aurora, Redshift, 
VPC, ELB, ALB, NLB, CloudFront, Route53, APIGateway, S3, EFS, EBS, IAM, Cognito, WAF, Shield, 
SQS, SNS, EventBridge, CloudWatch, CloudTrail, CloudFormation

对于架构图描述，使用以下JSON格式:
- nodes: 节点数组，每个节点包含id、type和name，其中type必须是上述AWS服务类型之一
- connections: 连接数组，每个连接包含from、to和label

请直接返回JSON格式结果，包含以下字段:
- architecture_overview: 架构概述
- components: 架构组件列表，每个组件包含name、service_type、description字段
- diagram_description: 架构图描述，包含nodes和connections
- design_decisions: 设计决策列表
- best_practices: 最佳实践列表

示例格式:
{{
  "components": [
    {{
      "name": "Web服务器",
      "service_type": "EC2",
      "description": "运行Web应用的EC2实例"
    }},
    {{
      "name": "用户认证服务",
      "service_type": "Cognito",
      "description": "管理用户身份验证和授权"
    }}
  ],
  "diagram_description": {{
    "nodes": [
      {{"id": "web", "type": "EC2", "name": "Web服务器"}},
      {{"id": "auth", "type": "Cognito", "name": "用户认证服务"}}
    ],
    "connections": [
      {{"from": "web", "to": "auth", "label": "认证请求"}}
    ]
  }}
}}

注意：确保所有service_type和type字段都使用上述列出的AWS服务类型，不要使用"Service"或其他通用类型。
重要：在components和diagram_description中的name字段不能包含方括号[]、圆括号()等特殊字符，以确保生成的图表正确显示。""".format(requirements)
        
        return prompt
    
    def _call_api(self, prompt: str, stream_callback=None) -> Dict[str, Any]:
        """
        调用千问API
        
        Args:
            prompt: 提示词
            stream_callback: 流式响应回调函数，接收部分响应文本
            
        Returns:
            Dict: API响应
        """
        # 使用dashscope库调用API
        if self.dashscope:
            return self._call_api_with_dashscope(prompt, stream_callback)
        else:
            return self._call_api_with_requests(prompt, stream_callback)
    
    def _call_api_with_dashscope(self, prompt: str, stream_callback=None) -> Dict[str, Any]:
        """
        使用dashscope库调用千问API
        
        Args:
            prompt: 提示词
            stream_callback: 流式响应回调函数
            
        Returns:
            Dict: API响应
        """
        from dashscope import Generation
        
        try:
            logger.info(f"使用dashscope库调用千问API (模型: {self._model}, 流式模式: {stream_callback is not None})")
            
            # 设置参数
            parameters = {
                "temperature": 0.7,
                "top_p": 0.8,
                "result_format": "json",
                "max_tokens": 2000
            }
            
            if stream_callback:
                # 流式响应处理
                full_text = ""
                
                def handle_stream_response(response):
                    nonlocal full_text
                    if response.status_code == 200:
                        if response.output and response.output.text:
                            # 计算增量文本
                            new_text = response.output.text[len(full_text):]
                            full_text = response.output.text
                            
                            # 调用回调函数处理增量文本
                            if stream_callback and new_text:
                                stream_callback(new_text)
                    return True  # 继续接收流式响应
                
                # 发送流式请求
                response = Generation.call(
                    model=self._model,
                    prompt=prompt,
                    stream=True,
                    stream_callback=handle_stream_response,
                    **parameters
                )
                
                # 处理完整响应
                logger.info("流式响应接收完成")
                return self._parse_response({"output": {"text": full_text}})
            else:
                # 普通响应处理
                response = Generation.call(
                    model=self._model,
                    prompt=prompt,
                    **parameters
                )
                
                if response.status_code == 200:
                    logger.info("收到千问API响应")
                    return self._parse_response({"output": {"text": response.output.text}})
                else:
                    logger.error(f"API请求失败: {response.code}, {response.message}")
                    return {"error": f"API请求失败: {response.message}"}
                
        except Exception as e:
            logger.error(f"API调用异常: {str(e)}")
            return {"error": str(e)}
    
    def _call_api_with_requests(self, prompt: str, stream_callback=None) -> Dict[str, Any]:
        """
        使用requests库调用千问API
        
        Args:
            prompt: 提示词
            stream_callback: 流式响应回调函数
            
        Returns:
            Dict: API响应
        """
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 根据是否需要流式响应设置参数
        stream_mode = stream_callback is not None
        
        data = {
            "model": self._model,  # 使用配置的模型
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.8,
                "result_format": "json",
                "max_tokens": 2000,  # 限制输出长度以加快响应
                "stream": stream_mode  # 启用流式响应
            }
        }
        
        try:
            logger.info(f"使用requests库调用千问API (模型: {self._model}, 流式模式: {stream_mode})")
            
            # 添加重试机制
            max_retries = 2
            retry_count = 0
            timeout = 120  # 减少超时时间
            
            while retry_count <= max_retries:
                try:
                    if stream_mode:
                        # 流式响应处理
                        return self._handle_streaming_response(prompt, headers, data, stream_callback)
                    else:
                        # 普通响应处理
                        response = requests.post(self.api_url, headers=headers, json=data, timeout=timeout)
                        response.raise_for_status()
                        logger.info("收到千问API响应")
                        return self._parse_response(response.json())
                except requests.exceptions.Timeout:
                    retry_count += 1
                    logger.warning(f"API请求超时 (尝试 {retry_count}/{max_retries})")
                    if retry_count > max_retries:
                        return {"error": "API请求多次超时，请稍后再试"}
                except requests.exceptions.RequestException as e:
                    logger.error(f"API请求失败: {str(e)}")
                    return {"error": str(e)}
                
        except Exception as e:
            logger.error(f"API调用异常: {str(e)}")
            return {"error": str(e)}
    
    def _handle_streaming_response(self, prompt: str, headers: Dict[str, str], data: Dict[str, Any], 
                                 stream_callback) -> Dict[str, Any]:
        """
        处理流式API响应
        
        Args:
            prompt: 提示词
            headers: 请求头
            data: 请求数据
            stream_callback: 流式响应回调函数
            
        Returns:
            Dict: 完整的API响应
        """
        import requests
        
        full_text = ""
        
        try:
            with requests.post(self.api_url, headers=headers, json=data, stream=True, timeout=60) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        # 解析SSE格式的数据
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data:'):
                            json_str = line_text[5:].strip()
                            if json_str:
                                try:
                                    chunk_data = json.loads(json_str)
                                    if "output" in chunk_data and "text" in chunk_data["output"]:
                                        chunk_text = chunk_data["output"]["text"]
                                        # 计算增量文本
                                        new_text = chunk_text[len(full_text):]
                                        full_text = chunk_text
                                        
                                        # 调用回调函数处理增量文本
                                        if stream_callback and new_text:
                                            stream_callback(new_text)
                                except json.JSONDecodeError:
                                    logger.warning(f"无法解析流式响应片段: {json_str}")
            
            # 处理完整响应
            logger.info("流式响应接收完成")
            return self._parse_response({"output": {"text": full_text}})
            
        except Exception as e:
            logger.error(f"流式响应处理失败: {str(e)}")
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