# 服务选择规则

本文档定义了公司在AWS架构设计中的服务选择规则。

## 规则条件

- 必须使用AWS原生服务而非自建服务，除非有特殊需求
- 容器化应用必须使用ECS或EKS，禁止使用自建容器编排
- 关系型数据库优先使用Aurora而非RDS MySQL/PostgreSQL
- 禁止使用已被AWS标记为即将淘汰的服务
- 大数据处理必须使用EMR或Athena，禁止使用自建Hadoop集群
- 微服务架构必须使用App Mesh或ECS Service Discovery

## 验证方法

验证架构是否使用了公司推荐的AWS服务，是否避免了禁止使用的服务。

## 示例实现

```json
{
  "components": [
    {
      "name": "容器服务",
      "service_type": "ECS",
      "description": "使用ECS Fargate运行容器化应用，无需管理底层基础设施"
    },
    {
      "name": "数据库服务",
      "service_type": "Aurora",
      "description": "使用Aurora MySQL兼容版作为主数据库，提供高性能和高可用性"
    },
    {
      "name": "无服务器API",
      "service_type": "APIGateway",
      "description": "使用API Gateway和Lambda构建无服务器API"
    }
  ]
}
```