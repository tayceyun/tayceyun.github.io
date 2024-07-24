## Linux

### Linux 内核

![](/images/linux/内核.jpg)

### 安装虚拟机

#### 安装步骤

简而言之：通过软件模拟计算机硬件，并给虚拟硬件安装真实的操作系统

- vmware Fusion Pro
- centos 安装 linux 操作系统
- FinalShell（HOSTBUF） 远程连接到 linux 操作系统并操作

  - 登陆 vmshare，桌面打开终端，`ifconfig` --> ens33-inet ip 地址 --> 点击文件夹 --> +号 --> ssh 链接（linux）--> 配置名称/ip 地址/用户 --> 双击打开

### 基础命令

通用格式 `command [-options] [parameter]`

`man [command]`：查看文档

Linux 系统的命令行终端，在启动时会默认加载当前登录用户的 Home 目录

- 出现在开头的 / 表示：根目录
- 出现在后面的 / 表示：层次关系
- `ls [-a -l -h] [路径]`
  - `ls /`：查看根目录内容
  - `ls -a`：列出全部文件（包含隐藏的文件/文件夹）
  - `ls -l`：竖向列表展示文件（更多信息）
  - `ls -la` / `ls -al` / `ls -s -a` / `ls -lah`：组合使用
  - `ls -lh`：展示文件的大小单位
- `cd [路径]`
  - `cd `：切换到 home 目录
  - `cd /`：切换到根目录
  - `cd /home/test/Document`(绝对路径) 等同于 `cd Document`（相对路径）
    - `.`：表示当前目录
    - `..`：表示上一级目录。例：`cd ../../`: 向上 2 级目录
    - `~`：表示 home 目录
- `pwd`：查看当前所在的工作目录
- `mkdir`：创建新的目录/文件夹
  - `mkdir -p`：**自动创建不存在**的父目录，适用于创建连续多层级的目录
- `touch [文件名]`：创建文件
- `cat [路径]`：查看文件内容
- `more [路径]`：查看文件内容，支持通过空格翻页
- `cp [-r] 参数1 参数2`
  - `-r`：**复制文件夹**（表示递归）
  - 参数 1：linux 路径，表示被复制的文件或文件夹
  - 参数 2：linux 路径，表示要复制到的地方
- `mv 参数1 参数2`：移动文件/文件夹
  - 例：`mv test Doc/`：将文件移动到Doc目录下
  - 例：`mv test1.txt test2.txt`：如果test1文件存在而test2文件不存在，则 test1.txt会被更名为test2.txt
- `rm [-r -f] 参数1 参数2 ...`
  - `-r`：删除文件夹
  - `-f`：强制删除（不会弹出提示确认信息）
  - `*`：通配符
    - `test*`：表示匹配任何以test开头的内容
	- `*test`：表示匹配任何以test结尾的内容
	- `*test*`：表示匹配任何包含test的内容

