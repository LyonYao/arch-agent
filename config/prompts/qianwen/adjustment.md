作为AWS解决方案架构师，请根据以下信息简洁调整现有AWS架构方案。

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
```json
{{
  "architecture_overview": "调整后的架构增加了负载均衡和自动扩展能力，提高了系统的可用性和性能。新增了CloudFront内容分发网络加速静态内容交付，并使用RDS替代了原有的数据库解决方案以提升数据管理能力。",
  "components": [
    {{
      "name": "Web服务器集群",
      "service_type": "EC2",
      "description": "运行Web应用的EC2实例集群"
    }},
    {{
      "name": "负载均衡器",
      "service_type": "ALB",
      "description": "分发流量到Web服务器集群"
    }},
    {{
      "name": "用户认证服务",
      "service_type": "Cognito",
      "description": "管理用户身份验证和授权"
    }},
    {{
      "name": "关系数据库",
      "service_type": "RDS",
      "description": "存储应用结构化数据"
    }},
    {{
      "name": "内容分发网络",
      "service_type": "CloudFront",
      "description": "加速静态内容交付"
    }}
  ],
  "diagram_description": {{
    "nodes": [
      {{"id": "cf", "type": "CloudFront", "name": "内容分发网络"}},
      {{"id": "alb", "type": "ALB", "name": "负载均衡器"}},
      {{"id": "web", "type": "EC2", "name": "Web服务器集群"}},
      {{"id": "auth", "type": "Cognito", "name": "用户认证服务"}},
      {{"id": "db", "type": "RDS", "name": "关系数据库"}}
    ],
    "connections": [
      {{"from": "cf", "to": "alb", "label": "动态内容请求"}},
      {{"from": "alb", "to": "web", "label": "负载均衡"}},
      {{"from": "web", "to": "auth", "label": "认证请求"}},
      {{"from": "web", "to": "db", "label": "数据操作"}}
    ]
  }},
  "design_decisions": [
    "引入ALB实现负载均衡，提高系统可用性和扩展性",
    "使用CloudFront加速静态内容交付，改善全球用户访问体验",
    "从DynamoDB迁移到RDS，以支持更复杂的查询和事务需求"
  ],
  "best_practices": [
    "实施多可用区部署以提高系统可用性",
    "配置自动扩展组应对流量变化",
    "使用RDS读取副本分担数据库读取负载"
  ]
}}
```
注意：确保所有service_type和type字段都使用上述列出的AWS服务类型，不要使用"Service"或其他通用类型。
重要：在components和diagram_description中的name字段不能包含方括号[]、圆括号()等特殊字符，以确保生成的图表正确显示。