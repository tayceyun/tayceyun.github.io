## Linux

### Linux 内核

![](/img/images/linux/内核.jpg)

### 安装虚拟机

#### 安装步骤

简而言之：通过软件模拟计算机硬件，并给虚拟硬件安装真实的操作系统

- vmware Fusion Pro
- centos 安装 linux 操作系统
- FinalShell（HOSTBUF） 远程连接到 linux 操作系统并操作

  - 登陆 vmshare，桌面打开终端，`ifconfig` --> ens33-inet ip 地址 --> 点击文件夹 --> +号 --> ssh 链接（linux）--> 配置名称/ip 地址/用户 --> 双击打开

### 基础命令

通用格式 `command [-options] [parameter]`

查看文档：1️⃣`man [command]`；2️⃣`man ls`

查看帮助：1️⃣Bash command：`help echo`；2️⃣Other command：`echo --help`

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

- `head 文件名`：默认查看文件前十行
  - `head -c [n]`：查看文件前 n 个字节的内容
  - `head -n [n]`：查看文件前 n 行的内容
- `more [路径]`：查看文件内容，支持通过空格翻页

- `tail 文件名`：默认查看文件最后十行

  - `tail -n [n]`：查看文件后 n 行的内容
  - `tail -f 文件名`：查看文件实时更新的后十行的内容

- `cp [-r] 参数1 参数2`

  - `-r`：**复制文件夹**（表示递归）
  - 参数 1：linux 路径，表示被复制的文件或文件夹
  - 参数 2：linux 路径，表示要复制到的地方

- `mv 参数1 参数2`：移动文件/文件夹

  - `mv -b directory1 directory2`：当文件存在时，覆盖前会创建一个备份
  - 例：`mv test Doc/`：将文件移动到 Doc 目录下
  - 例：`mv test1.txt test2.txt`：如果 test1 文件存在而 test2 文件不存在，则 test1.txt 会被更名为 test2.txt
  - 例：`mv file_1 file_2 /somedirectory`：移动多个文件

- `rm [-r -f] 参数1 参数2 ...`

  - `-r`：删除文件夹
  - `-f`：强制删除（不会弹出提示确认信息）
  - `*`：通配符
    - `test*`：表示匹配任何以 test 开头的内容
  - `*test`：表示匹配任何以 test 结尾的内容
  - `*test*`：表示匹配任何包含 test 的内容

- `rmdir directory`：删除文件夹
- `file test.jpg`：查看文件类型描述

- `find /home -name puppies.jpg`：在 home 目录下搜索名为`puppies.jpg`的文件

  - `find /home -type d -name MyFolder`：在 home 目录下搜索名为`MyFolder`的目录

- `whatis cat`：查看命令描述

- `alias gittree='git log --graph --full-history --all --oneline'`：设置别名（以 gittree 为例）

  - `unalias gittree`：移除别名

- exit from the shell：1️⃣`exit`；2️⃣`logout`

- `echo`

  - `echo Hello World >> peanuts.txt`：将 hello world 写入至 txt 文档中
  - `echo Hello World > peanuts.txt`：hello world 将覆盖掉 txt 的原内容
  - 新建/编辑文件内容,`>`和`>>`的区别在于：`>>`不会覆盖文件的原内容

![](/img/images/linux/output.png)

- `expand` & `unexpand`： tab 符和 空格 互相转换
- `join` & `split`：文件内容合并与分割
- `sort`：文件内容排序
  - `-r`：反向排序
  - `-n`：按数字大小排序
- ` tr a-z A-Z`：将输入的小写字母转为大写字母
- `uniq`：文件内容去重
  - `-u`：去重后留下 没有重复的内容
  - `-d`：去重后留下 存在重复的内容
  - `-c`：统计重复内容出现的次数
- `wc [OPTION] [FILE...]`：count the number of lines, words, characters, and bytes in files
  - -l: Counts the number of lines.
  - -w: Counts the number of words.
  - -c: Counts the number of bytes.
  - -m: Counts the number of characters (different from bytes in some cases, such as with multi-byte characters).
  - -L: Displays the length of the longest line in the file.
- stdin(0) stdout(1) stderr(2)

### Exercises 解读

- `ls -l /var/log > myoutput.txt`：将`/var/log`中的内容写入到文件`myoutput.txt`中
- `cat < peanuts.txt > banana.txt`：将`peanuts.txt`文件内容写入到`banana.txt`文件中
- `ls < peanuts.txt > banana.txt`：将文件列表写入到`banana.txt`
- `pwd < ttt.txt > copyttt.txt`：将当前所在目录写入到`copyttt.tx`
- `echo $HOME`：home 路径
- `echo $USER`：用户名
- `env`：环境变量信息
- `$PATH`：环境变量

### vim 使用

#### 搜索内容

- 从前向后搜索： `/[content]`
- 从后向前搜索：`?[content]`
- `n`：向前搜索；`N`：向后搜索

#### 正则匹配

- `^[content]`：匹配以 content 开头的内容
- `$[content]`：匹配以 content 结尾的内容
- `[single character].`：匹配单个字符
- 【例】`d[iou]g`：匹配特定符合(i,o,u)的字符
- 【例】`d[^i]g`：匹配除了 i 的任何字符
- 【例】`d[a-c]g`：匹配小写字符
- 【例】`d[A-C]g`：匹配大写字符
- h：左；k：上；j：下；l：右
- `x`：剪切选中的文本
- `dd`：删除当前行
- `y`：复制选中内容
- `yy`：复制当前行
- `p`：粘贴
- `:w`：编辑保存文件
- `:q`：退出
- `:q!`：退出不保存
- `:wq`：编辑保存
-
