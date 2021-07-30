---
title:  redis实战
layout: post
categories: 数据库应用
tags: 数据库应用 redis 书籍
excerpt: redis实战
---
# 关于本书
> [reids实战](http://redisinaction.com/preview/chapter3.html#id2)

第一部分：基本介绍
c1 - c2
第二部分：对`redis`多个命令进行详细介绍，介绍了`redis`的管理操作以及使用`redis`构建更复杂的应用程序的方法；
c3 - c8

第三部分：介绍如何通过内存优化、水平分片以及`Lua`脚本来扩展`redis`。
c9 - c11
通过复制、持久化（persistence）和客户端分片（client-side sharding）等特性，用户可以很方便地将Redis扩展成一个能够包含数百GB数据、每秒钟处理上百万次请求的系统。

代码下载：
[所有代码清单的源代码](https://www.manning.com/books/redis-in-action)
[用Python语言编写的源代码](github.com/josiahcarlson/redis-in-action)

# 第1章 初识Redis
> 在使用类似Redis这样的内存数据库时，一个首先要考虑的问题就是“当服务器被关闭时，服务器存储的数据将何去何从呢？”

redis的持久化方法：
- 时间点转储（point-in-time dump）

- 将所有修改了数据库的命令都写入到一个只追加（append-only）文件里面
用户可以根据数据的重要程度，将只追加写入设置为从不同步（sync）、每秒钟同步一次或者每写入一个命令就同步一次

------------------------------

> redis的性能优势在哪里？为什么说它是内存数据库？

在Redis里面，用户可以直接使用原子的（atomic）INCR命令及其变种来计算聚合数据，并且因为Redis将数据存储在内存里面，而且发送给Redis的命令请求并不需要经过典型的查询分析器（parser）或者查询优化器（optimizer）进行处理，所以对Redis存储的数据执行随机写的速度总是非常快。
使用Redis而不是关系数据库或者其他磁盘存储数据库，可以避免写入不必要的临时数据，也免去了对临时数据进行扫描或者删除的麻烦，并最终改善程序的性能。

------------------------------


介绍`5`种数据类型及相关命令案例
举了一个如何使用Redis来构建一个简单的文章投票网站的后端的例子：
- 获取文章
- 发布文章
- 对文章进行投票
- 对文章进行分组

# 第2章 使用Redis构建Web应用
- 登录cookie
- 购物车cookie
- 缓存生成的网页
- 缓存数据库行
- 分析网页访问记录

# 第3章 Redis命令
[完整命令列表](https://redis.io/commands)
[redis命令参考](http://redisdoc.com/transaction/watch.html)

## 3.2 [列表](http://redisinaction.com/preview/chapter3.html#id2)
- `BLPOP`:`BLPOP(key-name, [key-name ...], timeout)`——从第一个非空列表中弹出位于最左端的元素，或者在timeout秒之内阻塞并等待可弹出的元素出现。
- `BRPOPLPUSH`：`BRPOPLPUSH(source-key, sdest-key, timeout)`——从`source-key`列表中弹出位于最右端的元素，然后将这个元素推入到`dest-key`列表的最左端，并向用户返回这个元素；如果`source-key`为空，那么在timeout秒之内阻塞并等待可弹出的元素出现。

`BLPOP`命令举例如下:
```
init:
list: ['item3', 'item1'] 
list2:['item2']

conn.blpop(['list', 'list2'], 1) 
list: ['item1'] 
list2:['item2']

conn.blpop(['list', 'list2'], 1) 
list: [] 
list2:['item2']

conn.blpop(['list', 'list2'], 1) 
list: [] 
list2:[]

```

## 3.6 [发布与订阅](http://redisinaction.com/preview/chapter3.html#id8)
命令如下所示：
- SUBSCRIBE
SUBSCRIBE channel [channel ...]——订阅给定的一个或多个频道
- UNSUBSCRIBE
UNSUBSCRIBE [channel [channel ...]]——退订给定的一个或多个频道，如果执行时没有给定任何频道，那么退订所有频道
- PUBLISH
PUBLISH channel message——向给定频道发送消息
- PSUBSCRIBE
PSUBSCRIBE pattern [pattern ...]——订阅与给定模式相匹配的所有频道
- PUNSUBSCRIBE
PUNSUBSCRIBE [pattern [pattern ...]]——退订给定的模式，如果执行时没有给定任何模式，那么退订所有模式


以下是一个`python`中的使用例子：
```python
>>> def publisher(n):
...     time.sleep(1)                                                   # 函数在刚开始执行时会先休眠，让订阅者有足够的时间来连接服务器并监听消息。
...     for i in xrange(n):
...         conn.publish('channel', i)                                  # 在发布消息之后进行短暂的休眠，
...         time.sleep(1)                                               # 让消息可以一条接一条地出现。
...
>>> def run_pubsub():
...     threading.Thread(target=publisher, args=(3,)).start()
...     pubsub = conn.pubsub()
...     pubsub.subscribe(['channel'])
...     count = 0
...     for item in pubsub.listen():
...         print item
...         count += 1
...         if count == 4:
...             pubsub.unsubscribe()
...         if count == 5:
...             break
...

>>> def run_pubsub():
...     threading.Thread(target=publisher, args=(3,)).start()           # 启动发送者线程发送三条消息。
...     pubsub = conn.pubsub()                                          # 创建发布与订阅对象，并让它订阅给定的频道。
...     pubsub.subscribe(['channel'])                                   #
...     count = 0
...     for item in pubsub.listen():                                    # 通过遍历pubsub.listen()函数的执行结果来监听订阅消息。
...         print item                                                  # 打印接收到的每条消息。
...         count += 1                                                  # 在接收到一条订阅反馈消息和三条发布者发送的消息之后，
...         if count == 4:                                              # 执行退订操作，停止监听新消息。
...             pubsub.unsubscribe()                                    #
...         if count == 5:                                              # 当客户端接收到退订反馈消息时，
...             break                                                   # 需要停止接收消息。
...
>>> run_pubsub()                                                        # 实际运行函数并观察它们的行为。
{'pattern': None, 'type': 'subscribe', 'channel': 'channel', 'data': 1L}# 在刚开始订阅一个频道的时候，客户端会接收到一条关于被订阅频道的反馈消息。
{'pattern': None, 'type': 'message', 'channel': 'channel', 'data': '0'} # 这些结构就是我们在遍历pubsub.listen()函数时得到的元素。
{'pattern': None, 'type': 'message', 'channel': 'channel', 'data': '1'} #
{'pattern': None, 'type': 'message', 'channel': 'channel', 'data': '2'} #
{'pattern': None, 'type': 'unsubscribe', 'channel': 'channel', 'data':  # 在退订频道时，客户端会接收到一条反馈消息，
0L}                                                                     # 告知被退订的是哪个频道，以及客户端目前仍在订阅的频道数量。
```
虽然Redis的发布与订阅模式非常有用，但本书只在这一节和第8.5节使用了这个模式，这样做的原因有以下两个。

**第一个原因和Redis系统的稳定性有关**。对于旧版Redis来说，如果一个客户端订阅了某个或某些频道，但它读取消息的速度却不够快的话，那么不断积压的消息就会使得Redis输出缓冲区的体积变得越来越大，这可能会导致Redis的速度变慢，甚至直接崩溃。也可能会导致Redis被操作系统强制杀死，甚至导致操作系统本身不可用。新版的Redis不会出现这种问题，因为它会自动断开不符合`client-output-buffer-limit pubsub`配置选项（关于这个选项的具体信息本书在将第8章进行介绍）要求的订阅客户端。

**第二个原因和数据传输的可靠性有关**。任何网络系统在执行操作时都可能会遇上断线情况，而断线产生的连接错误通常会使得网络连接两端中的其中一端进行重新连接。本书使用的Python语言的Redis客户端会在连接失效时自动进行重新连接，也会自动处理连接池（connection pool，具体信息将在第4章介绍），诸如此类。但是，**如果客户端在执行订阅操作的过程中断线，那么客户端将丢失在断线期间发送的所有消息**，因此依靠频道来接收消息的用户可能会对Redis提供的PUBLISH命令和SUBSCRIBE命令的语义感到失望。

基于以上两个原因，本书在**第6章编写了两个不同的方法来实现可靠的消息传递操作**，这两个方法除了可以处理网络断线之外，还可以防止Redis因为消息积压而耗费过多内存（这个方法即使对于旧版Redis也是有效的）。

如果你喜欢简单易用的PUBLISH命令和SUBSCRIBE命令，并且能够承担可能会丢失一小部分数据的风险，那么你也可以继续使用Redis提供的发布与订阅特性，而不是本书在8.5节提供的实现，只要记得先把client-output-buffer-limit pubsub选项设置好就行了。



# 第4章 数据安全与性能保障
## 4.4 redis事务
在多个客户端同时处理相同的数据时，使用事务可以防止出错，提升性能。
**事务的基本使用方法**：
```shell
MULTI // 开始
……
EXEC // 结束
```

**流水线(pipeline)**：一次性发送多个命令，然后等待所有回复出现，它可以通过减少客户端与redis服务器之间的网络通信次数来提升redis在执行多个命令时的性能。

下面介绍一个买卖市场的案例。

### 4.4.1 定义用户信息和用户包裹
数据结构：
![liIygx.png](https://s2.ax1x.com/2019/12/25/liIygx.png)

![liI2DO.png](https://s2.ax1x.com/2019/12/25/liI2DO.png)

### 4.4.2 将商品放到市场上销售
```python
def list_item(conn, itemid, sellerid, price):
    inventory = "inventory:%s"%sellerid
    item = "%s.%s"%(itemid, sellerid)
    end = time.time() + 5
    pipe = conn.pipeline()

    while time.time() < end:
        try:
            pipe.watch(inventory)                    #A
            if not pipe.sismember(inventory, itemid):#B
                pipe.unwatch()                       #E
                return None

            pipe.multi()                             #C
            pipe.zadd("market:", {item: price})      #C
            pipe.srem(inventory, itemid)             #C
            pipe.execute()                           #F
            return True
        except redis.exceptions.WatchError:          #D
            pass                                     #D
    return False
#A Watch for changes to the users's inventory
#B Verify that the user still has the item to be listed
#E If the item is not in the user's inventory, stop watching the inventory key and return
#C Actually list the item
#F If execute returns without a WatchError being raised, then the transaction is complete and the inventory key is no longer watched
#D The user's inventory was changed, retry
#END
```

该函数的执行过程如下所示：

![li7lUe.png](https://s2.ax1x.com/2019/12/25/li7lUe.png)

### 4.4.3 购买商品
```python
def purchase_item(conn, buyerid, itemid, sellerid, lprice):
    buyer = "users:%s"%buyerid
    seller = "users:%s"%sellerid
    item = "%s.%s"%(itemid, sellerid)
    inventory = "inventory:%s"%buyerid
    end = time.time() + 10
    pipe = conn.pipeline()

    while time.time() < end:
        try:
            pipe.watch("market:", buyer)                #A

            price = pipe.zscore("market:", item)        #B
            funds = int(pipe.hget(buyer, "funds"))      #B
            if price != lprice or price > funds:        #B
                pipe.unwatch()                          #B
                return None

            pipe.multi()                                #C
            pipe.hincrby(seller, "funds", int(price))   #C
            pipe.hincrby(buyer, "funds", int(-price))   #C
            pipe.sadd(inventory, itemid)                #C
            pipe.zrem("market:", item)                  #C
            pipe.execute()                              #C
            return True
        except redis.exceptions.WatchError:             #D
            pass                                        #D

    return False
#A Watch for changes to the market and to the buyer's account information
#B Check for a sold/repriced item or insufficient funds
#C Transfer funds from the buyer to the seller, and transfer the item to the buyer
#D Retry if the buyer's account or the market changed
#END
```
`watch`命令的接口如下：
```
WATCH key [key ...]
```

在这里，同时`watch`了`market`和`buyer`的数据结构。

数据结构转化图如下所示：

![liOjCF.png](https://s2.ax1x.com/2019/12/25/liOjCF.png)

> 为什么redis没有典型的加锁功能？

`watch`命令可以看做是乐观锁，他的优点是客户端永远不必花时间去等待第一个取得锁的客户端——他们只需要在自己的事务执行失败时重试就可以了。
而传统数据库用的悲观锁虽然安全有效，但是对性能的影响也比较大。

---------------------------------

## 4.6 关于性能方面的注意事项

![livFpD.png](https://s2.ax1x.com/2019/12/25/livFpD.png)

# 第6章 使用 Redis 构建应用组件
## 6.2 分布式锁
redis使用`watch`命令来代替对数据进行加锁，这个命令也被称为乐观锁，因为**它不会阻止其他客户端对数据进行修改**。
```
WATCH key [key …]

监视一个(或多个) key ，如果在事务执行之前这个(或这些) key 被其他命令所改动，那么事务将被打断。
```
在redis应用程序中，会使用redis来构建锁，而不是使用其他操作系统级别、编程语言级别的锁，例如redis提供的`SETEX`命令有基本的加锁功能。
分布式锁也有类似`acquire; do something; release`动作的，不过这种锁是由不同机器上的不同redis客户端进行获取和释放的。

### 6.2.1 锁的重要性

> 为什么使用watch命令来监视被频繁访问的key可能会引起性能问题?

因为watch频繁修改的key失败率很高，导致大量的重试自旋操作。性能结果如下所示：

![lF9I0J.png](https://s2.ax1x.com/2019/12/25/lF9I0J.png)

所以需要锁的登场。

---------------

### 6.2.3 使用redis构建锁
使用`SETNX`命令：
```
SETNX key value
只在键 key 不存在的情况下， 将键 key 的值设置为 value 。
若键 key 已经存在， 则 SETNX 命令不做任何动作。
```


```python
#A Watch for changes to the market and the buyer's account information
#B Check for a sold/repriced item or insufficient funds
#C Transfer funds from the buyer to the seller, and transfer the item to the buyer
#END

def acquire_lock(conn, lockname, acquire_timeout=10):
    identifier = str(uuid.uuid4())                      #A

    end = time.time() + acquire_timeout
    while time.time() < end:
        if conn.setnx('lock:' + lockname, identifier):  #B
            return identifier

        time.sleep(.001)

    return False
#A A 128-bit random identifier
#B Get the lock
#END
```

> 如何释放锁？

删除`lock:lockname`。

```python
def release_lock(conn, lockname, identifier):
    pipe = conn.pipeline(True)
    lockname = 'lock:' + lockname
    if isinstance(identifier, str):
        identifier = identifier.encode()

    while True: # 注意这里有一个无限循环
        try:
            pipe.watch(lockname)                  #A
            if  pipe.get(lockname) == identifier:  #A
                pipe.multi()                      #B
                pipe.delete(lockname)             #B
                pipe.execute()                    #B
                return True                       #B

            pipe.unwatch()
            break

        except redis.exceptions.WatchError:       #C
            pass                                  #C

    return False                                  #D
#A Check and verify that we still have the lock, 同时防止程序错误地释放同一个锁多次
#B Release the lock
#C Someone else did something with the lock, retry
#D We lost the lock
#END
```

----------------------------

使用锁来代替`4.4`中的`watch`操作，如下所示：
```python
def purchase_item_with_lock(conn, buyerid, itemid, sellerid):
    buyer = "users:%s" % buyerid
    seller = "users:%s" % sellerid
    item = "%s.%s" % (itemid, sellerid)
    inventory = "inventory:%s" % buyerid

    locked = acquire_lock(conn, 'market:')     #A
    if not locked:
        return False

    pipe = conn.pipeline(True)
    try:
        pipe.zscore("market:", item)           #B
        pipe.hget(buyer, 'funds')              #B
        price, funds = pipe.execute()          #B
        if price is None or price > funds:     #B
            return None                        #B

        pipe.hincrby(seller, 'funds', int(price))  #C
        pipe.hincrby(buyer, 'funds', int(-price))  #C
        pipe.sadd(inventory, itemid)               #C
        pipe.zrem("market:", item)                 #C
        pipe.execute()                             #C
        return True
    finally:
        release_lock(conn, 'market:', locked)      #D
#A Get the lock
#B Check for a sold item or insufficient funds
#C Transfer funds from the buyer to the seller, and transfer the item to the buyer
#D Release the lock
#END
```
看起来这把锁是用来加锁整个购买操作的，实际上这把锁是用来锁住市场数据的。

使用锁实现之后性能提升如下所示：

![lFV6zR.png](https://s2.ax1x.com/2019/12/25/lFV6zR.png)

> 如何评价读/写的偏好？

可以查看买卖操作的执行次数比率跟买家数量和卖家数量之间的比率，如果基本一致，说明这个系统对买家和卖家是比较公平的。

------------------------------------

### 6.2.4 细粒度锁
通过使用粒度更细的锁——只对单个商品进行加锁，性能提升如下：

![lFVHSA.png](https://s2.ax1x.com/2019/12/25/lFVHSA.png)

> 使用细粒度锁会有什么问题？

在数据结构复杂的时候如何确定锁的粒度、应该对小部分数据进行加锁还是直接锁住整个结构的判断变得困难起来。

------------------------------------

> 什么是`dogpile`效应？

------------------------------------

### 6.2.5 带有超时限制特性的锁
```python
def acquire_lock_with_timeout(
    conn, lockname, acquire_timeout=10, lock_timeout=10):
    identifier = str(uuid.uuid4())                      #A
    lockname = 'lock:' + lockname
    lock_timeout = int(math.ceil(lock_timeout))         #D

    end = time.time() + acquire_timeout
    while time.time() < end:
        if conn.setnx(lockname, identifier):            #B
            conn.expire(lockname, lock_timeout)         #B
            return identifier
        elif conn.ttl(lockname) < 0:                    #C
            conn.expire(lockname, lock_timeout)         #C

        time.sleep(.001)

    return False
#A A 128-bit random identifier
#B Get the lock and set the expiration
#C Check and update the expiration time as necessary 
#D Only pass integers to our EXPIRE calls
#END 
```

`TTL key`：当 key 不存在时，返回 -2 。 当 key 存在但没有设置剩余生存时间时，返回 -1 。 否则，以秒为单位，返回 key 的剩余生存时间。

> **Note**
在 Redis 2.8 以前，当 key 不存在，或者 key 没有设置剩余生存时间时，命令都返回 -1 。

注意区分该接口中`acquire_timeout`和`lock_timeout`之间的区别。


## 6.3 计数信号量
让多个客户端同时访问相同的信息时，计数信号量就是完成这项任务的最佳工具。


## 6.4 任务队列
### 6.4.1 先进先出队列
> 参考：redis实战 6.4.1

最简单的`deom`:
- send_sold_email_via_queue()
将待发送的邮件放进队列
- process_sold_email_queue()
将待发送的邮件从队列中取出并发送

其他问题
1. 多个可执行任务
可以采用以下的通用执行流程：
```python
def worker_watch_queue(conn, queue, callbacks):
    while not QUIT:
        packed = conn.blpop([queue], 30)                    #A
        if not packed:                                      #B
            continue                                        #B

        name, args = json.loads(packed[1])                  #C
        if name not in callbacks:                           #D
            log_error("Unknown callback %s"%name)           #D
            continue                                        #D
        callbacks[name](*args)                              #E
#A Try to get an item from the queue
#B There is nothing to work on, try again
#C Unpack the work item
#D The function is unknown, log the error and try again
#E Execute the task
#END
```

2. 任务优先级
对以上监听线程，可以添加任务优先级的判断，如下所示：
```python
def worker_watch_queues(conn, queues, callbacks):   #A
    while not QUIT:
        packed = conn.blpop(queues, 30)             #B
        if not packed:
            continue

        name, args = json.loads(packed[1])
        if name not in callbacks:
            log_error("Unknown callback %s"%name)
            continue
        callbacks[name](*args)
#A The first changed line to add priority support
#B The second changed line to add priority support
#END
```

在这里使用多个队列，输入一个队列列表，将优先级高的列表放在前面，这样会先`pop`优先级高的队列。
这样在输入队列的时候就涉及到一个**重排**，这实际上涉及到了一个调度算法。

## 6.5 消息拉取
传递消息的两种方式：
- 消息推送
使用内置接口`PUBLISH`和`SUBSCRIBE`，由发送者来确保所有接受者已经成功接收到了消息。
如果客户端在执行订阅操作的过程中断线，那么客户端将丢失在断线期间发送的所有消息
- 消息拉取
接受者自己去获取`mailbox`里面的消息。

### 6.5.1 单接收者消息的发送与订阅替代品
例子：移动通信应用程序

为每个接收端维护一个收件箱`mailbox`——用数据结构`list`来实现。发送端可以往`mailbox`中写数据，并且查看`mailbox`看是否已经被接收端取走了。
![lFaRCd.png](https://s2.ax1x.com/2019/12/25/lFaRCd.png)


### 6.5.2 多接收者消息的发送与订阅替代品
数据结构如下所示：
![lFdKaD.png](https://s2.ax1x.com/2019/12/25/lFdKaD.png)

`jason22`和`jeff24`都参加了`chat:827`群组，其中用户`jason22`看了`6`条群组消息中的`5`条。

1. 创建群组聊天会话
`sender`是创建者，拉了几个`recipients`创建了群聊，初始化表示群组聊天数据的`chat:***`和每个用户的`seen:xxx`数据结构。
```python
def create_chat(conn, sender, recipients, message, chat_id=None):
    chat_id = chat_id or str(conn.incr('ids:chat:'))      #A

    recipients.append(sender)                             #E
    recipientsd = dict((r, 0) for r in recipients)        #E

    pipeline = conn.pipeline(True)
    pipeline.zadd('chat:' + chat_id, recipientsd)         #B
    for rec in recipients:                                #C
        pipeline.zadd('seen:' + rec, {chat_id: 0})        #C
    pipeline.execute()

    return send_message(conn, chat_id, sender, message)   #D
#A Get a new chat id
#E Set up a dictionary of users to scores to add to the chat ZSET
#B Create the set with the list of people participating
#C Initialize the seen zsets
#D Send the message
#END
```

2. 发送消息
```python
# chat_id ：往哪个群发消息
# sender: 谁发消息
# message：发什么消息
def send_message(conn, chat_id, sender, message):
    identifier = acquire_lock(conn, 'chat:' + chat_id)
    if not identifier:
        raise Exception("Couldn't get the lock")
    try:
        mid = conn.incr('ids:' + chat_id)                #A 改群聊的最大消息ID自增1
        ts = time.time()                                 #A
        packed = json.dumps({                            #A
            'id': mid,                                   #A
            'ts': ts,                                    #A
            'sender': sender,                            #A
            'message': message,                          #A
        })                                               #A

        conn.zadd('msgs:' + chat_id, {packed: mid})      #B 
    finally:
        release_lock(conn, 'chat:' + chat_id, identifier)
    return chat_id
#A Prepare the message
#B Send the message to the chat
#END
```
用到的命令：
```
ZADD key score member [[score member] [score member] …]
将一个或多个 member 元素及其 score 值加入到有序集 key 当中
```

创建消息，将想要发送的消息添加到群组集合`chat:***`中，将`message`的信息存入该群组的聊天记录中`msgs:****`。
一般来说，**当程序使用一个来自redis的值去构建另一个将要被添加到redis里面的值时，就需要使用锁或者是事务来消除竞争条件**。

3. 获取消息
```python
# recipient：需要读消息的用户ID
def fetch_pending_messages(conn, recipient):
    seen = conn.zrange('seen:' + recipient, 0, -1, withscores=True) #A

    pipeline = conn.pipeline(True)

    for chat_id, seen_id in seen:                               #B
        pipeline.zrangebyscore(                                 #B
            b'msgs:' + chat_id, seen_id+1, 'inf')                #B
    chat_info = list(zip(seen, pipeline.execute()))                   #C

    for i, ((chat_id, seen_id), messages) in enumerate(chat_info):
        if not messages:
            continue
        messages[:] = list(map(json.loads, messages))
        seen_id = messages[-1]['id']                            #D
        conn.zadd(b'chat:' + chat_id, {recipient: seen_id})      #D

        min_id = conn.zrange(                                   #E
            b'chat:' + chat_id, 0, 0, withscores=True)           #E

        pipeline.zadd('seen:' + recipient, {chat_id: seen_id})  #F
        if min_id:
            pipeline.zremrangebyscore(                          #G
                b'msgs:' + chat_id, 0, min_id[0][1])             #G
        chat_info[i] = (chat_id, messages)
    pipeline.execute()

    return chat_info
#A Get the last message ids received
#B Fetch all new messages
#C Prepare information about the data to be returned
#D Update the 'chat' ZSET with the most recently received message
#E Discover messages that have been seen by all users
#F Update the 'seen' ZSET
#G Clean out messages that have been seen by all users
#END
```

相关命令说明如下：
```
ZRANGE key start stop [WITHSCORES]
返回有序集 key 中，指定区间内的成员。

ZRANGEBYSCORE key min max [WITHSCORES] [LIMIT offset count]
返回有序集 key 中，所有 score 值介于 min 和 max 之间(包括等于 min 或 max )的成员。有序集成员按 score 值递增(从小到大)次序排列。
```

4. 加入群组和离开群组
```python
def join_chat(conn, chat_id, user):
    message_id = int(conn.get('ids:' + chat_id))                #A

    pipeline = conn.pipeline(True)
    pipeline.zadd('chat:' + chat_id, {user: message_id})          #B
    pipeline.zadd('seen:' + user, {chat_id: message_id})          #C
    pipeline.execute()
#A Get the most recent message id for the chat
#B Add the user to the chat member list
#C Add the chat to the users's seen list
#END

def leave_chat(conn, chat_id, user):
    pipeline = conn.pipeline(True)
    pipeline.zrem('chat:' + chat_id, user)                      #A
    pipeline.zrem('seen:' + user, chat_id)                      #A
    pipeline.zcard('chat:' + chat_id)                           #B

    if not pipeline.execute()[-1]:
        pipeline.delete('msgs:' + chat_id)                      #C
        pipeline.delete('ids:' + chat_id)                       #C
        pipeline.execute()
    else:
        oldest = conn.zrange(                                   #D
            'chat:' + chat_id, 0, 0, withscores=True)           #D
        conn.zremrangebyscore('msgs:' + chat_id, 0, oldest[0][1])     #E
#A Remove the user from the chat
#B Find the number of remaining group members
#C Delete the chat
#D Find the oldest message seen by all users
#E Delete old messages from the chat
#END
```
