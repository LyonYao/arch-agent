# 安全性规则

本文档定义了AWS架构设计中必须遵循的安全性规则。

## 规则条件

- 所有架构必须包含IAM组件，用于身份和访问管理
- 所有面向互联网的应用必须使用WAF进行Web应用防火墙保护
- 所有敏感数据必须加密存储，包括S3、RDS和EBS等存储服务
- 必须实施最小权限原则，避免过度授权
- 必须启用CloudTrail进行API调用日志记录
- 必须启用VPC Flow Logs记录网络流量

## 验证方法

验证架构是否包含必要的安全组件，以及是否在架构概述、设计决策或最佳实践中明确提到了安全性考虑。

## 示例实现

```json
{
  "components": [
    {
      "name": "身份和访问管理",
      "service_type": "IAM",
      "description": "管理用户身份和访问权限，实施最小权限原则"
    },
    {
      "name": "Web应用防火墙",
      "service_type": "WAF",
      "description": "保护Web应用免受常见Web漏洞攻击"
    },
    {
      "name": "API调用日志",
      "service_type": "CloudTrail",
      "description": "记录和监控所有AWS API调用"
    }
  ]
}
```