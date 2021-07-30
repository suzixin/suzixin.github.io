---
title:  PostgreSQL 数据库内核分析-c5
layout: post
categories: PostgreSQL
tags: PostgreSQL 编译 规划 书籍
excerpt: PostgreSQL 数据库内核分析-c5
---
# 第5章 查询编译
查询编译的主要认识是根据用户的查询语句生成数据库中的最优执行计划，在此过程中要考虑视图、规则以及表的连接路径等问题。

## 5.1. 概述
当PostgreSQL的后台服务进程接收到查询语句后，首先将其传递到查询分析校块，进行词法、语法和语义分析。若是简单的命令（例如建表、创建用户、备份等）则将其分配到功能性命令处理模块；对于复杂的命令（SELECT/INSERT/DELETE/UPDATE)则要为其构建查询树（Query结构体），然后交给查询重写模块。査询重写模块接收到查询树后，按照该杳询所涉及的规则和视图对査询树迸行重写，生成新的査询树。生成路径模块依据重写过的查询树，考虑关系的访问方式、连接方式和连接顺序等问题，采用动态规划算法或遗传算法，生成最优的表连接路径。最后，由最优路径生成可执行的计划，并将其传递到査询执行模块执行。

查询优化的核心是生成路径和生成计划两个模块。
查询优化要处理的问题焦点在于如何计算最优的表连接路径。

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_123000.jpg)


## 5.2. 查询分析
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_143314.jpg)

```cpp
exec_simple_query
    pg_parse_query
        raw_parser
            base_yyparse
    pg_analyze_and_rewrite
        /* 语义分析 */
        parse_analyze
            // 根据分析树生成一个对应的查询树
        /* 查询重写 */
        pg_rewrite_query
            // 继续对这一查询树进行修改，返回查询树链表
```


### 5.2.1. Lex和Yacc简介
> 参考： https://zhuanlan.zhihu.com/p/143867739

假定我们有一个温度计，我们要用一种简单的语言来控制它。关于此的一个会话、如下：

```
heat on
Heater on!
heat off
Header off!
target temperature set!
```

1.词法分析工具`Lex`
通过`Lex`命令可以从`Lex`文件生成一个包含有扫描器的C语言源代码，其他源代码可以通过调用该扫描器来实现词法分析。
`Lex`主要是通过正则表达式来定义各种`TOKEN`。
通过`example.l`来定义词法规则
```s
%{
#include <stdio.h>
#include "y.tab.h"
%}

%%
[0-9]+ return NUMBER;
heat return TOKHEAT;
on|off return STATE;
target return TOKTARGET;
temperature return TOKTEMPERATURE;
\n /* ignore end of line */;
[ \t]+ /* ignore whitespace */
%%
```

命令：
```shell
lex example.l
cc lex.yy.c -o first -ll
```

2.语法分析工具`Yacc`
从输入流中寻找某一个特定的语法结构——`example.y`
```s
commands: /* empty */
| commands command
;

command: heat_switch | target_set ;

heat_switch:
TOKHEAT STATE
{
	printf("\tHeat turned on or off\n");
};

target_set:
TOKTARGET TOKTEMPERATURE NUMBER
{
	printf("\tTemperature set\n");
};
```
编译命令:
```
lex example.l
yacc –d example.y
cc lex.yy.c y.tab.c –o example
```

### 5.2.2. 词法和语法分析
词法和语法分析输出语法树`raw_parsetree_list`。

词法和语法分析的源文件：
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_153016.jpg)

#### 5.2.2.1. `SELECT`语句在文件`gram.y`中的定义
```s
SelectStmt: select_no_parens			%prec UMINUS
			| select_with_parens		%prec UMINUS
		;

select_with_parens:
			'(' select_no_parens ')'				{ $$ = $2; }
			| '(' select_with_parens ')'			{ $$ = $2; }
		;

select_no_parens:
			simple_select						{ $$ = $1; }
			| select_clause sort_clause
				{
					insertSelectOptions((SelectStmt *) $1, $2, NIL,
										NULL, NULL, NULL,
										yyscanner);
					$$ = $1;
				}
			| select_clause opt_sort_clause for_locking_clause opt_select_limit
				{
					insertSelectOptions((SelectStmt *) $1, $2, $3,
										(Node*)list_nth($4, 0), (Node*)list_nth($4, 1),
										NULL,
										yyscanner);
					$$ = $1;
				}
			| select_clause opt_sort_clause select_limit opt_for_locking_clause
				{
					insertSelectOptions((SelectStmt *) $1, $2, $4,
										(Node*)list_nth($3, 0), (Node*)list_nth($3, 1),
										NULL,
										yyscanner);
					$$ = $1;
				}
			| with_clause select_clause
				{
					insertSelectOptions((SelectStmt *) $2, NULL, NIL,
										NULL, NULL,
										$1,
										yyscanner);
					$$ = $2;
				}
			| with_clause select_clause sort_clause
				{
					insertSelectOptions((SelectStmt *) $2, $3, NIL,
										NULL, NULL,
										$1,
										yyscanner);
					$$ = $2;
				}
			| with_clause select_clause opt_sort_clause for_locking_clause opt_select_limit
				{
					insertSelectOptions((SelectStmt *) $2, $3, $4,
										(Node*)list_nth($5, 0), (Node*)list_nth($5, 1),
										$1,
										yyscanner);
					$$ = $2;
				}
			| with_clause select_clause opt_sort_clause select_limit opt_for_locking_clause
				{
					insertSelectOptions((SelectStmt *) $2, $3, $5,
										(Node*)list_nth($4, 0), (Node*)list_nth($4, 1),
										$1,
										yyscanner);
					$$ = $2;
				}
		;

select_clause:
			simple_select							{ $$ = $1; }
			| select_with_parens					{ $$ = $1; }
		;

simple_select:
			SELECT hint_string opt_distinct target_list
			into_clause from_clause where_clause
			group_clause having_clause window_clause
				{
					SelectStmt *n = makeNode(SelectStmt);
					n->distinctClause = $3;
					n->targetList = $4;
					n->intoClause = $5;
					n->fromClause = $6;
					n->whereClause = $7;
					n->groupClause = $8;
					n->havingClause = $9;
					n->windowClause = $10;
					n->hintState = create_hintstate($2);
					n->hasPlus = getOperatorPlusFlag();
					$$ = (Node *)n;
				}
			| values_clause							{ $$ = $1; }
			| TABLE relation_expr
				{
					/* same as SELECT * FROM relation_expr */
					ColumnRef *cr = makeNode(ColumnRef);
					ResTarget *rt = makeNode(ResTarget);
					SelectStmt *n = makeNode(SelectStmt);

					cr->fields = list_make1(makeNode(A_Star));
					cr->location = -1;

					rt->name = NULL;
					rt->indirection = NIL;
					rt->val = (Node *)cr;
					rt->location = -1;

					n->targetList = list_make1(rt);
					n->fromClause = list_make1($2);
					$$ = (Node *)n;
				}
			| select_clause UNION opt_all select_clause
				{
					$$ = makeSetOp(SETOP_UNION, $3, $1, $4);
				}
			| select_clause INTERSECT opt_all select_clause
				{
					$$ = makeSetOp(SETOP_INTERSECT, $3, $1, $4);
				}
			| select_clause EXCEPT opt_all select_clause
				{
					$$ = makeSetOp(SETOP_EXCEPT, $3, $1, $4);
				}
			| select_clause MINUS_P opt_all select_clause
				{
					$$ = makeSetOp(SETOP_EXCEPT, $3, $1, $4);
				}
		;
```

#### 5.2.2.2. 实例
数据结构：
```cpp
typedef struct SelectStmt {
    NodeTag type;

    /*
     * These fields are used only in "leaf" SelectStmts.
     */
    List *distinctClause;   /* NULL, list of DISTINCT ON exprs, or
                             * lcons(NIL,NIL) for all (SELECT DISTINCT) */
    IntoClause *intoClause; /* target for SELECT INTO */
    List *targetList;       /* the target list (of ResTarget) */
    List *fromClause;       /* the FROM clause */
    Node *whereClause;      /* WHERE qualification */
    List *groupClause;      /* GROUP BY clauses */
    Node *havingClause;     /* HAVING conditional-expression */
    List *windowClause;     /* WINDOW window_name AS (...), ... */
    WithClause *withClause; /* WITH clause */

    /*
     * In a "leaf" node representing a VALUES list, the above fields are all
     * null, and instead this field is set.  Note that the elements of the
     * sublists are just expressions, without ResTarget decoration. Also note
     * that a list element can be DEFAULT (represented as a SetToDefault
     * node), regardless of the context of the VALUES list. It's up to parse
     * analysis to reject that where not valid.
     */
    List *valuesLists; /* untransformed list of expression lists */

    /*
     * These fields are used in both "leaf" SelectStmts and upper-level
     * SelectStmts.
     */
    List *sortClause;    /* sort clause (a list of SortBy's) */
    Node *limitOffset;   /* # of result tuples to skip */
    Node *limitCount;    /* # of result tuples to return */
    List *lockingClause; /* FOR UPDATE (list of LockingClause's) */
    HintState *hintState;

    /*
     * These fields are used only in upper-level SelectStmts.
     */
    SetOperation op;         /* type of set op */
    bool all;                /* ALL specified? */
    struct SelectStmt *larg; /* left child */
    struct SelectStmt *rarg; /* right child */

    /*
     * These fields are used by operator "(+)"
     */
    bool hasPlus;
    /* Eventually add fields for CORRESPONDING spec here */
} SelectStmt;
```

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_161132.jpg)

```sql
CREATE TABLE class(classno varchar(20), classname varchar(30), gno varchar(20));
CREATE TABLE student(sno varchar(20), sname varchar(30), sex varchar(5), age integer, nation varchar(20), classno varchar(20));
CREATE TABLE course(cno varchar(20), cname varchar(30), credit integer,  priorcourse varchar(20));
CREATE TABLE sc(sno varchar(20), cno varchar(20), score integer);
```

查询2005级各班高等数学的平均成绩， 且只查询平均分在`80`以上的班级， 并将结果按照升序排列。
查询命令：
```sql
SELECT classno,classname, AVG(score) AS avg_score
FROM sc, (SELECT* FROM class WHERE class.gno='2005') AS sub
WHERE sc.sno IN (SELECT sno FROM student WHERE student.classno=sub.classno) AND
      sc.cno IN (SELECT course.cno FROM course WHERE course.cname='高等数学')
GROUP BY classno, classname
HAVING AVG(score) > 80.0
ORDER BY avg_score;
```

一些重要的结构定义:
1.DISTINCT

```
opt_distinct:
			DISTINCT								{ $$ = list_make1(NIL); }
			| DISTINCT ON '(' expr_list ')'			{ $$ = $4; }
			| ALL									{ $$ = NIL; }
			| /*EMPTY*/								{ $$ = NIL; }
		;
```

2.目标属性： `SELECT`语句中所要查询的属性列表
```
target_list:
			target_el								{ $$ = list_make1($1); }
			| target_list ',' target_el				{ $$ = lappend($1, $3); }
		;
target_el:	a_expr AS ColLabel
				{
					$$ = makeNode(ResTarget);
					$$->name = $3;
					$$->indirection = NIL;
					$$->val = (Node *)$1;
					$$->location = @1;
				}
```

`ResTarget`数据结构如下：
```cpp
typedef struct ResTarget {
    NodeTag type;
    char *name;        /* column name or NULL */
    List *indirection; /* subscripts, field names, and '*', or NIL */
    Node *val;
             /* the value expression to compute or assign */
    int location;      /* token location, or -1 if unknown */
} ResTarget;
```


图5-5 分析树种目标属性的数据结构组织
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_171550.jpg)

`SELECT classno,classname, AVG(score) AS avg_score`语句对应的目标属性在内存中的数据组织结构如下图：
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_171910.jpg)

3.FROM子句
语法定义:
```cpp
from_clause:
			FROM from_list							{ $$ = $2; }
			| /*EMPTY*/								{ $$ = NIL; }
		;

from_list:
			table_ref								{ $$ = list_make1($1); }
			| from_list ',' table_ref				{ $$ = lappend($1, $3); }
		;

table_ref:	relation_expr /* 关系表达式 */
				{
					$$ = (Node *) $1;
				}
			| relation_expr alias_clause /* 取别名的关系表达式 */
				{
					$1->alias = $2;
					$$ = (Node *) $1;
				}
			| func_table
				{
					RangeFunction *n = makeNode(RangeFunction);
					n->funccallnode = $1;
					n->coldeflist = NIL;
					$$ = (Node *) n;
				}

relation_expr:
			qualified_name
				{
					/* default inheritance */
					$$ = $1;
					$$->inhOpt = INH_DEFAULT;
					$$->alias = NULL;
				}
			| qualified_name '*'

qualified_name:
			ColId
				{
					$$ = makeRangeVar(NULL, $1, @1);
				}
			| ColId indirection

RangeVar* makeRangeVar(char* schemaname, char* relname, int location)
{
    RangeVar* r = makeNode(RangeVar);

    r->catalogname = NULL;
    r->schemaname = schemaname;
    r->relname = relname;
    r->partitionname = NULL;
    r->inhOpt = INH_DEFAULT;
    r->relpersistence = RELPERSISTENCE_PERMANENT;
    r->alias = NULL;
    r->location = location;
    r->ispartition = false;
    r->partitionKeyValuesList = NIL;
    r->isbucket = false;
    r->buckets = NIL;
    r->length = 0;
    return r;
}

typedef struct RangeVar {
    NodeTag type;
    char* catalogname;   /* the catalog (database) name, or NULL */
    char* schemaname;    /* the schema name, or NULL */
    char* relname;       /* the relation/sequence name */
    char* partitionname; /* partition name, if is a partition */
    InhOption inhOpt;    /* expand rel by inheritance? recursively act
                          * on children? */
    char relpersistence; /* see RELPERSISTENCE_* in pg_class.h */
    Alias* alias;        /* table alias & optional column aliases */
    int location;        /* token location, or -1 if unknown */
    bool ispartition;    /* for partition action */
    List* partitionKeyValuesList;
    bool isbucket;       /* is the RangeVar means a hash bucket id ? */
    List* buckets;       /* the corresponding bucketid list */
    int length;
#ifdef ENABLE_MOT
    Oid foreignOid;
#endif
} RangeVar;


```

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_174410.jpg)
`FROM sc, (SELECT* FROM class WHERE class.gno='2005') AS sub`解析为：
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_174428.jpg)

4.WHERE子句
语法结构：
```
where_clause:
			WHERE a_expr							{ $$ = $2; }
			| /*EMPTY*/								{ $$ = NULL; }
		;
```

数据结构：
```cpp
typedef struct A_Expr {
    NodeTag type;
    A_Expr_Kind kind; /* see above */
    List *name;       /* possibly-qualified name of operator */
    Node *lexpr;      /* left argument, or NULL if none */
    Node *rexpr;      /* right argument, or NULL if none */
    int location;     /* token location, or -1 if unknown */
} A_Expr;
```

```SQL
WHERE sc.sno IN (SELECT sno FROM student WHERE student.classno=sub.classno) AND
      sc.cno IN (SELECT course.cno FROM course WHERE course.cname='高等数学')
```

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_180853.jpg)
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_180954.jpg)

5.`GROUP BY`子句
语法定义：
```
group_clause:
			GROUP_P BY group_by_list				{ $$ = $3; }
			| /*EMPTY*/								{ $$ = NIL; }
		;
group_by_list:
			group_by_item							{ $$ = list_make1($1); }
			| group_by_list ',' group_by_item		{ $$ = lappend($1,$3); }
		;

group_by_item:
			a_expr									{ $$ = $1; }
```

`GROUP BY classno, classname`
内存组织结构：
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-07_090157.jpg)

6.HAVING子句和ORDER BY子句
语法定义：
```
having_clause:
			HAVING a_expr							{ $$ = $2; }
			| /*EMPTY*/								{ $$ = NULL; }
		;

sort_clause:
			ORDER BY sortby_list					{ $$ = $3; }
		;

sortby_list:
			sortby									{ $$ = list_make1($1); }
			| sortby_list ',' sortby				{ $$ = lappend($1, $3); }
		;

sortby:		a_expr USING qual_all_Op opt_nulls_order
				{
					$$ = makeNode(SortBy);
					$$->node = $1;
					$$->sortby_dir = SORTBY_USING;
					$$->sortby_nulls = (SortByNulls)$4;
					$$->useOp = $3;
					$$->location = @3;
				}
```

```sql
HAVING AVG(score) > 80.0
ORDER BY avg_score;
```

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_182711.jpg)

### 5.2.3. 语义分析
检查命令中是否有不符合语义规定的成分。

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_143314.jpg)

关键数据结构：
```cpp
/* 用于记录语义分析的中间信息 */
struct ParseState {
    List* p_rtable;                      /* range table so far */
}

/* 用于存储查询树 */
typedef struct Query {
    CmdType commandType; /* select|insert|update|delete|merge|utility */
    List* rtable;       /* list of range table entries 查询中使用的表的列表 */
    int resultRelation; /* rtable index of target relation for
                         * INSERT/UPDATE/DELETE/MERGE; 0 for SELECT 
                         * 涉及数据修改的范围表的编号
                         */
    FromExpr* jointree; /* table join tree (FROM and WHERE clauses) */
    List* targetList; /* target list (of TargetEntry) */
} Query;
```

关键过程：
```cpp
/*
 * parse_analyze
 *		Analyze a raw parse tree and transform it to Query form.
 *
 * Optionally, information about $n parameter types can be supplied.
 * References to $n indexes not defined by paramTypes[] are disallowed.
 *
 * The result is a Query node.	Optimizable statements require considerable
 * transformation, while utility-type statements are simply hung off
 * a dummy CMD_UTILITY Query node.
 */
Query* parse_analyze(
    Node* parseTree, const char* sourceText, Oid* paramTypes, int numParams, bool isFirstNode, bool isCreateView)
{
    ParseState* pstate = make_parsestate(NULL);
    // 将分析树`parseTree`转换成查询树`query`
    query = transformTopLevelStmt(pstate, parseTree, isFirstNode, isCreateView);
        // 以查询为例
        static Query* transformSelectStmt(ParseState* pstate, SelectStmt* stmt, bool isFirstNode, bool isCreateView)
}
```

这里的`parseTree`数据结构通过`Node`指针来传递， 通过`NodeTag`来确定数据结构的类型。
```cpp
typedef struct Node {
    NodeTag type;
} Node;

typedef enum NodeTag {
    /*
     * TAGS FOR STATEMENT NODES (mostly in parsenodes.h)
     */
    T_Query = 700,
    T_PlannedStmt,
    T_InsertStmt,
    T_DeleteStmt,
    T_UpdateStmt,
    T_MergeStmt,
    T_SelectStmt,
    ……
}
```

可以在执行`SQL`命令时打印查询树的规则， 相关参数：
```
#debug_print_parse = off
#debug_print_rewritten = off
#debug_print_plan = off
```

分析树对应的语义分析函数如下所示：
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_193515.jpg)
1.`transformSelectStmt`函数的总体流程如下：
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_194446.jpg)

2.FROM子句的语义分析处理
`transformFromClause`负责处理`FROM`子句的语法分析，并生成范围表。(`Query::rtable`)

关键数据结构：
```cpp
typedef struct RangeTblEntry {
    NodeTag type;

    RTEKind rtekind; /* see above */
}
```

关键过程：
```cpp
void transformFromClause(ParseState* pstate, List* frmList, bool isFirstNode, bool isCreateView)
{
    foreach (fl, frmList) {
        Node* n = (Node*)lfirst(fl);
        RangeTblEntry* rte = NULL;
        int rtindex;
        List* relnamespace = NIL;

        // 根据`fromClause`的`Node`产生一个或多个`RangeTblEntry`结构， 加入到`ParseState::p_rtable`中
        n = transformFromClauseItem(
            pstate, n, &rte, &rtindex, NULL, NULL, &relnamespace, isFirstNode, isCreateView);
            Node* transformFromClauseItem(ParseState* pstate, Node* n, RangeTblEntry** top_rte, int* top_rti,
            RangeTblEntry**  right_rte, int* right_rti, List** relnamespace, bool isFirstNode, bool isCreateView, bool isMergeInto)
            {
                // 普通表
                if (IsA(n, RangeVar)) {
                    /* Plain relation reference, or perhaps a CTE reference */
                    RangeVar* rv = (RangeVar*)n;
                    RangeTblRef* rtr = NULL;
                    RangeTblEntry* rte = NULL;
            
                    /* if it is an unqualified name, it might be a CTE reference */
                    if (!rv->schemaname) {
                        CommonTableExpr* cte = NULL;
                        Index levelsup;
            
                        cte = scanNameSpaceForCTE(pstate, rv->relname, &levelsup);
                        if (cte != NULL) {
                            // 将其作为一个`RTE`加入到`ParseState::p_rtable`中
                            rte = transformCTEReference(pstate, rv, cte, levelsup);
                        }
                    }
            
                    /* if not found as a CTE, must be a table reference */
                    if (rte == NULL) {
                        rte = transformTableEntry(pstate, rv, isFirstNode, isCreateView);
                    }
            
                    rtr = transformItem(pstate, rte, top_rte, top_rti, relnamespace);
                    return (Node*)rtr;
                }
            }
        // 执行重名检查
        checkNameSpaceConflicts(pstate, pstate->p_relnamespace, relnamespace);
```

`From`子句得到的`Query`如下：
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_200915.jpg)

> 我的小问题： `Query`和`RangeTblEntry`数据结构之间的关系是什么？


在生成`query`的过程中，可以利用`ParseState::p_rtable`的结构来生成，这个结构是一个链表，它的子节点是`RangeTblEntry`类型。
```cpp
Query* parse_analyze(
    Node* parseTree, const char* sourceText, Oid* paramTypes, int numParams, bool isFirstNode, bool isCreateView)
{
    ParseState* pstate = make_parsestate(NULL);
    // 将分析树`parseTree`转换成查询树`query`
    query = transformTopLevelStmt(pstate, parseTree, isFirstNode, isCreateView);
        // 以查询为例
        static Query* transformSelectStmt(ParseState* pstate, SelectStmt* stmt, bool isFirstNode, bool isCreateView)
            /* process the FROM clause */
            transformFromClause(pstate, stmt->fromClause, isFirstNode, isCreateView); {
                foreach (fl, frmList) {
                    Node* n = (Node*)lfirst(fl);
                    RangeTblEntry* rte = NULL;
                    // 根据`fromClause`的`Node`产生一个或多个`RangeTblEntry`结构， 加入到`ParseState::p_rtable`中
                    n = transformFromClauseItem(pstate, n, &rte, &rtindex, NULL, NULL, &relnamespace, isFirstNode, isCreateView);
                }
            }
}
```

-----

3.目标属性的语义分析处理
```cpp
Query* parse_analyze(
    Node* parseTree, const char* sourceText, Oid* paramTypes, int numParams, bool isFirstNode, bool isCreateView)
{
    ParseState* pstate = make_parsestate(NULL);
    // 将分析树`parseTree`转换成查询树`query`
    query = transformTopLevelStmt(pstate, parseTree, isFirstNode, isCreateView);
        // 以查询为例
        static Query* transformSelectStmt(ParseState* pstate, SelectStmt* stmt, bool isFirstNode, bool isCreateView)
            Query* qry = makeNode(Query);
            /* transform targetlist */
            qry->targetList = transformTargetList(pstate, stmt->targetList);
                // * Turns a list of ResTarget's into a list of TargetEntry's.
                foreach (o_target, targetlist) {
                    // 多列元素`*`
                    p_target = list_concat(p_target, ExpandColumnRefStar(pstate, cref, true));
                    p_target = list_concat(p_target, ExpandIndirectionStar(pstate, ind, true));
                    // 单列
                    p_target = lappend(p_target, transformTargetEntry(pstate, res->val, NULL, res->name, false));
                }

}
```

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_201840.jpg)

4.WHERE子句的语义分析处理
```cpp
    /* transform WHERE
     * Only "(+)" is valid when  it's in WhereClause of Select, set the flag to be trure
     * during transform Whereclause.
     */
    Node* qual = NULL;
    setIgnorePlusFlag(pstate, true);
    qual = transformWhereClause(pstate, stmt->whereClause, "WHERE");
    setIgnorePlusFlag(pstate, false);
    qry->jointree = makeFromExpr(pstate->p_joinlist, qual);
```

连接树`jointree`整体的数据组织结构如下：
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-06_201743.jpg)

------

```sql
SELECT classno,classname, AVG(score) AS avg_score
FROM sc, (SELECT* FROM class WHERE class.gno='2005') AS sub
WHERE sc.sno IN (SELECT sno FROM student WHERE student.classno=sub.classno) AND
      sc.cno IN (SELECT course.cno FROM course WHERE course.cname='高等数学')
GROUP BY classno, classname
HAVING AVG(score) > 80.0
ORDER BY avg_score;
```

## 5.3. 查询重写
### 5.3.1. 规则系统
规则系统可以理解成编译器中的`PASS`，在系统表`pg_rewrite`中存储重写规则.
系统表`pg_rewrite`的`scheme`如下所示：
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-07_102617.jpg)


### 5.3.2. 查询重写的处理操作
## 5.4. 查询规划
查询优化的核心思想是“尽量先做选择操作，后做连接操作”。


### 5.4.1. 总体处理流程
**预处理**：对查询树`Query`进行进一步改造，最重要的是提升子链接和提升子查询。
**生成路径**： 采用动态规划算法或遗传算法，生成最优连接路径和候选的路径链表。
**生成计划**： 先生成基本计划树，然后添加子句所定义的计划节点形成完整计划树。
**查询规划模块**： 入口函数`pg_plan_queries`，将查询树链表变成执行计划链表，只处理非`Utilitiy`命令。调用`pg_plan_query`对每一个查询树进行处理，并将生成的`PlannedStmt`结构体构成一个链表返回。
```plantuml
digraph G {
    pg_plan_queries -> pg_plan_query -> planner
    planner -> standard_planner [label="Query* parse"]
    standard_planner -> planner [label="PlannedStmt*"]
}
```
从`planner`函数开始进入执行计划的生成阶段， `PlannedStmt`结构体包含了执行器执行该查询所需要的全部信息。

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_102513.jpg)

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_105349.jpg)
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_105431.jpg)
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_105509.jpg)


### 5.4.2. 实例分析
#### 5.4.2.1. 查询分析之后的查询树
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_105821.jpg)

查询2005级各班高等数学的平均成绩， 且只查询平均分在`80`以上的班级， 并将结果按照升序排列。
原始查询命令：
```sql
SELECT classno,classname, AVG(score) AS avg_score
FROM sc, (SELECT* FROM class WHERE class.gno='2005') AS sub
WHERE sc.sno IN (SELECT sno FROM student WHERE student.classno=sub.classno) AND
      sc.cno IN (SELECT course.cno FROM course WHERE course.cname='高等数学')
GROUP BY classno, classname
HAVING AVG(score) > 80.0
ORDER BY avg_score;
```

#### 5.4.2.2. 提升子链接
将`WHERE`子句中的子链接提升成为范围表

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_111050.jpg)


提升后的查询命令如下：
```sql
SELECT sub.classno, sub.classname, AVG(score) AS avg_score
FROM sc, (SELECT* FROM class WHERE class.gno='2005') AS sub, (SELECT course.cno FROM course WHERE course.cname='高等数学') AS ANY_subquery
WHERE sc.sno IN (SELECT sno FROM student WHERE student.classno=sub.classno) 
    AND sc.cno = ANY_subquery.cno
GROUP BY classno, classname
HAVING AVG(score) > 80.0
ORDER BY avg_score;
```

#### 5.4.2.3. 提升子查询
对于子查询`(SELECT* FROM class WHERE class.gno='2005') AS sub`，提升后如下:
```sql
SELECT class.classno, class.classname, AVG(score) AS avg_score
FROM sc, (SELECT* FROM class WHERE class.gno='2005') AS sub, (SELECT course.cno FROM course WHERE course.cname='高等数学') AS ANY_subquery, class, course
WHERE sc.sno IN (SELECT sno FROM student WHERE student.classno=sub.classno) 
    AND sc.cno = course.cno
    AND course.cname = '高等数学'
    AND class.gno = '2005'
GROUP BY classno, classname
HAVING AVG(score) > 80.0
ORDER BY avg_score;
```

子查询整体提升完毕后如下：
```sql
SELECT classno, classname, AVG(score) AS avg_score
FROM sc, class, course
WHERE sc.sno IN (SELECT sno FROM student WHERE student.classno=sub.classno) 
    AND sc.cno = course.cno
    AND course.cname = '高等数学'
    AND class.gno = '2005'
GROUP BY classno, classname
HAVING AVG(score) > 80.0
ORDER BY avg_score;
```

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_112909.jpg)

#### 5.4.2.4. 生成路径
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_113048.jpg)
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_113056.jpg)
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_113108.jpg)

#### 5.4.2.5. 生成计划
![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/2021-01-12_113019.jpg)
