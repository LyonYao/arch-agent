#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gemini API调用模块
提供与Google Gemini大模型API的交互功能
"""

import os
import json
import re
import google.generativeai as genai
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from src.utils.logger import get_logger
from src.api.base_api import BaseAPIClient

# 加载环境变量
load_dotenv()

# 获取日志记录器
logger = get_logger(__name__)

class GeminiAPI(BaseAPIClient):
    """Gemini API客户端类"""
    
    def __init__(self):
        """初始化Gemini API客户端"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self._model = os.getenv("GEMINI_MODEL", "gemini-pro")  # 默认使用gemini-pro模型
        
        if not self.api_key:
            raise ValueError("未设置Gemini API密钥，请在.env文件中设置GEMINI_API_KEY")
        
        # 配置Google Generative AI SDK
        genai.configure(api_key=self.api_key)
        
        # 检查可用模型
        try:
            available_models = [model.name for model in genai.list_models()]
            logger.info(f"可用的Gemini模型: {available_models}")
            
            # 确保使用正确的模型名称
            if self._model not in available_models:
                # 尝试使用完整模型名称
                if f"models/{self._model}" in available_models:
                    self._model = f"models/{self._model}"
                # 或者尝试使用最新的gemini模型
                elif any("gemini" in model for model in available_models):
                    for model in available_models:
                        if "gemini" in model and "pro" in model:
                            self._model = model
                            break
                    else:
                        self._model = next(model for model in available_models if "gemini" in model)
                    
                logger.info(f"已调整为可用的模型: {self._model}")
        except Exception as e:
            logger.warning(f"获取可用模型列表失败: {str(e)}, 将使用默认模型名称")
        
        logger.info(f"初始化Gemini API客户端，使用模型: {self._model}")
    
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
            logger.info("调用Gemini API调整架构设计")
        else:
            prompt = self._create_architecture_prompt(requirements)
            logger.info("调用Gemini API生成架构设计")
            
        return self._call_api(prompt, stream_callback)
    
    def _create_architecture_prompt(self, requirements: str) -> str:
        """
        创建架构设计的提示词
        
        Args:
            requirements: 用户输入的系统需求描述
            
        Returns:
            str: 格式化的提示词
        """
        from src.utils.prompt_manager import PromptManager
        
        # 获取提示词模板
        prompt_manager = PromptManager()
        prompt_template = prompt_manager.get_prompt("gemini", "architecture")
        
        # 如果没有找到配置的提示词，使用默认提示词
        if not prompt_template:
            prompt_template = """作为AWS解决方案架构师，请根据以下需求设计简洁的AWS架构方案。考虑AWS Well-Architected Framework的关键原则。

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
SQS, SNS, EventBridge, CloudWatch, CloudTrail, CloudFormation"""
        
        # 格式化提示词
        return prompt_template.format(requirements)
    
    def _create_adjustment_prompt(self, requirements: str) -> str:
        """
        创建架构调整的提示词
        
        Args:
            requirements: 包含历史交互、当前架构和新需求的文本
            
        Returns:
            str: 格式化的提示词
        """
        from src.utils.prompt_manager import PromptManager
        
        # 获取提示词模板
        prompt_manager = PromptManager()
        prompt_template = prompt_manager.get_prompt("gemini", "adjustment")
        
        # 如果没有找到配置的提示词，使用默认提示词
        if not prompt_template:
            prompt_template = """作为AWS解决方案架构师，请根据以下信息简洁调整现有AWS架构方案。

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
SQS, SNS, EventBridge, CloudWatch, CloudTrail, CloudFormation"""
        
        # 格式化提示词
        return prompt_template.format(requirements)
    
    def _call_api(self, prompt: str, stream_callback=None) -> Dict[str, Any]:
        """
        调用Gemini API
        
        Args:
            prompt: 提示词
            stream_callback: 流式响应回调函数，接收部分响应文本
            
        Returns:
            Dict: API响应
        """
        try:
            logger.info(f"发送请求到Gemini API (模型: {self._model}, 流式模式: {stream_callback is not None})")
            
            # 获取模型
            # 尝试使用不同的模型名称格式
            try:
                model = genai.GenerativeModel(self._model)
            except Exception as model_error:
                logger.warning(f"使用模型名称 '{self._model}' 失败: {str(model_error)}")
                # 尝试使用不带前缀的模型名称
                if self._model.startswith("models/"):
                    try:
                        simple_model_name = self._model.split("/")[-1]
                        logger.info(f"尝试使用简化模型名称: {simple_model_name}")
                        model = genai.GenerativeModel(simple_model_name)
                        self._model = simple_model_name
                    except Exception:
                        # 如果还是失败，尝试使用默认的 "gemini-pro"
                        logger.info("尝试使用默认模型名称: gemini-pro")
                        model = genai.GenerativeModel("gemini-pro")
                        self._model = "gemini-pro"
                else:
                    # 尝试添加前缀
                    try:
                        prefixed_model_name = f"models/{self._model}"
                        logger.info(f"尝试使用带前缀的模型名称: {prefixed_model_name}")
                        model = genai.GenerativeModel(prefixed_model_name)
                        self._model = prefixed_model_name
                    except Exception:
                        # 如果还是失败，尝试使用默认的 "gemini-pro"
                        logger.info("尝试使用默认模型名称: gemini-pro")
                        model = genai.GenerativeModel("gemini-pro")
                        self._model = "gemini-pro"
            
            # 设置生成参数
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "max_output_tokens": 2000,
            }
            
            if stream_callback is not None:
                # 流式响应处理
                return self._handle_streaming_response(model, prompt, generation_config, stream_callback)
            else:
                # 普通响应处理
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                logger.info("收到Gemini API响应")
                return self._parse_response(response)
                
        except Exception as e:
            logger.error(f"API调用异常: {str(e)}")
            return {"error": str(e)}
    
    def _handle_streaming_response(self, model, prompt: str, generation_config: Dict[str, Any], 
                                 stream_callback) -> Dict[str, Any]:
        """
        处理流式API响应
        
        Args:
            model: Gemini模型实例
            prompt: 提示词
            generation_config: 生成参数
            stream_callback: 流式响应回调函数
            
        Returns:
            Dict: 完整的API响应
        """
        full_text = ""
        
        try:
            # 使用流式模式生成内容
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True
            )
            
            # 处理流式响应
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    # 计算增量文本
                    new_text = chunk.text
                    full_text += new_text
                    
                    # 调用回调函数处理增量文本
                    if stream_callback:
                        stream_callback(new_text)
            
            # 处理完整响应
            logger.info("流式响应接收完成")
            return self._parse_response({"text": full_text})
            
        except Exception as e:
            logger.error(f"流式响应处理失败: {str(e)}")
            return {"error": str(e)}
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """
        解析API响应
        
        Args:
            response: API原始响应
            
        Returns:
            Dict: 解析后的响应
        """
        try:
            # 根据Gemini API的实际响应格式进行解析
            logger.info("解析API响应")
            
            # 从响应中提取文本
            if isinstance(response, dict) and "text" in response:
                text = response["text"]
            elif hasattr(response, "text"):
                text = response.text
            else:
                text = str(response)
                
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
        
        except Exception as e:
            logger.error(f"解析响应失败: {str(e)}")
            return {"error": f"解析响应失败: {str(e)}", "raw_response": str(response)}