#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AWS最佳实践模块
提供AWS架构最佳实践
"""

from typing import Dict, Any, List

class AWSBestPractices:
    """AWS最佳实践类"""
    
    def __init__(self):
        """初始化AWS最佳实践"""
        # AWS Well-Architected Framework的六大支柱
        self.pillars = {
            "卓越运营": {
                "description": "运行和监控系统，持续改进流程和程序",
                "practices": [
                    "实施基础设施即代码(IaC)",
                    "使用CloudFormation或Terraform管理基础设施",
                    "实现小批量、可逆的变更",
                    "频繁优化运营程序",
                    "预见故障",
                    "从所有运营故障中学习",
                ]
            },
            "安全性": {
                "description": "保护信息、系统和资产",
                "practices": [
                    "实施强身份认证和授权机制",
                    "应用深度防御策略",
                    "自动化安全最佳实践",
                    "保护传输中和静态数据",
                    "为所有用户实施最小权限原则",
                    "为安全事件做好准备",
                ]
            },
            "可靠性": {
                "description": "确保工作负载按预期执行其功能",
                "practices": [
                    "自动从故障中恢复",
                    "横向扩展以增加工作负载可用性",
                    "停止猜测容量",
                    "通过自动化管理变更",
                    "测试恢复程序",
                    "使用多可用区部署提高可用性",
                ]
            },
            "性能效率": {
                "description": "有效使用计算资源",
                "practices": [
                    "使用无服务器架构",
                    "采用先进技术",
                    "全球部署",
                    "使用托管服务",
                    "根据指标优化架构",
                    "缓存数据和资产",
                ]
            },
            "成本优化": {
                "description": "避免不必要的成本",
                "practices": [
                    "采用消费模式",
                    "实施云财务管理",
                    "测量整体效率",
                    "停止在低级任务上花费资金",
                    "分析和归因支出",
                    "使用托管服务减少拥有成本",
                ]
            },
            "可持续性": {
                "description": "最大限度地减少环境影响",
                "practices": [
                    "了解您的影响",
                    "设定可持续发展目标",
                    "最大化利用率",
                    "预测和采用新的更高效的硬件和软件",
                    "使用托管服务",
                    "减少下游影响",
                ]
            }
        }
        
        # 常见架构模式
        self.patterns = {
            "Web应用": [
                "使用CloudFront作为CDN加速静态内容",
                "使用ALB实现负载均衡",
                "使用Auto Scaling Group实现弹性伸缩",
                "使用RDS作为关系型数据库",
                "使用ElastiCache缓存频繁访问的数据",
                "使用S3存储静态资源",
                "使用WAF防御Web攻击",
            ],
            "微服务": [
                "使用ECS或EKS部署容器化服务",
                "使用API Gateway管理API",
                "使用SQS实现服务间异步通信",
                "使用DynamoDB作为NoSQL数据库",
                "使用X-Ray进行分布式追踪",
                "使用Service Discovery服务发现",
            ],
            "无服务器": [
                "使用Lambda处理事件驱动的计算",
                "使用API Gateway创建无服务器API",
                "使用DynamoDB作为无服务器数据库",
                "使用S3触发Lambda函数",
                "使用Step Functions编排工作流",
                "使用EventBridge实现事件驱动架构",
            ],
            "数据处理": [
                "使用Kinesis处理实时数据流",
                "使用EMR进行大数据处理",
                "使用Glue进行ETL作业",
                "使用Redshift进行数据仓库",
                "使用Athena查询S3数据",
                "使用QuickSight可视化数据",
            ],
            "IoT": [
                "使用IoT Core管理设备连接",
                "使用IoT Analytics分析IoT数据",
                "使用Greengrass在边缘设备上运行代码",
                "使用IoT Events检测和响应事件",
                "使用IoT SiteWise监控工业设备",
            ],
        }
    
    def get_best_practices(self, system_type: str, requirements: Dict[str, Any]) -> List[str]:
        """
        获取适用的最佳实践
        
        Args:
            system_type: 系统类型
            requirements: 需求分析结果
            
        Returns:
            List[str]: 最佳实践列表
        """
        practices = []
        
        # 添加系统类型相关的最佳实践
        if system_type in self.patterns:
            practices.extend(self.patterns[system_type])
        
        # 根据需求关键词添加相关支柱的最佳实践
        keywords = requirements.get("keywords", {})
        
        if "高可用" in keywords:
            practices.extend(self.pillars["可靠性"]["practices"][:3])
        
        if "安全性" in keywords:
            practices.extend(self.pillars["安全性"]["practices"][:3])
        
        if "性能" in keywords:
            practices.extend(self.pillars["性能效率"]["practices"][:3])
        
        if "成本" in keywords:
            practices.extend(self.pillars["成本优化"]["practices"][:3])
        
        # 去重
        return list(set(practices))
    
    def get_all_pillars(self) -> Dict[str, Any]:
        """
        获取所有支柱信息
        
        Returns:
            Dict: 支柱信息
        """
        return self.pillars