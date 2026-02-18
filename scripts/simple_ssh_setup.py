#!/usr/bin/env python3
"""
SSH配置工具 - 避免编码问题
"""

import subprocess
import os
from pathlib import Path

def main():
    print("=== SSH配置工具 ===")
    
    # 创建密钥目录
    ssh_dir = Path("D:/ssh_keys")
    ssh_dir.mkdir(exist_ok=True)
    
    print("生成SSH密钥对...")
    
    # 生成新的SSH密钥对
    result = subprocess.run([
        "ssh-keygen",
        "-t", "rsa",
        "-b", "4096", 
        "-f", "D:/ssh_keys/aliyun_key",
        "-N", "High-Performance-Aliyun-Key",
        "-C", "deployer@highperformance.com",
        "-q"  # 静默模式
    ], capture_output=True, text=True, shell=True)
    
    if result.returncode == 0:
        print("SSH密钥生成成功")
        
        # 读取公钥
        public_key_path = "D:/ssh_keys/aliyun_key.pub"
        try:
            with open(public_key_path, 'r', encoding='utf-8') as f:
                public_key = f.read()
                
            print("\n" + "="*60)
            print("请复制以下公钥到阿里云控制台:")
            print("="*60)
            print(public_key)
            print("="*60)
            
        except Exception as e:
            print(f"读取公钥失败: {e}")
            
    else:
        print("SSH密钥生成失败")
    
    # 配置SSH
    ssh_config = f"""Host aliyun-server
    HostName 8.152.199.108
    User root
    Port 22
    IdentityFile D:/ssh_keys/aliyun_key
    StrictHostKeyChecking no"""
    
    ssh_config_path = Path.home() / ".ssh" / "config"
    with open(ssh_config_path, 'a', encoding='utf-8') as f:
        f.write(ssh_config)
    
    print("SSH配置已更新")
    
    print("\n=== 下一步 ===")
    print("1. 复制公钥到阿里云控制台")
    print("2. 登录: ECS实例管理 → 找到8.152.199.108")
    print("3. 操作: 更多 → 密码/密钥 → 创建SSH密钥对")
    print("4. 精贴公钥内容")
    print("5. 设置: 密钥名称=High-Performance-Aliyun-Key")
    print("6. 绑定: root")
    print("7. 验证SSH: ssh root@8.152.199.108")

if __name__ == "__main__":
    main()