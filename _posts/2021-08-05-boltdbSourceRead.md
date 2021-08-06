---
title:  boltdb源码分析
layout: post
categories: 数据库内核
tags: 数据库内核 boltdb 源码阅读
excerpt: 
---
# 1. 官方介绍

Bolt is a relatively small code base (<3KLOC) for an embedded, serializable,
transactional key/value database so it can be a good starting point for people
interested in how databases work.

The best places to start are the main entry points into Bolt:

# 2. `Open()`-初始化数据库
Initializes the reference to the database. It's responsible for creating the database if it doesn't exist, obtaining an exclusive lock on the file, reading the meta pages, & memory-mapping the file.

流程如下：
```go
bolt.Open("my.db", 0600, nil) {
    // Set default options if no options are provided.
    // Open data file
    os.OpenFile(db.path, flag|os.O_CREATE, mode)
    // Lock db file
    flock(db, mode, !db.readOnly, options.Timeout)
    // Default values for test hooks
    db.ops.writeAt = db.file.WriteAt

    // Initialize the database if it doesn't exist.
    db.init()
        // Create two meta pages on a buffer.
        // Initialize the meta page.
        // Write an empty freelist at page 3. 
        // Write an empty leaf page at page 4.
        // Write the buffer to our data file.

    // Initialize page pool.
    db.pagePool = sync.Pool{
        New: func() interface{} {
            return make([]byte, db.pageSize)
        },
    }

    // Memory map the data file.
    db.mmap(options.InitialMmapSize) {
        // check size
        // Unmap existing data before continuing.
        // Memory-map the data file as a byte slice.
        mmap(db, size) {
            b, _ := syscall.Mmap(int(db.file.Fd()), 0, sz, syscall.PROT_READ, syscall.MAP_SHARED|db.MmapFlags)
            // Save the original byte slice and convert to a byte array pointer.
            db.dataref = b
            db.data = (*[maxMapSize]byte)(unsafe.Pointer(&b[0]))
            db.datasz = sz
        }
        // Save references to the meta pages.
        db.meta0 = db.page(0).meta()
        db.meta1 = db.page(1).meta()
        // Validate the meta pages.
        err0 := db.meta0.validate()
        err1 := db.meta1.validate()
        }
    }

    // Read in the freelist.
    db.freelist = newFreelist()
    db.freelist.read(db.page(db.meta().freelist)) {
        // Copy the list of page ids from the freelist.
        if count == 0 {
            f.ids = nil
        }

        // Rebuild the page cache.
        f.reindex()
    }

    // Mark the database as opened and return.
    return db, nil
```

页面布局如下:
```
disk: [MP1|MP2|DP1|DP2|...|DPi-1|FP|DPi|DPi+1|...]
```

在这里使用了两个page来存储meta数据， 获取的逻辑如下：  
We have to return the meta with the highest txid which doesn't fail validation.

> 我的小问题： 两个meta page在写入的时候是如何处理的？

---------

相关数据结构：

```go
// 每一个page使用的数据结构
type page struct {
	id       pgid
	flags    uint16 /* 指定了page的类型 */
	count    uint16
	overflow uint32
	ptr      uintptr
}

// page的类型如下
const (
	branchPageFlag   = 0x01
	leafPageFlag     = 0x02
	metaPageFlag     = 0x04
	freelistPageFlag = 0x10
)

// meta的数据结构
type meta struct {
    magic    uint32
	version  uint32
	pageSize uint32
	flags    uint32
	root     bucket
	freelist pgid
	pgid     pgid
	txid     txid
	checksum uint64
}

// 页面中空闲链表的定义
type freelist struct {
	ids     []pgid          // all free and available free page ids.
	pending map[txid][]pgid // mapping of soon-to-be free page ids by tx.
	cache   map[pgid]bool   // fast lookup of all free and pending page ids.
}
```

# 3. `DB.Begin()`
Starts a read-only or read-write transaction depending on the value of the `writable` argument. This requires briefly obtaining the "meta" lock to keep track of open transactions. Only one read-write transaction can exist at a time so the "rwlock" is acquired during the life of a read-write transaction.

```go
func (db *DB) Begin(writable bool) (*Tx, error) {
	if writable {
        return db.beginRWTx() {
            // Obtain writer lock.
            db.rwlock.Lock()
            // obtain metalock to set up the transaction.
            db.metalock.Lock()

            // Create a transaction associated with the database.
            t := &Tx{writable: true}
            t.init(db) {
                // Copy the meta page since it can be changed by the writer.
                /* newBucket returns a new bucket associated with a transaction. */
                tx.root = newBucket(tx) {
                    var b = Bucket{tx: tx, FillPercent: DefaultFillPercent}
                    if tx.writable {
                        b.buckets = make(map[string]*Bucket)
                        b.nodes = make(map[pgid]*node)
                    }
                    return b
                }
                tx.root.bucket = &bucket{}
                *tx.root.bucket = tx.meta.root

                // Increment the transaction id and add a page cache for writable transactions.
                if tx.writable {
                    tx.pages = make(map[pgid]*page)
                    tx.meta.txid += txid(1)
                }
            }
            db.rwtx = t

            // Free any pages associated with closed read-only transactions.
            // 将已经关闭的transaction的页面进行回收
            var minid txid = 0xFFFFFFFFFFFFFFFF
            for _, t := range db.txs {
                if t.meta.txid < minid {
                    minid = t.meta.txid
                }
            }
            if minid > 0 {
                /* release moves all page ids for a transaction id (or older) to the freelist. */
                db.freelist.release(minid - 1) {
                    // 从`freelist.pending`中释放页面，然后加入到`freelist.ids`中
                }
            }


        }
	}
	return db.beginTx()
}
```

关键数据结构:
```go
// DB represents a collection of buckets persisted to a file on disk.
// All data access is performed through transactions which can be obtained through the DB.
// All the functions on DB will return a ErrDatabaseNotOpen if accessed before Open() is called.

type DB struct {
	rwtx     *Tx
	txs      []*Tx
}

// freelist represents a list of all pages that are available for allocation.
// It also tracks pages that have been freed but are still in use by open transactions.
type freelist struct {
	ids     []pgid          // all free and available free page ids.
	pending map[txid][]pgid // mapping of soon-to-be free page ids by tx.
	cache   map[pgid]bool   // fast lookup of all free and pending page ids.
}


type Tx struct {
	writable       bool
	managed        bool
	db             *DB
	meta           *meta
	root           Bucket
	pages          map[pgid]*page /* map from pgid to page pointer */
	stats          TxStats
	commitHandlers []func()

	WriteFlag int
}
```

数据结构`Tx`表示了事务的概念。

> 我的小问题： 数据库如何管理会话？

在这里没有会话的概念， 只有`transaction`。有`rwtx`和`txs`来记录当前db写、读的transaction。

# 4. Bucket
`Bucket`的数据结构如下：
```go
// Bucket represents a collection of key/value pairs inside the database.
type Bucket struct {
    *bucket
    tx       *Tx                // the associated transaction
    buckets  map[string]*Bucket // subbucket cache
    page     *page              // inline page reference
    rootNode *node              // materialized node for the root page.
    nodes    map[pgid]*node     // node cache

    FillPercent float64
}

// bucket represents the on-file representation of a bucket.
// This is stored as the "value" of a bucket key. If the bucket is small enough,
// then its root page can be stored inline in the "value", after the bucket
// header. In the case of inline buckets, the "root" will be 0.
type bucket struct {
	root     pgid   // page id of the bucket's root-level page
	sequence uint64 // monotonically incrementing, used by NextSequence()
}
```

## 4.1. CreateBucket
```go
tx.CreateBucket([]byte("MyBucket"))
    return tx.root.CreateBucket(name) {
        // Move cursor to correct position.
        c := b.Cursor()
        /* seek moves the cursor to a given key and returns it.
           If the key does not exist then the next key is used. */
        k, _, flags := c.seek(key) {
            // Start from root page/node and traverse to correct page.
            c.stack = c.stack[:0]
            c.search(seek, c.bucket.root) {
                /* pageNode returns the in-memory node, if it exists. */
                p, n := c.bucket.pageNode(pgid) {
                    // Finally lookup the page from the transaction if no node is materialized.
                    return b.tx.page(id), nil {
                        // Check the dirty pages first.
                        if p, ok := tx.pages[id]; ok {
                            return p
                        }
                        // Otherwise return directly from the mmap.
                        return tx.db.page(id)
                    }
                }
                e := elemRef{page: p, node: n}
                c.stack = append(c.stack, e)

                // If we're on a leaf page/node then find the specific node.
                if e.isLeaf() {
                    c.nsearch(key) {
                        // If we have a node then search its inodes.
                        // If we have a page then search its leaf elements.
                        inodes := p.leafPageElements()
                        // 在这些`inodes`中进行二分查找，找到`key`对应的`index`
                        index := sort.Search(int(p.count), func(i int) bool {
                            return bytes.Compare(inodes[i].key(), key) != -1
                        })
                        // 在栈顶元素中保存结果
                        e.index = index
                    }
                    return
                }
            }

            return c.keyValue() {
                ref := &c.stack[len(c.stack)-1]
                elem := ref.page.leafPageElement(uint16(ref.index))
            	return elem.key(), elem.value(), elem.flags
            }
        }

        // Create empty, inline bucket.
        var bucket = Bucket{
            bucket:      &bucket{},
            rootNode:    &node{isLeaf: true},
            FillPercent: DefaultFillPercent,
        }
        var value = bucket.write()

        // Insert into node.
        key = cloneBytes(key)
        c.node().put(key, key, value, 0, bucketLeafFlag) {
            // Find insertion index.
            index := sort.Search(len(n.inodes), func(i int) bool { return bytes.Compare(n.inodes[i].key, oldKey) != -1 })
            // Add capacity and shift nodes if we don't have an exact match and need to insert.
            // 需要添加节点
            exact := (len(n.inodes) > 0 && index < len(n.inodes) && bytes.Equal(n.inodes[index].key, oldKey))
            if !exact {
                // 在这里`n.inodes`就是当前`bucket`的集合
                n.inodes = append(n.inodes, inode{})
                copy(n.inodes[index+1:], n.inodes[index:])
            }
            // 使用传入的参数值设置这个`bucket`的索引信息
            inode := &n.inodes[index]
            inode.flags = flags
            inode.key = newKey
            inode.value = value
            inode.pgid = pgid
        }

        return b.Bucket(key), nil {
            /* Bucket retrieves a nested bucket by name. */

            // Move cursor to key.CreateBucket
            c := b.Cursor()
            k, v, flags := c.seek(name)
            // Otherwise create a bucket and cache it.
            var child = b.openBucket(v) {
                if b.tx.writable && !unaligned {
                    // create a bucket
                    child.bucket = &bucket{}
                    *child.bucket = *(*bucket)(unsafe.Pointer(&value[0]))
                }
            }
            if b.buckets != nil {
                // cache it
                b.buckets[string(name)] = child
            }
            return child
        }
    }
```

> 我的小问题： 在这里`b`是什么时候定义和初始化的？

`n.inodes`在`c.node().put(key, key, value, 0, bucketLeafFlag)`调用中类似一个bucket的集合  
类似`meta`信息的概念。

在这里对`createBucket`过程中的变量树进行一个简单的梳理：
```go
n.inodes /* c.node().put(key, key, value, 0, bucketLeafFlag) */
    c := b.Cursor() /* tx.root.CreateBucket(name) */
        b = tx.root
            tx.meta = &meta{} /* t.init(db) */
            db.meta().copy(tx.meta) /* t.init(db) */
                db.meta0 = db.page(0).meta()  /* db.mmap(options.InitialMmapSize)  */
            	db.meta1 = db.page(1).meta() /* db.mmap(options.InitialMmapSize) */
            tx.root = newBucket(tx) /* t.init(db) */
            tx.root.bucket = &bucket{} /* t.init(db) */
            *tx.root.bucket = tx.meta.root /* t.init(db) */
    k, _, flags := c.seek(key)
```

## 4.2. `Bucket.Put()` 
Writes a key/value pair into a bucket. After validating the arguments, a cursor is used to traverse the B+tree to the page and position where they key & value will be written. Once the position is found, the bucket materializes the underlying page and the page's parent pages into memory as "nodes". These nodes are where mutations occur during read-write transactions. These changes get flushed to disk during commit.

```go
func (b *Bucket) Put(key []byte, value []byte) error {
    // Move cursor to correct position.
	c := b.Cursor()
    k, _, flags := c.seek(key) {
        // 同createBucket
    }
    key = cloneBytes(key)
	c.node().put(key, key, value, 0, 0) {
        // 同createBucket
    }
} 

```

## 4.3. `Bucket.Get()`
Retrieves a key/value pair from a bucket. This uses a cursor to move to the page & position of a key/value pair. During a read-only transaction, the key and value data is returned as a direct reference to the underlying mmap file so there's no allocation overhead. For read-write transactions, this data may reference the mmap file or one of the in-memory node values.
```go
db.View(func(tx *bolt.Tx) error {
    /* Bucket retrieves a nested bucket by name. */
    /* Returns nil if the bucket does not exist. */
    /* The bucket instance is only valid for the lifetime of the transaction. */
    b := tx.Bucket([]byte("MyBucket")) {
        var child = b.openBucket(v)
        return child
    }
    v := b.Get([]byte("answer")) {
        k, v, flags := b.Cursor().seek(key)
        return v
    }
    fmt.Printf("The answer is: %s\n", v)
    return nil
})
```

# 5. `Cursor`

`Bucket`和`K-V`对的管理实际上都是通过`Cursor`来获取对应对象的， `Bucket`从`meta`中的获取也是通过`K-V`的方式。

This object is simply for traversing the B+tree of on-disk pages or in-memory nodes. It can seek to a specific key, move to the first or last value, or it can move forward or backward. The cursor handles the movement up and down the B+tree transparently to the end user.

接口如下所示：  


相关数据结构：
```go
// page
type page struct {
	id       pgid
	flags    uint16
	count    uint16
	overflow uint32
	ptr      uintptr
}

// node represents an in-memory, deserialized page.
type node struct {
	bucket     *Bucket
	isLeaf     bool
	unbalanced bool
	spilled    bool
	key        []byte
	pgid       pgid
	parent     *node
	children   nodes
	inodes     inodes
}


```

# 6. `Tx.Commit()`
Converts the in-memory dirty nodes and the list of free pages into pages to be written to disk. Writing to disk then occurs in two phases. 

First, the dirty pages are written to disk and an `fsync()` occurs. 

Second, a new meta page with an incremented transaction ID is written and another `fsync()` occurs. 

This two phase write ensures that partially written data pages are ignored in the event of a crash since the meta page pointing to them is never written. Partially written meta pages are invalidated because they are written with a checksum.

