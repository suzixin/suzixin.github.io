---
title:  boltdb源码分析-架构
layout: post
categories: 数据库内核
tags: 数据库内核 boltdb 架构
excerpt: 摘抄自PingCap员工的[博客](https://github.com/qw4990/blog/tree/master/database/boltDB)
---

# 1. BoltDB模型

接下来我们从下到上的介绍BoltDB的模型;

## 1.1. 分页

### 1.1.1. 分页简介

BoltDB把所有的数据都维护在一个大磁盘文件上, 并分页管理它;

其格式大概如下:

```
disk: [P1|P2|P3|P4|...|Pn]
```

这些页, 可分为三种类型:

1. META_PAGE: 存储元信息;
2. FREELIST_PAGE: 标记某个页是否处于free状态, 用来管理所有的DATA_PAGE;
3. DATA_PAGE: 存储实际的数据;

下面稍微详细点的介绍这几种页;

### 1.1.2. **META_PAGE**

P1和P2都是META_PAGE, 且相互独立;

设置两个META_PAGE的原因是用于备份, 后面会说;

下面介绍MEGA_PAGE中一些关键字段, 并可以从中看出BoltDB的一些机制;

1. root_pgid: BoltDB利用分页, 在磁盘维护一个B+树, 该字段表示B+树根节点所在的页号;
2. freelist_pgid: FREELIST_PAGE所在的页号;
3. checksum: 校验码;

### 1.1.3. **FREELIST_PAGE**

就是一个数组, 记录所有了free page的页号;

FREELIST_PAGE用来持久化这个数据;

### 1.1.4. **DATA_PAGE**

持久化B+树的节点, 用来维护索引和数据;

### 1.1.5. 区分类型后的格式

区分类型后, 分别用MP, FP, DP来表示这些页, 则磁盘的格式大致如下:

```
disk: [MP1|MP2|DP1|DP2|...|DPi-1|FP|DPi|DPi+1|...]
```

任何页都有可能作为FREELIST PAGE使用, 在META PAGE中的freelist_pgid记录了它当前的位置;

### 1.1.6. 分页的读入和缓存

由于内存有限, 一般分页后, 都需要一个PageCacher之类的组件, 来进行分页的置换;

BoltDB直接使用mmap, 直接将所有的页, 也就是整个数据大文件, 全部映射到内存内;

```
mem:  [MP1|MP2|DP1|DP2|...|DPi-1|FP|DPi|DPi+1|...]
                        ^
                        |(mmap)
                        |
disk: [MP1|MP2|DP1|DP2|...|DPi-1|FP|DPi|DPi+1|...]
```

从而省略了自己实现PageCacher的麻烦, 具体见"实现"篇;

## 1.2. B+树索引

### 1.2.1. 节点持久化

B+树算法本身就不做过多的赘述了;

BoltDB将B+树每个节点, 都持久化到一段连续的页中;

如Node2被持久化在Page4~Page6, Node7被持久化在Page9中;

对于枝干节点, 其持久化的格式大概如下:

```
branch node: [(key1,child_pgid1)|(key2,child_pgid2)|(key3,child_pgid3)...]
```

根据B+树算法, 上述pair对根据key有序, child_pgid指向其对应的子节点所在的页号;

对于叶子节点, 其格式大概如下:

```
leaf node: [(key1, val1)|(key2, val2)|(key3, val3)...]
```

同理, 直接存储数据内容.

根节点的root_pgid存储在META_PAGE中;

这样, 根据索引读入特定的页, 并解析成B+树节点, 能够很方便的对B+树进行遍历.

### 1.2.2. CopyOnWrite解决读写冲突

一般的数据库需要考虑"写写冲突", "读写冲突", 由于BoltDB只支持单写事务, 因此不存在"写写冲突";

现在考虑"读写冲突": 如果一个事务正在修改某个节点的数据, 但是还没提交, 那对于另一个读事务, 可能读到脏数据;

BoltDB使用了CopyOnWrite的方法, 对需要修改节点单保存一份;

当事务进行提交时, 将这些缓存的数据, 全部同步到磁盘;

## 1.3. 图解

下面模拟一个写事务对BoltDB的影响过程;

并在更下一节进行读写冲突和事务的分析;

### 1.3.1. 初始状态

下图中, META_PAGE中分别有字段指向B+树的root节点和freelist page;

蓝色代表数据干净, 还未被修改;

B+树节点中的数字为其占用的页号, 如根节点的4表示根节点的内容存储在4页开始的一些页中;

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt0.png)

### 1.3.2. 修改/添加

某个事务调用修改/添加操作, 修改了某个叶节点的内容;

BoltDB将改叶节点的内容copy一份出来, 缓存在内存中, 如下图红色部分;

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt1.png)

### 1.3.3. 删除

该事务调用了删除操作, 于是影响了某个叶节点内的内容;

同理, 拷贝出一份维护在内存中;

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt2.png)

### 1.3.4. Rebalance-Split

在事务提交时, BoltDB会对B+树进行rebalance;

如果某个节点内容过多, B+树会对他进行分裂, 分裂后, 会影响到父节点;

假设下面的这个节点进行了分裂, 则会形成如下图:

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt3.png)

### 1.3.5. Rebalance-Merge

B+树的另一个性质是如果某个节点内容过少, 会和兄弟节点进行合并, 这也会影响到父节点;

假设下面这个节点进行了合并, 则形成如下图:

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt4.png)

### 1.3.6. 持久化简介

到目前为止, 所有的修改都维护在内存中, 下面对其进行持久化;

BoltDB的整个持久化是从下向上的;

持久化的过程中, 会为内存中维护的节点申请页用于存储, 也会释放掉被覆盖的页;

该期间会影响freelist, 其改动也是维护在内存中;

另外, 被修改的节点, 持久化时, 所使用的页号会发生改变, 所以其父节点也会受到影响, 该影响一直持续到根;

### 1.3.7. 为B+树申请分页

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt5.png)

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt6.png)

因为中间两个节点的页号发生了改变, 所以其父亲节点的索引页需要更新, 于是他们的父亲节点也需要改动;



![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt7.png)

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt8.png)

### 1.3.8. 为freelist申请分页

回收老freelist所使用的页, 为新freelist申请分页:

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt10.png)

### 1.3.9. 更新META_PAGE

由于根节点和freelist的页号发生了改变, META PAGE也会被改变, 改变先缓存在内存中;

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt11.png)

### 1.3.10. 持久化B+树节点

接下来真正的持久化B+树节点;

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt12.png)

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt13.png)

### 1.3.11. 持久化freelist

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt14.png)

### 1.3.12. 更新META PAGE到磁盘

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt15.png)

### 1.3.13. 最后结果

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/bolt16.png)

## 1.4. 容错, 冲突分析及改进

### 1.4.1. 读写冲突分析

在事务提交前, 其改动都维护在内存中, 只对自己可见;

不会影响其他读事务;

### 1.4.2. 提交各阶段容错分析

接下来分析对事务的容错性;

1. 在1-9失败: 所有修改都在内存中, 对数据库文件毫无影响;
2. 在11-12失败: META_PAGE还没有持久化, 重启后, 之前的dirty page不会对数据库目前的状态产生影响;
3. 在12失败: 使用META_PAGE中的checksum进行校验, 如果失败, 则数据库不可用\(具体见下文Backup\);

### 1.4.3. Backup

Page1, Page2都被作为META_PAGE, 其原因是可用于人工backup;

当数据库启动时, 如果meta1校验失败, 则会使用meta2;

而当数据库每次更改时, 实际上都只会修改meta1;

那么meta2什么时候会被修改呢?

BoltDB提供了一个Backup的接口, 使用这个接口后, 会将整个数据库文件, 重新拷贝一份;

并且在新文件中, 把meta1的内容写到meta2中;

个人觉得这个措施并没有任何作用, 而且可能会造成数据库错误;

1. 比如backup后`meta2`的`freelist_pgid`为12;
2. 当一段时间过后, `Page12`内的内容可能已经被改变, 但是这段时间内, 只有`meta1`被改变, `meta2`完全不知此事;
3. 如果此时`meta1`被写坏, 使用`meta2`内的内容, 则出现了错误;

### 1.4.4. 一个改进点

在每次持久化Meta1之前, 先把Meta1的老数据写到Meta2的位置;

这样, 如果当写Meta2失败时, 则Meta1还是老版本, 可直接继续使用;
I 
如果写Meta2成功后写Meta1失败, 则fallback到Meta2, 也就是事务提交之前Meta1.

# 2. BoltDB实现

BoltDB本身代码写得还是很不错的, 就不过多赘述了, 仅仅是挑几个觉得写得比较不错的地方;

## 2.1. Struct到二进制转换

在做结构体到二进制的转换时, BoltDB直接使用go的unsafe包, 从而避免了序列化/反序列化的开销;

大概如下:

```
func main() {
	type T struct {
		A int
		B float64
	}

	buf := make([]byte, 1000)
	write := (*T)(unsafe.Pointer(&buf[0]))
	write.A = 23
	write.B = 23.33

	read := (*T)(unsafe.Pointer(&buf[0]))
	fmt.Println(*read)
}
```

## 2.2. 利用mmap直接管理分页

BoltDB利用mmap, 把分页的管理交给了操作系统;

同时, 利用unsafe, 也避免了序列化/反序列化:

```
type DB {
    data *[maxMapSize]byte
    ...
}

type page sturct {
    id pgid
    ...
}

func open(file String) *DB {
    ...
    buffer, _ := syscall.Mmap(...file...)
    db.data = (*[maxMapSize]byte)(unsafe.Pointer(&b[0]))
    ...
}

func (db *DB) page(id pgid) *page {
    pos := id * db.pageSize
    return (*page)(unsafe.Pointer(&db.data[pos]))
}
```



