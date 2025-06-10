#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
需求分析模块
分析用户输入的需求
"""

from typing import Dict, Any, List

class RequirementAnalyzer:
    """需求分析器"""
    
    def __init__(self):
        """初始化需求分析器"""
        # 关键词列表，用于识别需求中的关键点
        self.keywords = {
            "高可用": ["高可用", "可用性", "容错", "故障转移", "冗余"],
            "安全性": ["安全", "加密", "认证", "授权", "防火墙", "WAF"],
            "性能": ["性能", "响应时间", "吞吐量", "延迟", "并发"],
            "成本": ["成本", "预算", "费用", "开销", "经济"],
            "可扩展性": ["扩展", "伸缩", "弹性", "增长", "扩容"],
            "数据处理": ["数据", "存储", "数据库", "分析", "大数据"],
            "用户量": ["用户", "访问量", "流量", "PV", "UV"],
            "实时性": ["实时", "即时", "低延迟", "流处理"],
            "批处理": ["批处理", "定时任务", "离线处理"],
            "监控": ["监控", "告警", "日志", "追踪", "可观测性"],
        }
    
    def analyze(self, requirements: str) -> Dict[str, Any]:
        """
        分析需求
        
        Args:
            requirements: 用户输入的需求
            
        Returns:
            Dict: 分析结果
        """
        # 初始化结果
        result = {
            "keywords": {},
            "system_type": self._detect_system_type(requirements),
            "complexity": self._estimate_complexity(requirements),
        }
        
        # 识别关键词
        for category, words in self.keywords.items():
            count = 0
            for word in words:
                if word in requirements:
                    count += 1
            
            if count > 0:
                result["keywords"][category] = count
        
        return result
    
    def _detect_system_type(self, requirements: str) -> str:
        """
        检测系统类型
        
        Args:
            requirements: 用户输入的需求
            
        Returns:
            str: 系统类型
        """
        # 系统类型关键词
        system_types = {
            "Web应用": ["网站", "Web", "网页", "HTTP", "浏览器"],
            "移动应用": ["移动", "手机", "APP", "iOS", "Android"],
            "数据处理": ["数据处理", "分析", "ETL", "大数据", "数据仓库"],
            "IoT": ["IoT", "物联网", "传感器", "设备", "嵌入式"],
            "微服务": ["微服务", "服务网格", "容器", "Docker", "Kubernetes"],
            "无服务器": ["无服务器", "Serverless", "Lambda", "函数计算"],
            "混合云": ["混合云", "多云", "本地", "私有云", "公有云"],
        }
        
        # 计算每种类型的匹配度
        scores = {}
        for system_type, keywords in system_types.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in requirements.lower():
                    score += 1
            
            if score > 0:
                scores[system_type] = score
        
        # 返回得分最高的类型，如果没有匹配则返回"通用系统"
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        else:
            return "通用系统"
    
    def _estimate_complexity(self, requirements: str) -> str:
        """
        估计系统复杂度
        
        Args:
            requirements: 用户输入的需求
            
        Returns:
            str: 复杂度级别
        """
        # 简单的复杂度估计，基于文本长度和关键词数量
        length = len(requirements)
        keyword_count = sum(1 for category, words in self.keywords.items() 
                          for word in words if word in requirements)
        
        if length < 200 and keyword_count < 3:
            return "简单"
        elif length > 500 or keyword_count > 8:
            return "复杂"
        else:
            return "中等"