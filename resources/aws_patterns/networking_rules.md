# 网络架构规则

本文档定义了公司在AWS架构设计中必须遵循的网络架构规则。

## 规则条件

- 所有生产环境必须使用VPC，禁止使用EC2-Classic
- 必须使用私有子网部署应用和数据层组件
- 必须使用公有子网部署负载均衡器和堡垒主机
- 必须使用安全组和网络ACL实施多层防御
- 必须使用VPC端点访问AWS服务，避免通过公网访问
- 必须使用Transit Gateway或VPC Peering连接多个VPC
- 必须实施网络流量监控和异常检测

## 验证方法

验证架构是否符合网络分层原则，是否在架构概述、设计决策或最佳实践中明确提到了网络安全考虑。

## 示例实现

```json
{
  "components": [
    {
      "name": "虚拟私有云",
      "service_type": "VPC",
      "description": "包含公有子网和私有子网的VPC，实现网络隔离"
    },
    {
      "name": "应用负载均衡器",
      "service_type": "ALB",
      "description": "部署在公有子网中的ALB，将流量路由到私有子网中的应用服务器"
    },
    {
      "name": "VPC端点",
      "service_type": "VPC",
      "description": "使用VPC端点访问S3和DynamoDB，避免通过公网访问"
    }
  ]
}
```