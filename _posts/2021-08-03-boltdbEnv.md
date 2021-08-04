---
title:  boltdb开发环境部署
layout: post
categories: 数据库内核
tags: 数据库内核 boltdb
excerpt: 
---

# 1. 参考
- [bolt](https://github.com/boltdb/bolt)
- [BoltDB 使用入门实践](https://learnku.com/articles/34683)
- [技术文档](https://pkg.go.dev/github.com/boltdb/bolt)

# 2. 编译与安装
## 2.1. golang
参考：  
- 安装
    - [JetBrains全系列软件激活教程激活码以及JetBrains系列软件汉化包](https://www.macwk.com/article/jetbrains-crack)
    - [GoLand 2021.2 破解版 (专业的 Go 开发集成环境) (官方版 + 补丁/许可证)](https://www.macwk.com/soft/goland)
- 入门
    - [如何使用Go编程](https://go-zh.org/doc/code.html)
    创建程序、包；
    - [实效Go编程](https://go-zh.org/doc/effective_go.html)
    - [Go语言之旅](https://tour.golang.org/)
    官方学习课程

快捷键：[Mac Shortcuts](https://resources.jetbrains.com/storage/products/goland/docs/GoLand_ReferenceCard_macOS.pdf?_gl=1*14yd1cp*_ga*MjA5MzA0MzE3NC4xNjI3OTkzMTQz*_ga_V0XZL7QHEB*MTYyNzk5MzE0MS4xLjEuMTYyNzk5MzIxMC4w&_ga=2.14568631.1274109547.1627993143-2093043174.1627993143)

![](https://suzixinblog.oss-cn-shenzhen.aliyuncs.com/20210803202058.png)

> 我的小问题： go中多线程如何使用？

参考： [Go goroutine理解](https://zhuanlan.zhihu.com/p/60613088)

> DO NOT COMMUNICATE BY SHARING MEMORY; INSTEAD, SHARE MEMORY BY COMMUNICATING.

go中的`CSP`并发模型就是使用了这种思想。

Go的CSP并发模型，是通过`goroutine`和`channel`来实现的。

- `goroutine` 是Go语言中并发的执行单位。有点抽象，其实就是和传统概念上的”线程“类似，可以理解为”线程“。
- `channel`是Go语言中各个并发结构体(`goroutine`)之前的通信机制。 通俗的讲，就是各个`goroutine`之间通信的”管道“，有点类似于Linux中的管道。

一个实例如下:
```go
package main

import "fmt"

func main() {
   
   messages := make(chan string)

   go func() { messages <- "ping" }()

   msg := <-messages
   fmt.Println(msg)
}
```

-----

## 2.2. boltdb
参考 ： https://github.com/boltdb/bolt

将`boltdb`编译成包
```
go mod init github.com/boltdb/bolt
go build
```

编译测试程序：
创建`data`目录， 在该目录下创建`client.go`文件。

```go
package main

import (
    "log"

    "github.com/boltdb/bolt"
)

func main() {
    // Open the my.db data file in your current directory.
    // It will be created if it doesn't exist.
    db, err := bolt.Open("my.db", 0600, nil)
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()
}
```

在当前目录下运行如下：
```
go run client.go
```


# 3. 使用
## 3.1. 事务
To work with data in multiple goroutines you must start a transaction for each one or use locking to ensure only one goroutine accesses a transaction at a time. Creating transaction from the DB is thread safe.

要处理多个 goroutine 中的数据，您必须为每个 goroutine 启动一个事务，或者使用锁定来确保一次只有一个 goroutine 访问一个事务。从`DB`创建事务是线程安全的。

> 我的小问题： 该数据库的多线程是如何使用的？

- 起多个线程打开数据库

--------

## 3.2. 增查
```go
func main() {
    // Open the my.db data file in your current directory.
    // It will be created if it doesn't exist.
    db, err := bolt.Open("my.db", 0600, nil)
    if err != nil {
        log.Fatal(err)
    }

    db.Update(func(tx *bolt.Tx) error {
       b, err := tx.CreateBucket([]byte("MyBucket"))
       if err != nil {
           return fmt.Errorf("create bucket: %s", err)
       }
       err = b.Put([]byte("answer"), []byte("42"))
       return err
    })
    db.Update(func(tx *bolt.Tx) error {
       b := tx.Bucket([]byte("MyBucket"))
       err = b.Put([]byte("suzixin"), []byte("43"))
       return err
    })
    
    db.View(func(tx *bolt.Tx) error {
       // Assume bucket exists and has keys
       b := tx.Bucket([]byte("MyBucket"))
    
       c := b.Cursor()
    
       for k, v := c.First(); k != nil; k, v = c.Next() {
           fmt.Printf("key=%s, value=%s\n", k, v)
       }
    
       return nil
    })

    defer db.Close()
}
```



# 4. 调试
## 4.1. boltd
参考： https://github.com/boltdb/boltd

安装
```
go get github.com/boltdb/boltd/...
```

使用
```
~/go/bin/boltd my.db
```

## 4.2. lldb调试
参考  
[lldb-golang-debug](https://zddhub.com/memo/2015/12/20/lldb-golang-debug.html)

无法设置断点

## 4.3. delve
### 4.3.1. 特性
- 在调试的过程中可以修改代码
- debug from mian
- devel是一个编译器

### 4.3.2. 安装
```
go install github.com/go-delve/delve/cmd/dlv@latest
```

### 4.3.3. 设置环境变量
```
export GOPATH=~/go
export PATH=$PATH:$GOPATH/bin
```

### 4.3.4. 常用命令
```shell
#Running the program#
continue
break main.main
break package/filename.go:linenumber
# step over
n
# step in
s

#Viewing program variables and memory#
# 查看局部变量
locals
# 设置变量
set value=""
# 查看变量
print value

#Other commands#
# 查看源码
list
```


## 4.4. goland调试
参考： 

> 我的小问题： 如何使用goland调试helloworld？

参考： [debugging-with-goland-getting-started](https://blog.jetbrains.com/go/2019/02/06/debugging-with-goland-getting-started/)

直接创建包含`main`函数的文件后使用IDE debug即可。

--------

> 我的小问题： 如何使用goland调试库？

在创建模块的时候要使用`go mod init`来创建`go.mod`文件将该目录声明为一个模块。

--------

> 我的小问题： 如何使用goland调试bolt库？

发现了如下bug:  
[Fatal error 'bad access: nil dereference' while Debugging in Goland](https://youtrack.jetbrains.com/issue/GO-8953)

放弃使用goland。


# 5. 问题
## 5.1. go包安装慢
参考 [GO命令中go get拉取库卡住、慢的解决方法](https://blog.csdn.net/weixin_44384146/article/details/106561414)

```
export GOPROXY=https://goproxy.io
```

## 5.2. go引用boltdb模块失败
创建`data`目录， 在该目录下创建`client.go`文件。

```go
package main

import (
    "log"

    "github.com/boltdb/bolt"
)

func main() {
    // Open the my.db data file in your current directory.
    // It will be created if it doesn't exist.
    db, err := bolt.Open("my.db", 0600, nil)
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()
}
```

在当前目录下运行如下：
```
go run client.go
```

提示错误如下：
```
$ go run client.go 
client.go:6:5: no required module provides package github.com/boltdb/bolt: go.mod file not found in current directory or any parent directory; see 'go help modules'
```

将`bolt`编译成一个模块

```
go mod init github.com/boltdb/bolt
go build
```

重新编译测试程序：
```
cd data
go build
```

## 5.3. goland调试出错
提示如下：
```
panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x1 addr=0x8 pc=0x10ad866]

goroutine 1 [running]:
github.com/boltdb/bolt.(*Bucket).ForEach(0x0, 0x10e6d08, 0x10dfc2d, 0xb)
        /Users/suzixin/git/bolt/bucket.go:385 +0x26
main.main.func1(0xc0000c4000, 0x0, 0xc0000c4000)
        /Users/suzixin/git/bolt/data/client.go:60 +0x85
github.com/boltdb/bolt.(*DB).View(0xc0000c0000, 0x10e6d10, 0x0, 0x0)
        /Users/suzixin/git/bolt/db.go:629 +0x93
main.main()
        /Users/suzixin/git/bolt/data/client.go:52 +0xcd
```

参考： [Fatal error 'bad access: nil dereference' while Debugging in Goland](https://youtrack.jetbrains.com/issue/GO-8953)

- 将goland切换为`2019.3.2`版本， 现象不变

## 5.4. delve安装失败
需要设置环境变量，如下
```
export GOPATH=~/go
export PATH=$PATH:$GOPATH/bin
```