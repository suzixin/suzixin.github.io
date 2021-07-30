---
title:  C++ Primer
layout: post
categories: C++
tags: C++ 编程语言
excerpt: C++ Primer
---
# c2
## 2.2 变量
初始化和赋值是完全不同的操作：
- 初始化：创建变量时赋予一个初始值
- 赋值：把对象的当前值擦除，而以一个新值来替代。

**列表初始化**：无论是初始化对象还是某些时候为对象赋新值，可以使用一组由花括号括起来的初始值。
如果使用列表初始化且初始值存在丢失信息的风险，则编译器将报错。
```cpp
long double ld = 3.14;
int a{ld}, b = {ld}; // error
int c(ld), d = ld; // correct
```
> `int a{ld}`和`int c(ld)`的区别是什么？

`int a{ld}`是一个列表初始化，而`int c(ld)`是一个拷贝初始化。

------- 

**默认初始化**：定义任何函数体外的内置类型变量被初始化为0；定义在函数体内部的内置类型变量将不被初始化。
要注意使用未初始化的变量引发的故障。

### 2.3.2 指针
**空指针**:
最好使用`nullptr`而不是`NULL`来初始化一个空指针。

## 2.4 const限定符
`const`一般是在本文件内有效，如果要在多个文件之间共享`const`，需要在定义的时候加`extern`，然后在其他需要使用到该变量的地方也使用`extern const`来声明。
`const`对象在创建的时候必须初始化。

### 2.4.4 constexp
将变量定义成`constexp`以便编译器来验证表达式是否是常量表达式,如果验证发现非常量表达式，就会编译报错。
```cpp
int a = 0;
const int b = a; // correct
constexpr int c = a; // error,because expr(a) is not const expr.
```

限制：
- 使用字面值类型。
自定义类型就不是字面值类型，只有字面值类型编译器才能够做表达式的类型推导。


## 2.5 处理类型
### 2.5.1 类型别名
```cpp
// 类型别名
typedef double wages;
using SI = Sales_item;

// 指针、常量别名
typedef char *pstring; // pstring 是 char* 的别名
const pstring cts = 0; // 定义指向char的常量指针
const char *cts = 0; // 定义`const char`类型的指针
```

### 2.5.2 auto
自动类型`auto`，让编译器来根据上下文推断出这个类型具体指的是什么。
类似的概念还有`auto_ptr`智能指针。

### 2.5.3 decltype类型指示符

**decltype和引用**
- 如果表达式的内容是解引用操作，则`decltype`得到的结果是引用类型。
引用类型在定义的时候必须初始化。
- 赋值是会产生引用的一类典型表达式，引用的类型就是左值的类型。
例如`i=x`的类型是`int&`。
- 如果`decltype`使用的是一个加了括号的变量， 则`decltype`得到的结果是引用类型。

> 习题2.38 `auto`和`decltype`的区别和联系？

- `auto`类型说明符用编译器计算变量的初始值来推断其类型
- `auto`会适当改变结果类型使其更符合初始化规则，例如`auto`一般会忽略顶层`const`，而`decltype`会保留顶层`const`。

## 2.6 自定义数据结构
### 2.6.1 定义Sales_data类型
**类内初始值**：创建对象时，类内初始值将用于初始化数据成员。


# c3 字符串、向量和数 组
## 3.2 标准库类型string
### 3.2.3 处理string对象中的字符
建议使用c++版本的c标准库头文件
| c++版本  | c版本     |
|--------|---------|
| cctype | ctype.h |
注意c++版本的头文件定义的名字从属于命名空间`std`，这样比较好管理。但是如果使用了c的头文件，则不然。

**使用范围for语句改变字符串中的字符**
使用引用类型。
```cpp
string s("Hello World");
for (auto &c : s)
    c = toupper(c)
```

**使用下标访问string中的元素**
注意下标的合法性，可以使用`string::size_type`来保证类型是无符号数，确保下标不会小于`0`。

## 3.3 标准库类型vector
### 3.3.1 定义和初始化vector
注意区分列表初始值和元素数量：
```cpp
vector<int> v1(10); // 10 elements, each val = 0
vector<int> v2{10}; // 1 elements, val = 10
vector<string> v6{10}; // 10 elemens, val = ""
vector<string> v7{10, "hi"}; // 10 elements, val = "hi"
```
遇到`{}`的时候会查看里面的值是否能够用来初始化为`vector`的列表，如否，则将其处理为元素数量。如上例`vector<string> v6{10}`以及`vector<string> v7{10, "hi"}`所示。

### 3.3.2 向vector对象中添加元素
- `vector`对象能高效增长，所以没必要在创建的时候确定它的容量。
- 向`vector`中添加元素蕴含的编程假定
确保所写的循环正确无误，特别是在循环有可能改变`vector`容量的时候。

### 3.3.3 其他vector操作
- 拷贝替换
`v1 = {a,b,c};`，用列表中的元素的拷贝替换`v1`中的元素。
- 以字典顺序进行比较
只有当元素的值可以被比较的时候，`vector`对象才能以字典顺序进行比较。

## 3.4 迭代器
### 3.4.1 使用迭代器
一般来说我们不在意迭代器的具体类型，使用`auto`类型定义迭代器即可。
实际上还是可以定义迭代器准确的类型的：
| 类型     | 是否常量 | 举例                     |
|--------|------|------------------------|
| string | 是    | string::const_iterator |
| string | 否    | string::iterator       |

可以使用`cbegin`和`cend`函数来获得常量的迭代器。

**迭代器的操作**：
| 操作            | 含义                        |
|---------------|---------------------------|
| *iter         | 返回iter所指元素的引用             |
| iter->mem     | 解引用iter并获取该元素的名为`mem`的成员。 |
| （*it).empty() | 解引用it，然后调用结果对象的`empty`成员。 |
| it->empty()   | 解引用it，然后调用结果对象的`empty`成员。 |
总的来说这些操作和指针差不多。

某些对`vector`对象的操作会导致迭代器失效：
- 不能再for循环中向`vector`对象添加元素
因为这样可能导致死循环
- 更广泛的说，任何一种可能改变`vector`对象容量的操作，都会使得`vector`对象的迭代器失效。

**迭代器的算术运算：**
```cpp
// 得到最接近vi中间元素的一个迭代器
auto mid = vi.begin() + vi.size()/2

// 二分搜索的例子
bool bSearch(int sought) { 
    vector<int> text;
    auto beg = text.begin(), end = text.end();
    auto mid = text.begin() + (end - beg)/2;
    while (mid != end && *mid != sought) {
        if (sought < *mid)
            end = mid;
        else
            beg = mid + 1;
        mid = beg + (end - beg)/2;
    }
}
```

## 3.5 数组
### 3.5.1 定义和初始化数组
定义数组是的维度必须是常量表达式。
```cpp
int a = 10;
int b[a]; // err, a is not constexpr
```

不可以直接赋值拷贝数组，但是可直接拷贝`vector`。

### 6.3.3 返回数组指针
**使用类型别名：**
```cpp
typedef string arr[10];
// 声明一个函数，返回一个数组的引用，这个数组是包含10个string。
arr& func();
```

**声明一个返回数组指针的函数**：
```c
// 通用格式
Type (*function(parameter_list))[dimension]
// 声明一个函数func，返回类型是一个大小为10的整型数组的指针。
int (*func(int i))[10];
// 返回数组的引用该数组包含10个string对象
string (&func( ))[10];
```

**使用尾置返回类型**：
适合用于返回类型比较复杂的函数。
```cpp
// fcn takes an int argument and returns a pointer to an array of ten ints
auto func(int i) -> int(*)[10];
auto func() -> string(&)[10];
```

**使用decltype**
```cpp
int odd[] = {1,3,5,7,9};
int even[] = {0,2,4,6,8};
// returns a pointer to an array of five int elements
decltype(odd) *arrPtr(int i)
{
    return (i % 2) ? &odd : &even; // returns a pointer to the array
}
```

`decltype(odd)`的结果一个数组类型，还必须在函数声明时加一个`*`符号。

### 4.11.3 显式转换
> 实际上应该尽量避免强制类型转换。

**命名的强制类型转换**：
```cpp
cast-name<type>(expression);
```
`type`转换的目标类型，`expression`要转换的值。
`cast-name`可以是：
- static_cast
    - 把一个较大的算术类型赋值给较小的类型时常常使用，告知编译器不在乎潜在的精度损失
    - 用于编译器无法自动执行类型转换的场景
    ```cpp
    void &p = &d;
    double *dp = static_cast<double*>(p);
    ```
- dynamic_cast
支持运行时类型识别。
- const_cast
改变表达式的常量属性，不能做强制类型转换。
- reinterpret_cast
通常为运算对象的位模式提供较低层次上的重新解释。
- static_pointer_cast
- dynamic_pointer_cast

**旧式的强制类型转换**：
效果类似于`reinterpret_cast`
```
type (expr);
(type) expr;
```



## 6.7 函数指针

- **函数指针形参**
- 可以直接把函数作为实参使用，会自动转换为指针。
```cpp
// useBigger函数的声明
// third parameter is a function type and is automatically treated as a pointer to function
void useBigger(const string &s1, const string &s2, bool pf(const string &, const string &));
// equivalent declaration: explicitly define the parameter as a pointer to function
void useBigger(const string &s1, const string &s2, bool (*pf)(const string &, const string &));

// useBigger函数的调用
// compares lengths of two strings
bool lengthCompare(const string &, const string &);
// automatically converts the function lengthCompare to a pointer to function
useBigger(s1, s2, lengthCompare);
```
可以使用`typedef`和`decltype`来简化函数指针作为形参时的函数声明，关于`typedef`的理解可以查看[这篇文章](https://zhuanlan.zhihu.com/p/81221267)的总结：typedef中声明的类型在变量名的位置出现，在使用函数指针的情况下，用别名取代函数名的位置，并且用括号将这个别名括起来，并在前面加*号。
如下例子所示：
```cpp
bool lengthCompare(const string &, const string &);
// Func and Func2 have function type
typedef bool Func(const string&, const string&);
typedef decltype(lengthCompare) Func2; // equivalent type
// FuncP and FuncP2 have pointer to function type
typedef bool(*FuncP)(const string&, const string&);
typedef decltype(lengthCompare) *FuncP2; // equivalent type
// equivalent declarations of useBigger using type aliases
void useBigger(const string&, const string&, Func);
void useBigger(const string&, const string&, FuncP2);
```

- **返回指向函数的指针**
可以使用类型别名。
```cpp
using F = int(int*, int); // F is a function type, not a pointer
using PF = int(*)(int*, int); // PF is a pointer type
PF f1(int); // ok: PF is a pointer to function; f1 returns a pointer to function
F f1(int); // error: F is a function type; f1 can't return a function
F *f1(int); // ok: explicitly specify that the return type is a pointer to function
auto f1(int) -> int (*)(int*, int); // 使用尾置返回类型来声明一个函数
```

# 7. 类
类的基本思想是**数据抽象**和**封装**。
数据抽象是一种依赖于接口和实现分离的编程技术。
## 7.1 定义抽象数据类型
### 7.1.2 定义改进的Sales_data类
> 定义在类内部的函数是隐式的`inline`函数

**定义成员函数**：可以定义在类内，也可以定义在类外
**引入this**：在调用成员函数时，实际上是在替某个对象调用它。`this`是指向一个实例的指针。
```cpp
// 一般调用形式
total.isbn();
// 伪代码，用于说明调用成员函数的实际执行过程
Sales_data::isbn(&total)
// 显式使用this
std::string isbn() const { return this->bookNo;}
// 隐式使用this
std::string isbn() const { return bookNo;}
```
**引入const成员函数**：函数声明后的`const`表示类的成员不会被该函数改变。
```cpp
std::string isbn() const { return bookNo;}
// 隐式等效
std::string Sales_data::isbn(const Sales_data *const this)
{ return this->isbn; }
```

### 7.1.4 构造函数
> 其他相关知识：
- 7.5
- 13
- 15.7
- 18.1.3

编译器创建的构造函数又被称为**合成的默认构造函数**。
按照如下规则初始化类的数据成员：
- 如果存在类内的初始值，用它来初始化成员
- 否则，默认初始化该成员

> 我的小问题： 为什么要写构造函数？

- 在块中的内置类型和复合类型的对象被默认初始化，那么这些值是未定义的。我们不想看到这种行为。
- 有些比较复杂的情况下，默认的构造函数无法自动合成，例如类中包含一个其他类类型的成员。

------

构造函数中相关语法:
- `= default`
要求编译器生成默认构造函数
- 构造函数初始值列表


## 7.5 构造函数再探
### 7.5.1 构造函数初始值列表
成员初始化：若成员是const、引用、无默认构造函数的类，必须通过初始值列表将其初始化。
初始化顺序：与类中定义的顺序一致，不受初始值列表中顺序影响。

### 7.5.5 聚合类
聚合类：所有成员public、未定义构造函数、无类内初始值、无基类或virtual函数；使用花括号初始化，花括号内的初始值顺序与声明顺序一致。

### 7.5.6 字面值常量类

### 7.2.1 友元
类可以允许其他类或者函数访问他的非公有成员，方法是令其他类或者函数成为它的友元。

## 7.6 类的静态成员
类的成员和类本身直接相关，而不是与类的各个对象保持关联

- 静态成员的声明
- 静态成员的使用
- 静态成员的定义
静态数据成员不属于类的任何一个对象，并不是在创建类的对象时被定义的。
必须在类的外部定义和初始化每个静态成员。
```cpp
double Account::interestRate = initRate();
```

- 静态常量成员的类内初始化
```cpp
class Account {
private:
    // 初始值必须是常量表达式
    static constexpr int period = 30;
}
// 无初始值的静态成员的定义
constexpr int Account::period;
```

- 静态成员能用于某些场景，而普通成员不行
    - 静态成员可以是不完全类型
    - 可以使用静态成员作为默认实参

> 静态成员的优点：

- 作用域位于类的范围之内，避免与其他类的成员或者全局作用域的名字冲突
- 可以是私有成员

# 9. 顺序容器
## 9.1 概述
![1TsQ2Q.png](https://s2.ax1x.com/2020/02/11/1TsQ2Q.png)

确定使用哪种顺序容器的原则：
- 尽量使用`vector`
- 根据以下原则选择
    - 是否要求随机访问元素
    - 在容器中插入或删除元素的位置
        - 中间
        - 头尾
## 9.2 容器库概览
![1TyYyd.png](https://s2.ax1x.com/2020/02/11/1TyYyd.png)
![1Tyawt.png](https://s2.ax1x.com/2020/02/11/1Tyawt.png)


### 10.2.3 重排容器元素的算法
- `sort`
- `unique`

使用示例：https://en.cppreference.com/w/cpp/algorithm/unique
```cpp
    // remove duplicate elements
    std::vector<int> v{1,2,3,1,2,3,3,4,5,4,5,6,7};
    std::sort(v.begin(), v.end()); // 1 1 2 2 3 3 3 4 4 5 5 6 7 
    auto last = std::unique(v.begin(), v.end());
    // v now holds {1 2 3 4 5 6 7 x x x x x x}, where 'x' is indeterminate
    v.erase(last, v.end()); 
    for (int i : v)
      std::cout << i << " ";
    std::cout << "\n";
```
`unique`可以将一个顺序容器内的值进行重排，返回重排后非重复元素和重复元素的分界点。

## 10.1 概述
`find`方法可以返回在范围`[first,last)`中是否包含一个特定值，如果包含，返回它的迭代器，否则返回范围的右边界，注意这个范围是左包右不包。

例如：
```cpp
int val = 42;
auto result = find(vec.cbegin(), vec.cend(), val);
cout << "The value " << val
     << (result = vec.cend())
        ? " is not present" : " is present") << endl;
```

指针是内置数字的迭代器。
```cpp
int ia[] = {1, 2, 3};
int val = 3;
int *result = find(begin(ia), end(ia), val);
```
迭代器令算法不依赖于容器，但算法依赖于元素类型的操作。
**关键的一点：**泛型算法不会直接调用容器的操作，而是通过迭代器来访问、修改、移动元素。，这个特性带来了一个假定：算法永远不会改变底层容器的大小。(`10.4.1`中介绍的特殊迭代器——插入器除外。)

## 10.3 定制操作
### 10.3.1 向算法传递函数
为了使字符串除了默认的按字典序排序之外，我们还可以向`sort`函数的第三个参数传递函数指针，这个参数我们把它称为**谓词**(`predicate`)，我们可以使用它来自定义排序的规则。
谓词可以分成一元的和二元的，取决于该谓词接收的对象。`sort`函数接收一个二元谓词。
另外，我们还可以使用`stable_sort`，这个排序算法将范围中的元素`[first,last)`按(和`sort`一样)升序排序，但`stable_sort`保留具有相等值的元素的相对顺序。

```cpp
    bool compareInterval(string &i1, string &i2) 
    {
        return i1.size() > i2.size();
    } 
    sort(wordDict.begin(), wordDict.end());
    stable_sort(wordDict.begin(), wordDict.end(), compareInterval);
```

### 10.3.2 lambda表达式	
我们可以使用`find_if`来查找第一个具有特定特征的元素，这个特征使用一元谓词来描述。
```cpp
template <class InputIterator, class UnaryPredicate>
   InputIterator find_if (InputIterator first, InputIterator last, UnaryPredicate pred);
```

一元谓词的另一个例子：使用`partition`来将根据谓词的`true`/`false`将范围内的迭代器分成两组，返回第二组的第一个元素。使用`stable_partition`可以在划分后的序列中维持原有元素的顺序。
 
```cpp
// 打印`vector`中长度大于等于5的元素
bool longStr(const std::string &s) {
  return s.size() >= 5;
}

int main() {
  std::vector<std::string> words;
  for (std::string s; std::cin >> s; words.push_back(s)) {}
  auto long_bg = std::partition(words.begin(), words.end(), longStr);
  for (auto it = words.begin(); it != long_bg; ++it)
    std::cout << *it << " ";
  std::cout << std::endl;

  return 0;
}
```

`lambda`表达式是一种可调用的对象，
```
[capture list] (parameter list) -> return type { function body }
```
`capture list`:函数中定义的局部变量的列表，其它和普通函数一样。捕获列表只用于局部非`static`变量，`lambda`可以直接使用局部`static`变量和在它所在函数之外声明的名字。
`return type`：`lambda`表达式必须使用**尾置返回**来指定返回类型。
`parameter list`和`return type`是可选的，必须包含`capture list`和`function body`。
```cpp
auto f = [] {return 42; };
```
向`lambda`传递参数和向普通函数传递参数没有区别。

```cpp
// compute the number of elements with size >= sz
auto count = words.end() - wc;
cout << count << " " << make_plural(count, "word", "s")
<< " of length " << sz << " or longer" << endl;
```
可以使用`make_plural`来决定输出`word`或者`words`

完成的函数：
```cpp
void biggies(vector<string> &words,vector<string>::size_type sz) {
    elimDups(words); // put words in alphabetical order and remove duplicates
    
    // sort words by size, but maintain alphabetical order for words of the same size
    stable_sort(words.begin(), words.end(),
    [](const string &a, const string &b)
    { return a.size() < b.size();});
    
    // get an iterator to the first element whose size() is >= sz
    auto wc = find_if(words.begin(), words.end(),
    [sz](const string &a)
    { return a.size() >= sz; });
    
    // compute the number of elements with size >= sz
    auto count = words.end() - wc;
    cout << count << " " << make_plural(count, "word", "s")
    << " of length " << sz << " or longer" << endl;
    
    // print words of the given size or longer, each one followed by a space
    for_each(wc, words.end(),
    [](const string &s){cout << s << " ";});
    cout << endl;
}
```

### 10.3.3 lambda捕获和返回	
捕获的方式和函数参数传递的方式类似， 我们可以通过值捕获、引用捕获和隐式捕获。
**值捕获**:
采用值捕获的前提是变量可以拷贝。
被捕获的变量时在`lambda`创建时拷贝，而不是调用时拷贝。
由于被捕获的值是在`lambda`创建时拷贝，因此随后对其修改不会影响到 `lambda`对应的值。如下所示：
```cpp
void fcn1()
{
    size_t v1 = 42; // local variable
    // copies v1 into the callable object named f
    auto f = [v1] { return v1; };
    v1 = 0;
    auto j = f(); // j is 42; f stored a copy of v1 when we created it
}
```

**引用捕获**：
如果采用引用方式捕获一个变量，就必须确保被引用的对象在`lambda`执行的时候是存在的。
如果可能的话，尽量避免捕获指针或引用，因为这容易出问题，在创建`lambda`表达式到执行的这段时间，这些被捕获的对象可能发生非预期的变化。

**隐式捕获**：
在捕获列表写一个`&`或`=`告诉便以其采用捕获引用方式或值捕获方式来推断捕获列表。

**混合捕获**：
捕获列表的第一个元素应该是`&`或`=`，显示捕获的变量必须使用与隐式捕获不同的方式。

![31QK6f.png](https://s2.ax1x.com/2020/02/23/31QK6f.png)

**可变lambda**：
如果希望改变一个被捕获的变量的值，在参数列表首加上关键字`mutable`。

**指定lambda返回类型**：
```cpp
// correct
transform(vi.begin(), vi.end(), vi.begin(),
         [](int i) { return i < 0 ? -i : i; });

// error: cannot deduce the return type for the lambda
transform(vi.begin(), vi.end(), vi.begin(),
         [](int i) { if (i < 0) return -i; else return i;
});

// correct
transform(vi.begin(), vi.end(), vi.begin(),
         [](int i) -> int
         { if (i < 0) return -i; else return i; });
```


### 10.3.4 参数绑定	

# 11 关联容器
![33f9qP.png](https://s2.ax1x.com/2020/02/24/33f9qP.png)

分类的纬度：
- `set`/`map`
- 允许重复/不允许重复
允许重复:加上`multi`前缀
- 有序/无序
无序：加上`unordered_`前缀
## 11.1 使用关联容器	
`pair`只是用来存储两个混合的对象，当每次从`map`中提取一个元素时，会得到一个`pair`类型的对象。 `map`所使用的`pair`用`first`来保存关键字，用`second`保存对应的值。

练习`11.2`：分别给出最合适使用`list`、`vector`、`deque`、`map`以及`set`的例子。

[![33IR1g.md.png](https://s2.ax1x.com/2020/02/24/33IR1g.md.png)](https://imgchr.com/i/33IR1g)

## 11.2 关联容器概述

#### 11.2.1 定义关联容器
##### map
**自定义`map`的默认值**
> 参考：https://blog.csdn.net/dreamiond/article/details/84101516

在使用`map`的[]操作符对其进行访问时，如果`map`中尚没有查询的`key`值，则将创建一个新的键值对。其`key`值为查询的值，value值分为以下两种情况：
- value为内置类型时，其值将被初始化为0
- value为自定义数据结构时，如果定义了默认值则初始化为默认值，否则初始化为0

也可以使用第二种方法自定义`map`的value默认值
例如：
`map`的`value`为`int`类型，`key`值也为`value`类型，想要将`value`的默认值自定义为1，可以定义一个只包含一个默认`num`值的结构体，将其作为我们`map`的`value`值类型。

```cpp
struct IntDefaultedToOne {
		int num = 1;
	};
map<int,IntDefaultToOne> mp;
cout<<map[0].num;                 //将输出1
```

--------

**查找一个`map`中的元素**：
- m.count(key)
`1` if the container contains an element whose key is equivalent to k, or `zero` otherwise.
- m.find(v)
return an `iterator` to the element, if an element with specified key is found, or map::end otherwise.


-----------

**插入一个`map`中的元素**：
- auto ret = m.insert({key, value});
返回一个`pair`，第一个元素是个`iterator`，第二个元素is set to `true` if a new element was inserted or `false` if an equivalent key already existed.

------------


### 11.2.2 关键字类型的要求
**有序容器的关键字类型**
有序容器的排序依赖于关键字提供的`<`运算，这个比较函数需要有严格弱序的要求。
> 在实际编程中，重要的是，如果一个类型定义了行为正常的`<`运算符，则它可以用做关键字类型。

> Exercise 11.10: Could we define a map from vector<int>::iterator to int? What about from list<int>::iterator to int? In each case, if not, why not?

这个问题考察关联容器对关键字类型的要求。
有序容器要去关键字类型必须支持比较操作`<`。
```cpp
map <vector<int>::iterator , int> m1; // correct，vector的迭代器支持比较操作。
map <list<int>::iterator , int> m2; // wrong，list的迭代器不支持比较操作。
```
-------

### 11.2.3 pair类型
`pair`类型定义在头文件`utility`中

**创造pair对象的函数**
```cpp
pair<string, int>
process(vector<string> &v)
{
    // process v
    if (!v.empty())
        return {v.back(), v.back().size()}; // list initialize
        return pair<string, int>(v.back(), v.back().size());
        return make_pair(v.back(), v.back().size());
    else
        return pair<string, int>(); // explicitly constructed return value
}
```

11.3 关联容器操作
11.3.1 关联容器迭代器
11.3.2 添加元素
11.3.3 删除元素
11.3.4 map的下标操作
11.3.5 访问元素
11.3.6 一个单词转换的map

## 11.4 无序容器

# 第12章 动态内存
## 12.1 动态内存与智能指针	
`shared_ptr`和`unique_ptr`主要的区别：
`shared_ptr`允许多个指针指向同一个对象，而`unique_ptr`则独占所指向的对象。
`weak_ptr`是一种弱引用，指向`shared_ptr`所管理的对象。

### 12.1.1 shared_ptr类
![8PgKfS.png](https://s2.ax1x.com/2020/03/10/8PgKfS.png)
- `make_share`函数
通常使用`make_share`来分配一个对象并初始化它。
通常用`auto`定义一个对象来保存`make_shared`的结果。
智能指针类能记录有多少个`shared_ptr`指向相同的对象，并能在恰当的时候自动释放对象。
当指向一个对象的最后一个`shared_ptr`被销毁时，`shared_ptr`类会自动销毁此对象。
所以保证`share_ptr`在无用之后就不再保留非常重要。

**使用了动态生存期的资源的类**
程序使用动态内存出于三种原因之一：
1. They don’t know how many objects they’ll need
2. They don’t know the precise type of the objects they need
3. They want to share data between several objects
使用动态内存的一个常见原因是允许多个对象共享相同的状态，某些类分配的资源具有与原对象相独立的生存期，类似于[这里](https://cppcodetips.wordpress.com/2013/12/23/uml-class-diagram-explained-with-c-samples/)描述`Aggregation`时所说的意思。

定义了一个`StrBlob`类，这个类的实例们共享一个`vector`。
- 构造函数
- 成员访问函数
- 拷贝、赋值和销毁

### 12.1.2 直接管理内存
### 12.1.3 shared_ptr和new结合使用

## 14.8 函数调用运算符
如果类重载了函数调用运算符，则我们可以像使用函数一样使用该类的对象。
函数对象常常作为泛型算法的实参。例如：
```cpp
for_each(vs.begin(), vs.end(), PrintString(cerr, '\n'));
sort(v.begin(), v.end(), Compare);
```

# 第16章 模板与泛型编程
模板是`c++`泛型编程的基础。
模板定义以`template`开始，后跟一个模板参数列表，这是一个以逗号分隔的一个或多个模板参数。

**实例化函数模板**：当调用一个函数模板时，编译器通常用函数实参来推断模板实参。
编译器用推断出的模板参数来为我们实例化一个特定版本的函数。

**模板类型参数**：类型参数前必须使用关键字`class`或`typename`

**非类型模板参数**：用来表示一个值而非一个类型。
```cpp
template<unsigned N, unsigned M>
int compare(const char (&p1)[N], const char (&p2)[M])
{
    return strcmp(p1, p2);
}
```
当通过`compare("hi", "mom")`调用的时候，编译器会实例化出如下版本：
```cpp
int compare(const char (&p1)[3], const char (&p2)[4])
```

## 16.1 定义模板
## 16.1.1 函数模板

## 19.6 union: 一种节省空间的类
`union`是一种特殊的类，一个`union`可以有多个数据成员，但是在任意时刻只有一个数据成员可以有值。
- 使用`union`
```cpp
// objects of type Token have a single member, which could be of any of the listed types
union Token {
// members are public by default
    char cval;
    int ival;
    double dval;
};
```

- 匿名`union`
```cpp
union { // anonymous union
    char cval;
    int ival;
    double dval;
}; // defines an unnamed object, whose members we can access directly
cval = 'c'; // assigns a new value to the unnamed, anonymous union object
ival = 42; // that object now holds the value 42
```
