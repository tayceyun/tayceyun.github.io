---
sidebar: auto
tags:
  - docker
---

## 什么是 docker

docker 可以帮助我们跨平台快速运行应用、快速构建应用、快速分享应用(docker hub)。

- 使用 docker 构建应用：`docker build xxx`
- 使用 docker 分享应用：`docker push xxx`,`docker pull xxx`
- 使用 docker 运行应用：`docker pull xxx`,`docker run xxx`

![](/img/images/docker/基本原理.png)

### 理解容器

容器类似轻量级的 VM，共享操作系统内核，容器互相隔离。容器拥有自己的文件系统、CPU、内存、进程空间等。

![](/img/images/docker/容器.png)

### 登录云服务器

方式一：`ssh root@121.37.185.179`

方式二：配置服务器名称

- `vim ~/.ssh/config`

```bash
Host testDocker
HostName 121.37.185.179
User root
```

密码：Xuchao?123

登录：`ssh testDocker`

### 准备工作
- 安装docker(debain)：`apt install docker`
- 启动 docker：`systemctl start docker`
