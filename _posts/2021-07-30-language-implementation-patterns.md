---
title:  编程语言实现模式
layout: post
categories: 编译器
tags: 编译器 书籍
excerpt: 编程语言实现模式
---
> [编程语言实现模式](https://github.com/Lucifier129/language-implementation-patterns/blob/master/%E7%BC%96%E7%A8%8B%E8%AF%AD%E8%A8%80%E5%AE%9E%E7%8E%B0%E6%A8%A1%E5%BC%8F.pdf)  
[Language Implementation Patterns : Create Your Own Domain-Specific and General Programming Languages](https://doc.lagout.org/programmation/Pragmatic%20Programmers/Language%20Implementation%20Patterns.pdf)

相比于龙书，这本书更浅显易懂，实操性更强一些。而且这本书不止于编译器，它包括了语言类的应用。
这本书介绍了语言应用常见的`31`种模式，在构造自己的应用时，可以使用搭积木一样的方式来选择这些模式。

# 1. 初探语言应用  
## 1.1. 大局观
![1HEdj1.png](https://s2.ax1x.com/2020/02/12/1HEdj1.png)

语言应用的分类：
- 文件读取器
- 生成器
收集内部数据结构的信息然后产生输出。
- 翻译器
文件读取器和生成器的组合，汇编器和编译器都属于翻译器
- 解释器
计算器、编程语言java、python

## 1.2. 模式概览 
本书会介绍`31`种不同的模式。

- 解析输入语句
- 构建语法树
`IR`实际上就是处理过了的输入内容。
- 遍历树
    两种方法：
    - 把方法内置于每个节点的类里
    - 把方法封装在外部访问者里
- 弄清输入的含义
    符号表是符号的字典，符号有它的作用域，具体可分为：
    - 单一作用域
    - 嵌套作用域
    - C结构体作用域
    - 类作用域
- 解释输入语句
介绍了常见解释器的模式
- 翻译语言
计算输出和产生输出这两个阶段还是应该分开进行。

## 1.3. 深入浅出语言应用 
介绍几个语言应用的架构。
### 1.3.1. 字节码解释器
![1HnAJO.png](https://s2.ax1x.com/2020/02/12/1HnAJO.png)

解释器用软件模拟出硬件处理器，因此也被称为虚拟机。
解释器需要完成的工作：
- 取指令-解码-执行
- 产生输出的指令

### 1.3.2. Java查错程序
这里举例说明设计一个查找自赋值错误的查错程序的步骤。
输入：源代码文件，比如以下的一个错误函数
```java
void setX(int y) {this.x = x;}
```
输出：bug list

![1HM61S.png](https://s2.ax1x.com/2020/02/12/1HM61S.png)
![1HlcZj.png](https://s2.ax1x.com/2020/02/12/1HlcZj.png)
采用多次扫描还能支持前向引用。

### 1.3.3. Java查错程序2
输入：`.class`文件
输出：bug list

![1H8bwQ.png](https://s2.ax1x.com/2020/02/12/1H8bwQ.png)

### 1.3.4. C编译器
编译器最复杂的地方是语义分析和优化。

![1HYQJA.png](https://s2.ax1x.com/2020/02/12/1HYQJA.png)
![1HdPvn.png](https://s2.ax1x.com/2020/02/12/1HdPvn.png)

### 1.3.5. 借助C编译器实现C++语言
这也是C++之父创造C++的过程：
![1H01AK.png](https://s2.ax1x.com/2020/02/12/1H01AK.png)

## 1.4. 为语言应用选择合适的模式 
程序员常常做的两种事情:
- 实现某种`DSL`(`Domain Specific Languages`)
- 处理或翻译`GPPL`(`General-Purpose Programming Language`)

解析器是语法分析的必要工具，符号表对于分析输入内容的语义也有至关重要的地位。
syntax tells us what to do, and semantics tells us what to do it to.

# 2. 第2章 基本解析模式
**文法**可以看做是语法解析器的功能说明书或设计文档。
文法可以看成是某种`DSL`编写的能执行的程序。`ANTLR`等解析器的生成工具能够根据文法自动生成解析器，自动生成的解析器代码少，稳定，不容易出错。

## 2.1. 识别式子的结构
**解析(Parse)**：将线性的词法单元序列组成带有结构的解析树。

## 2.2. 构建递归下降语法解析器
**语法解析器**可以检查句子的结构是否符合语法规范。
解析器的任务是遇到某种结构，就执行某些操作。
`LL(1)`：向前看一个词法单元的自顶向下解析器。
手写解析器的一个例子：
```cpp
/** To parse a statement, call stat(); */
void stat() { returnstat(); }
void returnstat() { match("return" ); expr(); match(";" ); }
void expr() { match("x" ); match("+" ); match("1" ); }
```
手写解析器挺无聊的，所以考虑用`DSL`来构建语法解析器。

## 2.3. 使用文法DSL来构建语法解析器
**文法**：用专用的`DSL`来描述语言。
**解析器生成器**：能将文法翻译为解析器的工具。
**`ANTLR`**：（全名：ANother Tool for Language Recognition）是基于`LL(*)`算法实现的语法解析器生成器（`parser generator`），用Java语言编写，使用自上而下（`top-down`）的递归下降`LL`剖析器方法。由旧金山大学的`Terence Parr`博士等人于1989年开始发展。
举例如下：
```
stat : returnstat // "return x+0;" or
     | assign // "x=0;" or
     | ifstat // "if x<0 then x=0;"
;
returnstat : 'return' expr ';' ; // single-quoted strings are tokens
assign : 'x' '=' expr ;
ifstat : 'if' expr 'then' stat ;
expr : 'x' '+' '0' // used by returnstat
     | 'x' '<' '0' // used by if conditional
     | '0' // used in assign
     ;
```

可以使用`ANTLRWorks`的图形输入界面来输入产生式：
![1qE6CF.png](https://s2.ax1x.com/2020/02/13/1qE6CF.png)

## 2.4. 词法单元和句子
**词法解析器**：能处理输入字符流的解析器
**例子**：
识别形如`[a,b,c]` 、`[a,[b,c],d]`的列表。
语法：
```
grammar NestedNameList;
list : '[' elements ']' ; // match bracketed list
elements : element (',' element)* ; // match comma-separated list
element : NAME | list ; // element is name or nested list
NAME : ('a'..'z' |'A'..'Z' )+ ; // NAME is sequence of >=1 letter
```

对应生成的解析树：
![1qVaGD.png](https://s2.ax1x.com/2020/02/13/1qVaGD.png)

### 2.4.1. 模式1：从文法到递归下降识别器
#### 2.4.1.1. 目的
此模式介绍了直接根据**文法**生成**识别器**的方法。
局限性：
- 对左递归文法无能为力

#### 2.4.1.2. 实现
```java
public class G extends Parser { // parser definition written in Java
    «token-type-definitions»
    «suitable-constructor»
    «rule-methods»
}
```

#### 2.4.1.3. 规则的转换
```java
public void r() {
    ...
}
```

#### 2.4.1.4. 词法单元的转换
- 定义词法单元类型`T`
- 如果规则出现了类型`T`，则调用`match(T)`来`eat`掉这个`Token`

#### 2.4.1.5. 子规则的转换
**例子**：
- 子规则
`(«alt1 »|«alt2 »|..|«altN »)`
- 控制流
![1que9f.png](https://s2.ax1x.com/2020/02/13/1que9f.png)
- 一般实现方式
```cpp
if ( «lookahead-predicts-alt1 » ) { «match-alt1 » }
else if ( «lookahead-predicts-alt2 » ) { «match-alt2 » }
...
else if ( «lookahead-predicts-altN » ) { «match-altN » }
else «throw-exception» // parse error (no viable alternative)
```

- `switch`实现方式
```cpp
switch ( «lookahead-token» ) {
case «token1-predicting-alt1 » :
case «token2-predicting-alt1 » :
...
«match-alt1 »
break;
case «token1-predicting-alt2 » :
case «token2-predicting-alt2 » :
...
«match-alt2 »
break;
...
case «token1-predicting-altN » :
case «token2-predicting-altN » :
...
«match-altN »
break;
default : «throw-exception»
}
```

#### 2.4.1.6. 转换子规则操作符
- `optional`
`if ( «lookahead-is-T » ) { match(T); } // no error else clause`

- `one_or_more`
```cpp
do {
    «code-matching-alternatives»
} while ( «lookahead-predicts-an-alt-of-subrule» );
```

- `zero_or_more`
```cpp
while ( «lookahead-predicts-an-alt-of-subrule» ) {
    «code-matching-alternatives»
}
```

### 2.4.2. 模式2：`LL(1)`递归下降的词法解析器
#### 2.4.2.1. 目的
该词法解析器能识别字符流中的模式，生成词法单元流。


第3章 高阶解析模式 49
3.1 利用任意多的向前看符号进行解析 50
3.2 记忆式解析 52
3.3 采用语义信息指导解析过程 52
第2部分 分析输入
第4章 从语法树构建中间表示 73
4.1 为什么要构建树 75
4.2 构建抽象语法树 77
4.3 简要介绍ANTLR 84
4.4 使用ANTLR文法构建AST 86
第5章 遍历并改写树形结构 101
5.1 遍历树以及访问顺序 102
5.2 封装访问节点的代码 105
5.3 根据文法自动生成访问者 107
5.4 将遍历与匹配解耦 110
第6章 记录并识别程序中的符号 131
6.1 收集程序实体的信息 132
6.2 根据作用域划分符号 134
6.3 解析符号 139
第7章 管理数据聚集的符号表 155
7.1 为结构体构建作用域树 156
7.2 为类构建作用域树 158
第8章 静态类型检查 181
第3部分 解释执行
第9章 构建高级解释器 219
9.1 高级解释器存储系统的设计 220
9.2 高级解释器中的符号记录 222
9.3 处理指令 224
第10章 构建字节码解释器 239
10.1 设计字节码解释器 241
10.2 定义汇编语言语法 243
10.3 字节码机器的架构 245
10.4 如何深入 250
第4部分 生成输出
第11章 语言的翻译 278
11.1 语法制导的翻译 280
11.2 基于规则的翻译 281
11.3 模型驱动的翻译 283
11.4 创建嵌套的输出模型 291
第12章 使用模板生成DSL 312
12.1 熟悉StringTemplate 313
12.2 StringTemplate的性质 316
12.2 从一个简单的输入模型生成模板 317
12.4 在输入模型不同的情况下复用模板 320
12.5 使用树文法来创建模板 323
12.6 对数据列表使用模板 330
12.7 编写可改变输出结果的翻译器 336
第13章 知识汇总 348
13.1 在蛋白质结构中查找模式 348
13.2 使用脚本构建三维场景 349
13.3 处理XML 350
13.4 读取通用的配置文件 352
13.5 对代码进行微调 353
13.6 为Java添加新的类型 354
13.7 美化源代码 355
13.8 编译为机器码 356

