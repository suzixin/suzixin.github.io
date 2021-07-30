---
title:  dragonbook
layout: post
categories: 编译器
tags: 编译器 书籍
excerpt: dragonbook-c1
---
 # 书本资源
- 对应大学课程：[编译原理哈工大课程](https://www.icourse163.org/course/HIT-1002123007)
- [电子书](https://github.com/iBreaker/book.git)
- [源码](https://suif.stanford.edu/dragonbook/dragon-front-source.tar)
- [课后答案](https://github.com/fool2fish/dragon-book-exercise-answers)

# Introduction
一个语言处理系统的基本结构：
![lBQYM4.png](https://s2.ax1x.com/2020/01/05/lBQYM4.png)

## 1.1 Language Processors
> A compiler that translates a high-level language into another high-level
language is called a *source-to-source* translator. 

这种源到源翻译器可以用来做建模分析和性能优化。

## 1.2 The Structure of a Compiler
编译器的各个步骤：
![lBv0fK.png](https://s2.ax1x.com/2020/01/05/lBv0fK.png)

一个翻译的例子：
![lBxnje.png](https://s2.ax1x.com/2020/01/05/lBxnje.png)

### 1.2.1 Lexical Analysis
词法分析的输出：`(token-name, attribute-value)`  
其中，`token-name`是语法分析步骤使用的抽象符号，`attribute-value`指向符号表中关于这个词法单元的条目。

### 1.2.2 Syntax Analysis
**从输入输出的角度来说**，语法分析使用由词法分析器生成的各个词法单元的第一个分量来创建树形的中间表示。
**从文法的角度来描述**，接收一个终结符号串作为输入，找出从文法的开始符号推到出这个串的方法，如果找不到这样的方法， 则报告语法错误。

### 1.2.3 Semantic Analysis
语义分析使用语法树和符号表中的信息来检查源程序是否和语言定义的语义一致。
在这个阶段会执行一些检查，例如类型检查，如果不比配可能会做自动类型转换。

### 1.2.4 Intermediate Code Generation
在源程序的语法分析和语义分析完成后，编译器生成一个明确的低级的或者是类机器语言的中间表示。

### 1.2.5 Code Optimization
机器无关的代码优化步骤：改进中间代码，以生成更好的目标代码。

### 1.2.6 Code Generation
对源程序中的标识符进行存储分配、寄存器进行合理分配，生成可重定位的机器代码。

### 1.2.7 Symbol-Table Management
记录源程序中所使用的变量、函数的名字。

### 1.2.8 The Grouping of Phases into Passes
多个步骤的活动可以组合成一趟。

### 1.2.9 Compiler-Construction Tools
常见的编译工具如下所示：
1. **Parser generators** that automatically produce syntax analyzers from a
grammatical description of a programming language.
2. **Scanner generators** that produce lexical analyzers from a regular-expression
description of the tokens of a language.
3. **Syntax-directed translation engines** that produce collections of routines
for walking a parse tree and generating intermediate code.
4. **Code-generator generators** that produce a code generator from a collection
of rules for translating each operation of the intermediate language into
the machine language for a target machine.
5. **Data-flow analysis engines** that facilitate the gathering of information
about how values are transmitted from one part of a program to each
other part. Data-flow analysis is a key part of code optimization.
6. **Compiler-construction toolkits** that provide an integrated set of routines
for constructing various phases of a compiler.

## 1.5 Applications of Compiler Technology
除了构造编译器以外还有其他很多应用

### 1.5.1 Implement at ion of High-Level Programming Languages
在动态编译中(如`Java`的`JIT`)尽可能降低编译时间是很重要的， 因为编译时间也是运行开销的一部分。一个常用的技术是只编译和优化那些经常运行的程序片段。

### 1.5.2 Optimizations for Computer Architectures
- 并行性
    - 编译器对指令重新排布，提高指令的并行性
    - 指令级并行：微处理器流水线自身的指令级并行
- 内存层次结构
    - 通过改变数据的布局或数据访问代码的顺序来提高内存层次结构的效率
    - 通过改变代码的布局来提高指令高速缓存的效率。

### 1.5.3 Design of New Computer Architectures
- RISC
- CISC
使用高性能x86机器的最有效方式是仅使用它的简单指令。

### 1.5.4 Program Translations
编译：从一个高级语言到机器语言的翻译过程。
实际上可以延伸为：不同种类语言之间的翻译。
例如二进制翻译——直接将x86的二进制代码翻译成其他架构下的二进制代码。

### 1.5.5 Software Productivity Tools
使用编译技术开发的静态检查工具。

## 1.6 Programming Language Basics
### 1.6.1 The Static/Dynamic Distinction
静态：不需要运行程序就可以决定的问题
动态：只允许在运行程序的时候做出决定的问题

### 1.6.2 Environments and States
从一个变量名得到它对应的值实际上有两个步骤：`environment`和`state`。
![lDpDUA.png](https://s2.ax1x.com/2020/01/05/lDpDUA.png)
首先根据当前的`environment`判断这个变量名所对应的内存地址，然后再从这个内存地址(也有可能是寄存器)得到这个变量的值。

### 1.6.3 Static Scope and Block Structure
一个例子如下所示：
![lD90MT.png](https://s2.ax1x.com/2020/01/05/lD90MT.png)

![lD96o9.png](https://s2.ax1x.com/2020/01/05/lD96o9.png)

### 1.6.4 Explicit Access Control
`c++`中可以通过`public`、`private`和`protected`这样的关键字来提供对类中的成员的显示访问控制。
声明告诉我们事务的类型，定义告诉我们它们的值。

### 1.6.5 Dynamic Scope
定义：一个作用域策略依赖于一个或多个只有在程序执行时刻才能知道的因素
例子：
```c
#define a (x+1)
int x = 2;
void b() { int x = I ; printf (ll%d\nlla), ; }
void c() { printf("%d\nI1, a);}
void main() { b(); c(); }
```
静态作用域和动态作用域的类比：动态规则处理时间的方式类似于静态作用域处理空间的方式。
![lDCmmF.png](https://s2.ax1x.com/2020/01/05/lDCmmF.png)


### 1.6.6 Parameter Passing Mechanisms
- 值调用
- 引用调用
- 名调用(仅在早起使用)

### 1.6.7 Aliasing
一个例子：
```c
#include <stdio.h>
void q(int x[], int y[]) {
    x[10] = 2;
    printf("y[10] = %d\n", y[10]);
}

int main() {
    int a[20];
    q(a, a);
    printf("a[10] = %d\n", a[10]);
    return 0;
}
```

很多时候我们必须确认某些变量之间不是别名之后才可以优化程序。

# 2 A Simple Syntax-Directed Translator
目标：把源码转换成中间代码(三地址码)

## 2.1 Introduction
**语法**：描述了程序语言的程序的正确形式
**语义**：定义了程序的含义——即每个程序在运行时做什么事情。

编译器前端模型如下所示：
![lss5RK.png](https://s2.ax1x.com/2020/01/06/lss5RK.png)

两种中间代码形式如下所示：
![lgY7Os.png](https://s2.ax1x.com/2020/01/08/lgY7Os.png)

## 2.2 Syntax Definition
解决如何描述一套语法的问题。

### 2.2.1 Definition of Grammars
**文法**：用于描述程序设计语言语法的表示方法，被用于组织编译器前端。
**上下文无关文法**是文法的一种

其定义如下所示：
[![lsyEiq.md.png](https://s2.ax1x.com/2020/01/06/lsyEiq.md.png)](https://imgchr.com/i/lsyEiq)

词法分析的输出：`(token-name, attribute-value)`  
其中，`token-name`是语法分析步骤使用的抽象符号，`attribute-value`指向符号表中关于这个词法单元的条目。  
我们常常把`token-name`称为终结符号，因为他们在描述程序设计语言的文法中是以终结符号的形式出现的。

### 2.2.2 Derivations
**推导**：从开始符号出发，不断将某个非终结符替换为该非终结符号的某个产生式的体。
**语言**：从开始符号推导得出的所有终结符号串的集合。

### 2.2.3 Parse Trees
语法分析树使用图形的方式展现了从文法的开始符号推导出相应语言中的符号串的过程，所以一个语法分析树的叶子节点从左到右构成了树的结果。  

每个内部结点和它的子节点对应于一个产生式，内部节点对应于产生式的头，它的子节点对应于产生式的体。
**语法分析**：为一个给定的终结符号串构建一颗语法分析树的过程称为对该符号传进行语法分析。

### 2.2.4 Ambiguity
一个文法可能有多颗语法分析树能够生成同一个给定的终结符号串。
> 我的小问题：如何通过数学上的证明方法判断文法具有二义性？(除了举反例以外)

对于任意一个上下文无关文法，不存在一个算法，判定它是无二义性的；但能给出一组充分条件
满足这组充分条件的文法是无二义性的
- 满足，肯定无二义性
- 不满足，也未必就是有二义性的

-----------------

### 2.2.5 Associativity of Operators
运算符的结合性：左结合/右结合。
> 我的小问题：如何通过文法来设计这种左/右结合性？

通过把迭代的非终结符符号放在表达式的右侧。例如`a=b=c`可以由以下文法产生。  
![lscBGt.png](https://s2.ax1x.com/2020/01/06/lscBGt.png)

---------------

### 2.2.6 Precedence of Operators
例`2.6`展示了包含`+-*/`优先性考虑的文法，如下所示：
![lsR1Gn.png](https://s2.ax1x.com/2020/01/06/lsR1Gn.png)

在这里我们可以看到一个规律：非终结符号的数目正好比表达式中优先级的层数多`1`。

概念延伸：
- `factor`：不能被任何运算符分开的表达式
- `term`：可能被高优先级的运算符分开，但不能被低优先级运算符分开的表达式。

简单来说，在使用这种表达方式的时候，一个表达式就是一个由`+`或`-`分隔开的`term`的列表，而`term`是由`*`或`/`分隔的因子`factor`的列表。

例`2.7`展示了`java`语法的例子。

## 2.3 Syntax-Directed Translation
**语法制导**技术是一种面向文法的编译技术。
**语法制导翻译**是通过向一个文法的产生式附加一些规则或程序片段而得到的，相关概念
- **属性(Attributes)**：表示与某个程序构造相关的任意的量。  
- **(语法指导的)翻译方案(Syntax-directed)**：将程序片段附加到一个文法的各个产生式上的表示法。

例如，对于`expr -> expr1 + term`，可以使用如下伪代码来翻译：
```
translate expr1;
translate term;
handle +;
```

### 2.3.1 Postfix Notation
例`2.8`以从常规表达式翻译成后缀表达式为例，解释了语法指导翻译的基本过程
例`2.9`解释了后缀表达式的计算过程。

### 2.3.2 Synthesized Attributes
**语法制导(`Syntax-Directed`)**：把每个文法符号和一个属性集合相关联，并且把每个产生式和一组语义规则相关联，这些规则用于计算与该产生式中符号相关联的属性值。

**注释语法分析树**：一颗语法分析树的各个结点上标记了相应的属性值。  
例`2.10`介绍了如何根据图`2.10`中的语法制定定义得到一颗注释分析树。  
图`2.10`就是对产生式附加的规则。  
![lswZRg.png](https://s2.ax1x.com/2020/01/06/lswZRg.png)  
![lsN3gs.png](https://s2.ax1x.com/2020/01/06/lsN3gs.png)

### 2.3.3 Simple Syntax-Directed Definitions
**简单语法制导**：对于这种情形，要得到代表产生式头部的非终结符符号的翻译结果的字符串，只需要将产生式体中各非终结符号的翻译结果按照它们在非终结符号中的出现顺序连接起来，并在其中穿插一些附加的串即可。

### 2.3.5 Translation Schemes
**语法制导翻译方案**是一种在文法产生式中附加一些程序片段来描述翻译结果的表示方法。  

可以看到例`2.12`和例`2.10`是两种不同的翻译方案。  
例`2.12`在例`2.10`的基础上添加了实时打印结点的语义动作。如下所示：  
![lsDfm9.png](https://s2.ax1x.com/2020/01/06/lsDfm9.png)  
![lsB7rj.png](https://s2.ax1x.com/2020/01/06/lsB7rj.png)  

注意例`2.10`和例`2.12`构造结果的过程上的区别。
例`2.10`是把字符串作为属性附加到语法分析树中的结点上，而例`2.12`通过语义动作把翻译结果以增量方式打印出来。

## 2.4 Parsing
**词法分析**是决定如何使用一个文法生成一个终结符号串的过程，在讨论这个问题时。**可以想象正在构造一个语法分析树**，这样有助于理解分析的问题。

### 2.4.1 Top-Down Parsing
**自顶向下分析方法**：构造从根节点开始，逐步向叶子结点方向进行。一般来说，为一个非终结符号选择产生式是一个尝试并犯错的过程。
如以下的例子所示。  
文法：  
![l6gEWR.png](https://s2.ax1x.com/2020/01/07/l6gEWR.png)  
语法分析树：  
![lymAfK.png](https://s2.ax1x.com/2020/01/06/lymAfK.png)

输入中当前被扫描的终结符号通常称为向前看(`lookahead`)符号，如图中箭头所示。  

### 2.4.2 Predictive Parsing
**递归下降分析方法**(recursive-descent)是一种自顶向下的语法分析方法，它使用一组递归过程来处理输入。
递归下降分析法的一种简单形式是**预测分析法**。

将`FIRST(a)`定义为可以由`a`生成的一个或多个终结符号串的第一个符号的集合。
对于`2.16`的文法，其`FIRST`的计算如下：

```
FIRST(stmt) = {expr, if, for, other)
FIRST(expr; ) = {expr}
```

预测分析法的伪代码如下所示：
```
void stmt() {
    switch ( lookahead ) {
    case expr:
        match(expr); match(' ; '); break;
    case if:
        match(if); match(' (I); match (expr); match(') '); stmt ();
        break;
    case for:
        match (for); match (' (') ;
        optexpr (); match(' ; I); optexpr(); match(' ; '); optexpr();
        match(') '); stmt (); break;
    case other;
        match (ot her) ; break;
    default:
        report ("synt ax error");
    }
}

void optexpro {
    if ( lookahead == expr ) match(expr);
}

void match(termina1 t) {
    if ( Eookahead == t ) Eookahead = nextTermina1;
    else report ("syntax error If);
}
```

### 2.4.3 When to Use 6-Productions
我们的预测分析器在没有其他产生式可用时，将`ε`产生式作为默认选择使用。

### 2.4.4 Designing a Predictive Parser
一个预测分析器构造过程可以理解为是`2.4.2`的伪代码的一个抽象。
一个预测分析器程序由各个非终结符对应的过程组成。
- 检查`lookahead`符号，决定使用A的哪个产生式
- 然后，这个过程模拟被选中的产生式的体。

我们可以基于以上基本过程扩展得到一个语法制导的翻译器。

### 2.4.5 Left Recursion
`A->Aa`的右部的最左符号是`A`自身，非终结符号`A`和它的产生式就称为**左递归**的。
`A->Aa | β`也是左递归的。

> 如何消除左递归？

可改写成如下形式
```
A -> βR
R -> aR | ε
```
--------------------

同理，形如`R->aR`的产生式被称为右递归的。
左递归的产生式在使用递归下降分析方法时可能会出现无限循环，右递归的产生式对包含了左结合运算符的表达式的翻译较为困难。

> 左递归这个概念和前面提到的运算符的左结合有何关联？

--------


### 2.4.6 Exercises for Section 2.4
这几个练习蛮好，值得练下。

## 2.5 A Translator for Simple Expressions
基本的过程：
- 首先使用易于翻译的文法
- 再小心地对这个文法进行转换，使之能够支持语法分析。

### 2.5.1 Abstract and Concrete Syntax
在抽象(Abstract)语法树中，内部节点代表的是程序构造；而在语法(Concrete)分析树中，内部节点代表的是非终结符号。

### 2.5.2 Adapting the Translation Scheme
例`2.13`：
![l6zdBT.png](https://s2.ax1x.com/2020/01/07/l6zdBT.png)
以上产生式是左递归的， 其抽象形式如下

```
A = expr
α = + term { print ('+') }
β = - term { print('-') }
γ = term

A -> Aα | Aβ | γ
```

消除左递归，更改为
```
A -> γR
R -> αR | βR | ε
```

展开如下所示：  
![lc9MB6.png](https://s2.ax1x.com/2020/01/07/lc9MB6.png)

### 2.5.3 Procedures for the Nonterminals
```c
void expro {
    term () ; rest () ;
}

void rest() {
    if ( lookahead == '+' ) {
        match('+') ; term () ; print ('+'); rest () ;
    } else if ( lookahead == '-' ) {
        match('-'); term(); print ('-'); rest ();
    } else { } /* do nothing with the input */ ;
}

void term() {
    if ( lookahead is a digit ) {
        t = lookahead, match(1ookahead); print (t);
    else report (" syntax error") ;
    }
}
```

### 2.5.4 Simplifying the Translator
- 将尾递归改成循环
- 将多余的函数接口合一

### 2.5.5 The Complete Program
```java
import java.io.*;
class Parser {
    static int lookahead;
    public Parser() throws IOException {
        lookahead = System.in.read();
    }

    void expro throws IOException {
        term() ;
        while (true) {
            if ( lookahead == '+' ) {
                match('+') ; term() ; System.out.write('+');
            }
            else if ( lookahead == '-' ) {
                match('-'); term(); System.out
            }
            else return; 
        }
    }

    void term() throws IOException {
        if ( Character. isDigit ((char) lookahead)) {
            System. out. write( (char) lookahead) ; match(1ookahead) ;
        }
        else throw new Error("syntax error");
    }

    void match(int t) throws IOException {
        if ( lookahead == t ) lookahead = System. in.read() ;
        else throw new Error("syntax error") ;
    }
}

public class Postfix {
    public static void main(StringC1 args) throws IOException {
        Parser parse = new Parser();
        parse.expr() ; System.out. write('\n') ;
    }
}
```

## 2.6 Lexical Analysis
一个词法分析器从输入中读取字符，并将他们组成**词法单元对象**。

> 词法单元和终结符号的关系是什么？

除了用于语法分析的终结符号之外，一个词法单元对象还包含一些附加信息，这些信息以属性值的形式出现。

---------------------
### 2.6.5 A Lexical Analyzer
用一个哈希表`word`来保存关键字和标识符，程序中类的继承关系如下图所示：  

![lgnh7Q.png](https://s2.ax1x.com/2020/01/08/lgnh7Q.png)

伪代码如下所示：
```java
Token scan() {
    skip white space, as in Section 2.6.1;
    handle numbers, as in Section 2.6.3;
    handle reserved words and identifiers, as in Section 2.6.4;
    /* if we get here, treat read-ahead character peek as a token */
    Token t = new Token(peelc);
    peek = blank /* initialization, as discussed in Section 2.6.2 */ ;
    return t;
}
```
完整代码见`front/lexer`。

## 2.7 Symbol Tables
**符号表**是一种供编译器用于保存有关源程序构造的各种信息的数据结构。
**作用域**：起该声明作用的那一部分程序，为了实现作用域，我们将为每个作用域建立一个单独的符号表，这个作用域中的每个声明都在此符号表中有一个对应的条目。

> 谁来创建符号表？

符号表条目是在分析阶段由词法分析器、语法分析器和语义分析器创建并使用的。  
在书中的这个例子中，作者使用语法分析器来创建这些条目。

小目标：
输入：
```c
{
    int x;
    char y;
    {
        bool y;
        x;
        y;
    }
    x;
    y;
}
```

输出：
```c
{
    {
        x:int;
        y:bool;
    }
    x:int;
    y:char;
}
```

### 2.7.1 Symbol Table Per Scope 
文法声明如下所示：  
![lgMpy6.png](https://s2.ax1x.com/2020/01/08/lgMpy6.png)

例`2.15`用下标来区分对同一标识符的不同声明：  
![lg3Qvn.png](https://s2.ax1x.com/2020/01/08/lg3Qvn.png)

例`2.16`显示了例`2.15`中伪代码的符号表：  
![lg3t5F.png](https://s2.ax1x.com/2020/01/08/lg3t5F.png)

对应链接符号表的代码实现见`front/symbols/Env.java`。

```java
package symbols;
import java.util.*; import lexer.*; import inter.*;

public class Env {

	private Hashtable table;
	protected Env prev;

	public Env(Env n) { table = new Hashtable(); prev = n; }

	public void put(Token w, Id i) { table.put(w, i); }

	public Id get(Token w) {
		for( Env e = this; e != null; e = e.prev ) {
			Id found = (Id)(e.table.get(w));
			if( found != null ) return found;
		}
		return null;
	}
}

```
### 2.7.2 The Use of Symbol Tables
![lg8pZV.png](https://s2.ax1x.com/2020/01/08/lg8pZV.png)

## 2.8 Intermediate Code Generation

### 2.8.1 Two Kinds of Intermediate Representations
- 树形结构
- 线性表示形式

### 2.8.2 Construction of Syntax Trees
![lgaQB9.png](https://s2.ax1x.com/2020/01/08/lgaQB9.png)
主要可以分为：
- 语句的抽象语法树
- 在抽象语法树中表示语句块
- 表达式的语法树

### 2.8.3 Static Checking
**静态检查**是指在编译过程中完成的各种一致性的检查。包括
- 语法检查
它们并没有包括在用于语法分析的文法中，语法检查的一个例子是左值和右值检查
- 类型检查
类型检查规则按照抽象语法中运算符/运算分量的结构进行描述，主要运用了**实际类型和期望类型相匹配**的思想。

### 2.8.4 Three-Address Code
通过遍历语法树来生成三地址代码。  
- 语句的翻译  
举了翻译`if`语句的例子：  
从代码结构来说,每一个类内部包含一个构造函数和生成三地址代码的函数`gen`。
![lgXqk4.png](https://s2.ax1x.com/2020/01/08/lgXqk4.png)
![lgXOh9.png](https://s2.ax1x.com/2020/01/08/lgXOh9.png)
- 表达式的翻译  
![lgjB4J.png](https://s2.ax1x.com/2020/01/08/lgjB4J.png)
![lgjyg1.png](https://s2.ax1x.com/2020/01/08/lgjyg1.png)
    - 例`2.19`：翻译`a[2*k]`
    - 例`2.20`：翻译`a[i] = 2*a[j-k]`

优化策略：首先使用一个简单的中间代码生成方法，然后依靠代码优化器来消除不必要的指令。

## 2.9 Summary of Chapter 2
另一个关于本章工作的例子：
![l285gH.png](https://s2.ax1x.com/2020/01/08/l285gH.png)

# 6 Intermediate-Code Generation
## 6.1 Variants of Syntax Trees
通过`DAG`来代替语法树，表示程序的拓扑结构
### 6.1.1 Directed Acyclic Graphs for Expressions
### 6.1.2 The Value-Number Method for Constructing DAG's
### 6.1.3 Exercises for Section 6.1


# 8 Code Generation
## 8.5 Optimization of Basic Blocks
如何使用`DAG`来做局部代码优化
### 8.5.1 The DAG Representation of Basic Blocks
按照特定的方式为每一个基本块构造`DAG`，再之后根据这个`DAG`表示可以对基本块所表示的代码进行一些转换。

### 8.5.2 Finding Local Common Subexpressions
一个例子：
```
a = b + c
b = a - d
c = b + c
d = a - d
```
`d`这个节点是多余的，可以并入`b`中，如下所示：
![1iYPTP.png](https://s2.ax1x.com/2020/01/20/1iYPTP.png)

### 8.5.3 Dead Code Elimination
从一个`DAG`上删除所有没有附加活跃变量的根节点(没有父节点的节点)。

### 8.5.4 The Use of Algebraic Identities
- 代数恒等式
- 局部强度消减(reduction in strength)
- 常量合并(constant folding)

### 8.5.5 Representation of Array References
### 8.5.6 Pointer Assignments and Procedure Calls
### 8.5.7 Reassembling Basic Blocks From DAG's
### 8.5.8 Exercises for Section 8.5

# 9 Machine-Independent Optimizations 583
## 9.1 The Principal Sources of Optimization
### 9.1.1 Causes of Redundancy
### 9.1.2 A Running Example: Quicksort
### 9.1.3 Semantics-Preserving Transformations
### 9.1.4 Global Common Subexpressions
### 9.1.5 Copy Propagation
### 9.1.6 Dead-Code Elimination
### 9.1.7 Code Motion
### 9.1.8 Induction Variables and Reduction in Strength
