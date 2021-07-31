---
title:  PostgreSQL 数据库内核分析-c6
layout: post
categories: PostgreSQL
tags: PostgreSQL 数据库执行 书籍
excerpt: PostgreSQL 数据库内核分析-c6
---
# 6. 第6章 查询执行
在查询执行阶段， 将根据执行计划进行数据提取、处理、存储等一系列活动，以完成整个查询执行过程。根据执行计划的安排，调用存储、索引、并发等模块，按照各种执行计划中各种计划节点的实现算法来完成数据的读取或者修改的过程。

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_115025.jpg)

`Portal` ： 选择策略，是查询语句还是非查询语句
`Executor` ： 输入包含了一个查询计划树`Plan Tree`
`ProcessUtility` ： 为每个非查询指令实现了处理流程


## 6.1. 查询执行策略
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_123253.jpg)

### 6.1.1. 可优化语句和数据定义语句
### 6.1.2. 四种执行策略
### 6.1.3. 策略选择的实现
### 6.1.4. Portal执行的过程

Portal执行时的函数调用关系:
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_141106.jpg)

## 6.2. 数据定义语句执行
### 6.2.1. 数据定义语句执行流程
根据`NodeTag`字段的值来区分各种不同节点， 并引导执行流程进入相应的处理函数。
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_141141.jpg)

### 6.2.2. 执行实例
```sql
CREATE TABLE course(
    no SERIAL,
    name VARCHAR,
    credit INT,
    CONSTRAINT conl CHECK(credit >=0 AND name <>''),
    PRIMARY KEY(no)
)
```

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_142205.jpg)
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_142329.jpg)
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_143411.jpg)

将一个`T_CreateStmt`操作转换为一个操作序列`T_CreateSeqStmt`+`T_CreateStmt`+`T_IndexStmt`，之后`ProcessUtility`将逐个对序列中的操作进行处理。

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_143550.jpg)

### 6.2.3. 主要的功能处理器函数
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_143948.jpg)

## 6.3. 可优化语句执行
### 6.3.1. 物理代数与处理模型
### 6.3.2. 物理操作符的数据结构
### 6.3.3. 执行器的运行
### 6.3.4. 执行实例
```sql
/* 例6.2 */
course(no, name, credit)
teacher(no, name, sex, age)
teach_coures(no, cno, stu_num)

SELECT t.name, c.name, stu_num
FROM course AS c, teach_course AS tc, teacher AS t
WHERE c.no=tc.cno AND tc.tno=t.no AND c.name='Database System' AND t.name='Jennifer';
```

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_145754.jpg)
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_150129.jpg)

## 6.4. 计划节点
### 6.4.1. 控制节点
### 6.4.2. 扫描节点
### 6.4.3. 物化节点
### 6.4.4. 连接节点
## 6.5. 其他子功能介绍
### 6.5.1. 元组操作
### 6.5.2. 表达式计算
### 6.5.3. 投影操作
## 6.6. 小结
