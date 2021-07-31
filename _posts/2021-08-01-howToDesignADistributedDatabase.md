---
title:  从0到1，如何设计一个分布式数据库
layout: post
categories: 数据库内核
tags: 数据库内核 youtube
excerpt: PingCap创始人samplNewSQL大神黄东旭的分享
---

# 1. 为什么我们需要一个新的分布式数据库
- 数据增长快，分布式系统是主流的应对方式  
- 传统关系型数据库没有很好的scalability  
    - 法一： 数据库自身sharding  
    参考[开源数据库Sharding技术](https://developer.aliyun.com/article/530190)
    - 法二： 业务端来分表  
- OLTP and OLAP are separate to each other  
例如通过`ETL`来导出报表
- SQL never dies VS Nosql System  

# 2. NewSQL主流设计模式以及架构
## 2.1. Google Spanner/F1
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/20210731111753.png)

Google Spanner存储系统的关键特性：
- 支持sql  
- 支持业务透明的分布式事务  
例如：跨行强制事务，写入多行，要么全部成功，要么全部失败。
例如社交应用的加好友，需要同时在两个用户的好友列表里加
应用开发者需要不停的check来保证成功。
- 架构是从bigtable演进过来的  
- 计算层和存储层是分离的  
- 存储是share-nothing的架构  

F1: 一个无状态的sql层，对接Google Spanner存储系统

## 2.2. Amazon Aurora
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/20210731112551.png)

关键特性：
- 解决公有云上遇到的问题  
- 共享存储的设计，在存储引擎上实现scale  
- 优点： sql_parse和底下的存储引擎分离，业务兼容性好， 在业务量不大的业务代价较小，适合公有云业务。适合多租户业务。  
- 缺点： 写入是单点写入，然后在存储层做复制，尽量保持副本之间的一致性。 由于存算分离， 计算层是瓶颈，没法做高效的locality。  

> 观众的小问题1： 说说[codis](https://github.com/CodisLabs/codis)这个大规模分布式缓存项目

redis-sharding-middleware ： 在使用redis做缓存时的集群方案，对外呈现单节点。

------

> 观众的小问题2： 说说`spark sql`

- 生态系统很成功  
adaptive做的好，用户多， 可覆盖场景最全
- 存储层和计算存的抽象很漂亮，计算引擎没有依赖于某个特定的存储引擎  

------


# 3. TiDb的设计和实现
- google spanner流派  
- share-nothing， 自底向上的设计  
- scalability是最初的特性  
- 支持SQL  
- 和mysql兼容， 用户群体最大  
- OLTP + OLTP = HTAP  
- 24/7的可用性， 有自愈性  
- 开源项目  

软件架构如下所示：   
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/20210731115142.png)

其特点如下：  
- 软件组件划分清晰  
- 组件自身是可以scale-up的  
- 存算分离  
计算层可以使用CPU、内存资源丰富的机器， 存储层可以使用io资源丰富的机器。

> 观众的小问题3： TiDB的架构是微服务架构吗？

狭义上的微服务有一个服务发现， RPC框架在不同的框架之间起串联作用。
从广义上来说是的， 微服务本质是CSP，从思想上来说是相同的， 都利用了分层和去状态化的思想。

------

> 观众的小问题4： 模块多是否会带来`communication overhead`？

分布式系统中`communication overhead`是不可避免的。

------

## 3.1. TiDB Overview
- TiDB-无状态的SQL层(对标F1)  
    - Distributed SQL Optimizer/Executor  
- TiKV-分布式KV存储引擎(对标Spanner  
    - MVCC  
    - Distributed transaction(2PC)  
- PD(placement driver)-元信息管理、集群管理和调度(拥有全局视角的调度模块)  
管理员的角色。

> 观众的小问题5： `PD`是单点的吗？

逻辑上说是。但是其内部是有多个节点的， 通过`Raft`来通信。`PD`本身是`HA`高可用的。
`PD`本身的`scale`是有问题的， 当前元信息存储量还不太大。
集群有`1000`个`TiDB`节点， metadata才不到`100G`。
解决办法： 可以使用一个小的`TiDB`来存储`PD`。

> 观众的小问题6： `PD`的存储是否类似于[etcd](https://github.com/etcd-io/etcd)？

是的。实际上`PD`的存储就是用的[etcd](https://github.com/etcd-io/etcd)的方法。

------

> 观众的小问题7： `PD`这个词的出处？

`PD`(placement driver)是从`spanner`中出来的。

## 3.2. Storage overview(TiKV)
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/20210731143643.png)

复用了facebook的[rocksdb](https://github.com/facebook/rocksdb)。
LSMtree的开源实现， 前身是google的[leveldb](https://github.com/google/leveldb)。
本质是单机的嵌入式KVDb。
选用[rocksdb](https://github.com/facebook/rocksdb)主要看中了两个特性：
- lock-free snapshot read.  
LSM-tree 可在API层面上实现lock-free snapshot
- Batch write  
操作多个key，要么全部成功，要么全部失败。
- 性能上比[leveldb](https://github.com/google/leveldb)有很大优势  
    - 暴露了很多调优参数  
        - 根据LSM的不同层数选不同的压缩算法  
    - memory table  
    - 多线程的协调  

> 观众的小问题8： 比较不同数据结构的优缺点

- B-tree  
存储介质是SSD的话，用B-tree的意义不大。
它的设计是N叉树，设计的假设是尽可能让磁头的移动少。
- LSM-tree  
适合flash/SSD的存储介质。
随机写入对于LSM-tree来说就只有一个append-only操作，然后在后台做`compaction`。
把随机读写变成顺序读写。

> 观众的小问题9： TiKV在存储上对坏盘是如何处理的？

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/20210731143643.png)   
google的设计是叠罗汉。  
在不同的`region`之间做复制。  

-------

## 3.3. Key designs in TiKV
- Why Raft？  
    复制的模型过去只有主从。  
    mysql没法做到自动的、强一致性的replication。  
    最近的新特性是group replication。  
    `Raft`和`multi paxos`本质上是一样的， 在性能表现上也是一样的。  
    参考论文： [Paxos Made Live - An Engineering Perspective](https://research.google.com/archive/paxos_made_live.pdf)    
- Why RocksDB？  
- How to support MVCC and Distributed transaction？  
    `Raft`只能保证日志复制，它和分布式事务是两回事。  
    分布式事务build在`Raft`之上， 它本质上是两阶段提交算法。  
    分布式事务的唯一办法是两阶段提交算法。  
    分布式系统中最难的一个点就是全局时序。google依靠了一个硬件设备(True Time)来做这件事，对所有的transaction都有个绝对时序。  
    类似的， 在`TiKV`的`PD`中提供了全局时钟发生器。  
- Why not build it on top of distrubuted filesystem(HDFS/Ceph)?  
    减少性能开销。

> 观众的小问题10： Raft的优化？

参考文档： 
- Pipeline  
- Batch  
- leader List  

-----

## 3.4. Lifetime of a SQL in TiDB
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/20210731151543.png)  

`Selected Physical Plan`从数学上是一个有向无环图。

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/20210731152342.png)

因为存储是分布式的存储， sql-engine是基于分布式存储引擎设计的， 它对数据节点的`locality`是有感知的。

## 3.5. Key designs in TiDB
- Why MySQL dialect？  
    MySQL的用户群最多，迁移成本最低  
    而且做了mysql的一系列工具帮助用户在线迁移。
- Why no reuse MySQL's source code?  
    - MySQL是单机的  
    - sql-parser太差了  
- Row-based VS Columnar  
    - 取决于适应哪些workload  
    - 存储引擎慢慢做行列混合  
        在后台根据数据的使用场景智能地把一些数据把行存迁移到列存
- How to do resource isolation for OLTP and OLAP workload  
    优先做`OLTP`， 把`OLAP`的优先级调低。放在不同的任务执行队列上。
- How to support DDL for large table?  
    参考[Online, Asynchronous Schema Change in F1](https://research.google.com/pubs/archive/41376.pdf)  

## 3.6. Distributed system is fragile
> -- Jeff Dean, LADIS 2009  
一年中的硬件问题的次数：  
- ~5 racks out of 30 go wonky (50% packet loss)  
- ~8 network maintenances (4 might cause~30-minute random connectivity)  
- ~3 router failures (have to immediately pull traffic for an hour)  

软件上可能的错误：
- GC pause  
- Process crash  
- Scheduling delays  
- Network maintenances  
- Faulty equipment  

# 4. 大规模分布式系统测试经验(以TiDB为例)
在测试中引入`unstable`因素  
- Testing in distributed system is really hard  
- 使用工具`covers all`来保证单元测试  
    统计PR是否会影响单元测试的覆盖率
- 集成测试用例复用Mysql的  
    收集了`1000w+`个测试用例，使用了`distributed system`来跑testcase提高PR的测试效率。
- 故障注入  
    **本质： 在without other knowledge情况下， 加快缺陷本身出现的速度。**
    硬件： disk error, network card, cpu, clock  
    软件： file system, network and protocol
- Simulate everything:Network  
    可以通过`iptable`的隔离
- Distributed testing  
    - Jepsen  
    - Namazu  
- Random panic  
主动去找`PANNIC`点去注入故障

> 观众的小问题11： 描述一个有趣的bug？

多节点的system， 新的节点加进来之后， 再把老的下掉， 后面老的节点再回来。  
一个重要的要求：这类的bug能通过单元测试稳定复现。  
网络状态的状态能彻底抽象， 能在testcase里做复现。  
可以看TiKV里`Raft`相关的测试用例，里面有注释。

# 5. 分布式存储系统学习路径、经验
- Google papers(GFS/BigTable/Spanner/F1)  
- Consensus algorithms (Raft/Paxos)  
    - [Paxos Made Live - An Engineering Perspective](https://research.google.com/archive/paxos_made_live.pdf)    
    - [Paxos Made Simple - Leslie Lamport](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf)  
- Distributed computing systems (Spark/Dremel/Presto/Impala)  
- NewSQL systems(TiDB/CockroachDB)  
    - 从issue练手  

> 观众的小问题12： 为什么用`rust`编程语言？

计算用`go`，存储用`rust`。
- `rust`的性能好  
- `memory check`很好，控制了`data race`、`memory leak`、悬挂指针等问题  
有很好的Runtime safety特性。
- 现代的语言特性很多  
    - pattern matching  
    - cargo包管理  

# 6. what will the future be like?
- 当IO不再是数据库瓶颈的时候， 如何重新设计数据结构？  
    - 把数据库的查询逻辑固话到SSD的control里  
    - 修改一些硬件的假设带来的性能提升是一个数量级的  
- design for cloud  
- 行列混合支持OLHP  

