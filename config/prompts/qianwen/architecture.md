作为AWS解决方案架构师，请根据以下需求设计简洁的AWS架构方案。考虑AWS Well-Architected Framework的关键原则。

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
```json
{{
  "architecture_overview": "这是一个基于AWS的Web应用架构，使用EC2实例运行Web服务，Cognito进行用户认证，数据存储在DynamoDB中。该架构具有高可用性和可扩展性，适合处理变化的负载需求。",
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
    }},
    {{
      "name": "数据存储",
      "service_type": "DynamoDB",
      "description": "存储应用数据的NoSQL数据库"
    }}
  ],
  "diagram_description": {{
    "nodes": [
      {{"id": "web", "type": "EC2", "name": "Web服务器"}},
      {{"id": "auth", "type": "Cognito", "name": "用户认证服务"}},
      {{"id": "db", "type": "DynamoDB", "name": "数据存储"}}
    ],
    "connections": [
      {{"from": "web", "to": "auth", "label": "认证请求"}},
      {{"from": "web", "to": "db", "label": "数据操作"}}
    ]
  }},
  "design_decisions": [
    "使用EC2实例运行Web应用以提供灵活的配置和控制能力",
    "选择Cognito进行用户认证以减少开发工作量并提高安全性",
    "采用DynamoDB作为数据存储以获得高可用性和自动扩展能力"
  ],
  "best_practices": [
    "实施自动扩展以应对流量变化",
    "使用IAM角色管理服务间权限",
    "配置CloudWatch监控关键指标"
  ]
}}
```
注意：确保所有service_type和type字段都使用上述列出的AWS服务类型，不要使用"Service"或其他通用类型。
重要：在components和diagram_description中的name字段不能包含方括号[]、圆括号()等特殊字符，以确保生成的图表正确显示。