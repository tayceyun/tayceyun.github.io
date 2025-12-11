---
sidebar: auto
tags:
  - aws
  - cloud
---

## AWS

### lAM Security Tools
#### lAM Credentials Report (account-level)
- a report that lists all your account's users and the status of their various credentials

#### lAM Access Advisor (user-level)
- Access advisor shows the service permissions granted to a user and when those services were last accessed.
- You can use this information to revise your policies.

### IAM Guidelines & Best Practices
- Don't use the root account except for AWS account setup
- One physical user = One AWS user
- Assign users to groups and assign permissions to groups
- Create a strong password policy
- Use and enforce the use of Multi Factor Authentication (MFA)
- Create and use Roles for giving permissions to AWS services
- Use Access Keys for Programmatic Access (CLl / SDK)
- Audit permissions of your account using lAM Credentials Report & lAMAccess Advisor
- Never share lAM users & Access Keys

### lAM Section-Summary
- Users: mapped to a physical user, has a password for AWS Console
- Groups: contains users only
- Policies: JSON document that outlines permissions for users or groups
- Roles: for EC2 instances or AWS services
- Security: MFA + Password Policy

- AWS CLl: manage your AWS services using the command-line
- AWS SDK: manage your AWS services using a programming language
- Access Keys: access AWS using the CLl or SDK
- Audit: lAM Credential Reports & lAM Access Advisor

## EC2
基础设施即服务

EC2 is one of the most popular of AWS' offering
EC2 = Elastic Compute Cloud = Infrastructure as a Service

It mainly consists in the capability of:
Renting virtual machines (EC2)
Storing data on virtual drives (EBS)
Distributing load across machines (ELB)
Scaling the services using an auto-scaling group (ASG)

Knowing EC2 is fundamental to understand how the Cloud works

### EC2 sizing & configuration options
Operating System (OS): Linux,Windows or Mac OS
How much compute power & cores (CPU)
How much random-access memory (RAM)

How much storage space:
Network-attached (EBS & EFS)
hardware (EC2 Instance Store)

Network card: speed of the card, Public IP address.
Firewall rules: security group
Bootstrap script (configure at first launch): EC2 User Data

### EC2 User Data
lt is possible to bootstrap our instances using an EC2 User data script,
bootstrapping means launching commands when a machine starts
That script is only run once at the instance first start

EC2 user data is used to automate boot tasks such as:
Installing updates
Installing software
Downloading common files from the internet
Anything you can think of

The EC2 User Data Script runs with the root user

### EC2 InstanceTypes -Overview
You can use different types of EC2 instances that are optimised fordifferent use cases (https://aws.amazon.com/ec2/instance-types/)

AWS has the following naming convention:
m5.2xlarge:
m: instance class
5:generation (AWS improves them over time)
2xlarge: size within the instance class


### use ssh access Ec2 with key pair
```bash
ssh -i ~/Downloads/ec2test.pem ec2-user@13.61.33.230

chmod 400 ~/Downloads/ec2test.pem

ssh -i ~/Downloads/ec2test.pem ec2-user@13.61.33.230

# 退出instance
exit
```

### Security Groups (安全组)

![安全组简介](/img/aws/security-groups-intro.png)

![安全组流量图解](/img/aws/security-groups-diagram.png)

![安全组深入了解](/img/aws/security-groups-deeper-dive.png)

![安全组须知](/img/aws/security-groups-good-to-know.png)

![引用其他安全组](/img/aws/other-security-group-diagram.png)

### Classic Ports (常用端口)

![常用端口](/img/aws/classic-ports.png)

### SSH 连接方式

![SSH 连接方式汇总](/img/aws/SSH-summary-table.png)

### EC2 Instances Purchasing Options (EC2 购买选项)

![EC2 购买选项概览](/img/aws/ec2-purchase-options.png)

#### EC2 Reserved Instances (预留实例)

![EC2 预留实例](/img/aws/ec2-reserved.png)

#### EC2 Savings Plans (节省计划)

![EC2 节省计划](/img/aws/ec2-saving-plan.png)

#### EC2 Spot Instances (竞价实例)

![EC2 竞价实例](/img/aws/ec2-spot.png)

#### EC2 Dedicated Hosts (专用主机)

![EC2 专用主机](/img/aws/ec2-dedicated-hosts.png)

#### EC2 Dedicated Instances (专用实例)

![EC2 专用实例](/img/aws/ec2-dedicated-instances.png)

#### EC2 Capacity Reservations (容量预留)

![EC2 容量预留](/img/aws/ec2-capacity-reservations.png)

#### AWS IPv4 地址收费

![IPv4 地址收费](/img/aws/charge-for-ipv4.png)

### EBS Volume (弹性块存储)

![EBS 卷概述](/img/aws/EBS-Volume.png)

![EBS 卷示例](/img/aws/ebs-volume-example.png)

#### EBS Delete on Termination (终止时删除)

![EBS 终止时删除](/img/aws/EBS-delete-on-termination.png)

#### EBS Snapshots (快照)

![EBS 快照](/img/aws/EBS-Snapshots.png)

![EBS 快照功能](/img/aws/EBS-Snapshots-Features.png)

### EBS volume types

![EBS 卷类型](/img/aws/EBS-volume-types.png)

https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html

#### General Purpose SSD (gp2/gp3)

![通用型 SSD](/img/aws/gp2-gp3.png)

#### Provisioned IOPS SSD (io1/io2)

![预配置 IOPS SSD](/img/aws/PIOPS%20SSD.png)

#### Hard Disk Drives (HDD)

![HDD 硬盘](/img/aws/HDD.png)

### EC2 Instance Store (实例存储)

![EC2 实例存储](/img/aws/EC2-instance-store.png)

### EBS Multi-Attach (多重挂载)

![EBS 多重挂载](/img/aws/EBS-Multi-Attach.png)

### AMI (Amazon Machine Image)

![AMI 概述](/img/aws/AMI-overview.png)

![AMI 创建流程](/img/aws/ami-process.png)

### Amazon EFS (弹性文件系统)

![EFS 概述](/img/aws/EFS-overview.png)

![EFS 特性](/img/aws/EFS-overview2.png)

#### EFS Performance & Storage Classes

![EFS 性能与存储类别](/img/aws/EFS-performance.png)

![EFS 存储类别](/img/aws/EFS-storage-class.png)

### EBS vs EFS 对比

![EBS 与 EFS 对比](/img/aws/diff%20between%20EBS%20and%20EFS.png)

### High Availability & Scalability (高可用性与可扩展性)

![高可用性与可扩展性](/img/aws/availability%26Scalability.png)

### Elastic Load Balancing (弹性负载均衡)

#### 什么是负载均衡

![什么是负载均衡](/img/aws/concept%20of%20load%20balancing.png)

#### 为什么使用负载均衡

![为什么使用负载均衡](/img/aws/load-balancer.png)

#### Why use an Elastic Load Balancer

![弹性负载均衡器](/img/aws/elastic-load-balancer.png)

#### Health Checks (健康检查)

![健康检查](/img/aws/health-check.png)

#### Load Balancer Security Groups

![负载均衡器安全组](/img/aws/load-balancer-security-groups.png)

### Application Load Balancer (ALB)

![应用负载均衡器](/img/aws/load-balancer-v2.png)

#### ALB Target Groups (目标组)

![ALB 目标组](/img/aws/v2-target-groups.png)

#### ALB Good to Know

![ALB 须知](/img/aws/v2-good-to-know.png)

### Network Load Balancer (NLB)

![网络负载均衡器](/img/aws/network-load-balancer.png)

---

## 📚 学习路线图 AWS Developer Associate (DVA-C02)

### 第一阶段：基础知识建立（2-3周）

#### 1. AWS 核心概念
- **AWS 全球基础设施**
  - 区域（Regions）和可用区（Availability Zones）
  - 边缘站点（Edge Locations）

**如何选择AWS区域？**

![How to choose an AWS Region](/img/images/aws/aws-region-choice.png)

选择AWS区域时需要考虑的关键因素：
- **合规性（Compliance）**：数据治理和法律要求 - 未经明确许可，数据不会离开区域
- **接近性（Proximity）**：客户的地理位置 - 降低延迟
- **可用服务（Available services）**：区域内的服务 - 新服务和新功能并非在每个区域都可用
- **定价（Pricing）**：不同区域的定价有所差异，具体可查看服务定价页面

- **AWS 共享责任模型**
- **AWS 服务概览**

#### 2. 身份和访问管理 (IAM)
- 用户、组、角色和策略
- 权限边界和服务控制策略
- 多因素认证 (MFA)
- AWS STS (Security Token Service)

#### 3. AWS CLI 和 SDK
- AWS CLI 配置和使用
- AWS SDK 基础（Python boto3, JavaScript, Java等）
- 凭证配置和管理

### 第二阶段：核心开发服务（3-4周）

#### 1. 计算服务
**Amazon EC2**
- 实例类型和定价模型
- 用户数据和元数据
- 安全组和网络ACL
- 弹性IP和弹性网络接口

**AWS Lambda**
- 函数创建和配置
- 触发器和事件源
- 环境变量和层（Layers）
- 冷启动和性能优化
- 错误处理和重试机制

**Amazon ECS & Fargate**
- 容器化应用部署
- 任务定义和服务
- 负载均衡集成

#### 2. 存储服务
**Amazon S3**
- 存储桶策略和ACL
- 版本控制和生命周期管理
- 跨区域复制
- 事件通知
- 预签名URL
- S3 Transfer Acceleration

**Amazon EBS**
- 卷类型和性能特征
- 快照和加密

**Amazon EFS**
- 网络文件系统配置
- 性能模式

#### 3. 数据库服务
**Amazon RDS**
- 数据库引擎选择
- 多可用区部署
- 读取副本
- 备份和恢复
- 参数组和选项组

**Amazon DynamoDB**
- 表设计和分区键
- 全局二级索引 (GSI) 和本地二级索引 (LSI)
- DynamoDB Streams
- 条件写入和原子计数器
- 批量操作

### 第三阶段：应用集成和消息传递（2-3周）

#### 1. 消息队列服务
**Amazon SQS**
- 标准队列 vs FIFO队列
- 死信队列 (DLQ)
- 长轮询 vs 短轮询
- 消息可见性超时

**Amazon SNS**
- 主题和订阅
- 消息过滤
- 扇出模式

#### 2. API 管理
**Amazon API Gateway**
- REST API vs HTTP API
- 授权和认证
- 请求/响应转换
- 缓存和限流
- CORS配置
- API密钥和使用计划

#### 3. 工作流编排
**AWS Step Functions**
- 状态机设计
- 错误处理和重试
- 并行和选择状态

### 第四阶段：监控、日志和调试（2周）

#### 1. 监控服务
**Amazon CloudWatch**
- 指标和警报
- 日志组和日志流
- CloudWatch Insights
- 自定义指标

**AWS X-Ray**
- 分布式追踪
- 服务映射
- 性能分析
- 注释和元数据

#### 2. 调试和故障排除
- 应用程序日志分析
- 性能瓶颈识别
- 错误处理最佳实践

### 第五阶段：安全和部署（2-3周）

#### 1. 安全服务
**AWS KMS**
- 密钥管理
- 信封加密
- 密钥策略

**AWS Secrets Manager**
- 密钥轮换
- 跨服务集成

**AWS Systems Manager Parameter Store**
- 参数层次结构
- 安全字符串参数

#### 2. 部署和CI/CD
**AWS CodeCommit**
- Git仓库管理

**AWS CodeBuild**
- 构建项目配置
- buildspec.yml

**AWS CodeDeploy**
- 部署配置
- 蓝绿部署和滚动部署

**AWS CodePipeline**
- 管道创建和管理
- 阶段和操作

**AWS CloudFormation**
- 模板语法
- 堆栈管理
- 嵌套堆栈
- 自定义资源

**AWS SAM (Serverless Application Model)**
- 无服务器应用部署
- 本地测试和调试

## 🛠️ 实践项目建议

### 项目1：无服务器Web应用
- **技术栈**：Lambda, API Gateway, DynamoDB, S3, CloudFront
- **功能**：用户注册、登录、数据CRUD操作

### 项目2：微服务架构
- **技术栈**：ECS, RDS, SQS, SNS, CloudWatch
- **功能**：订单处理系统

### 项目3：CI/CD管道
- **技术栈**：CodeCommit, CodeBuild, CodeDeploy, CodePipeline
- **功能**：自动化部署流程




