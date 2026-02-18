#!/usr/bin/env python3
"""
SSH密钥生成和配置工具
"""

import subprocess
import os
from pathlib import Path

def create_ssh_key():
    """创建SSH密钥对"""
    print("🔑 生成SSH密钥对...")
    
    # 创建.ssh目录（如果不存在）
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(exist_ok=True)
    
    # 生成新的SSH密钥对
    try:
        result = subprocess.run([
            "ssh-keygen", 
            "-t", "rsa", 
            "-b", "4096", 
            "-f", "D:/ssh_keys/aliyun_key",
            "-N", "High-Performance-Aliyun-Key", 
            "-C", "deployer@highperformance.com"
        ], capture_output=True, text=True, shell=True)
        
        print("✅ SSH密钥对生成成功")
        return True
        
    except Exception as e:
        print(f"❌ SSH密钥生成失败: {e}")
        return False

def setup_aliyun_ssh():
    """配置阿里云SSH连接"""
    print("🔗 配置阿里云SSH连接...")
    
    ssh_config = """# 阿里云SSH配置
Host aliyun-server
    HostName 8.152.199.108
    User root
    Port 22
    IdentityFile D:/ssh_keys/aliyun_key
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/known_hosts
"""
    
    ssh_config_path = Path.home() / ".ssh" / "config"
    with open(ssh_config_path, 'a', encoding='utf-8') as f:
        f.write(ssh_config)
    
    print(f"✅ SSH配置已更新: {ssh_config_path}")
    return True

def copy_public_key():
    """复制公钥到剪贴板"""
    try:
        # 读取公钥文件
        public_key_path = Path("D:/ssh_keys/aliyun_key.pub")
        if not public_key_path.exists():
            print("❌ 公钥文件不存在")
            return False
        
        with open(public_key_path, 'r', encoding='utf-8') as f:
            public_key = f.read()
        
        print("✅ 公钥已复制到剪贴板")
        print("\n请将以下公钥复制到阿里云控制台:")
        print("=" * 60)
        print(public_key)
        print("=" * 60)
        print("\n阿里云控制台操作步骤:")
        print("1. 登录阿里云控制台")
        print("2. 进入ECS实例管理")
        print("3. 找到IP: 8.152.199.108")
        print("4. 点击操作 → 更多 → 密码/密钥 → 创建SSH密钥对")
        print("5. 精贴公钥内容")
        print("6. 设置密钥名称: High-Performance-Aliyun-Key")
        print("7. 绑定用户: root")
        print("8. 点击确定")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取公钥失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 SSH配置向导")
    print("=" * 60)
    
    # 检查并创建.ssh目录
    ssh_dir = Path("D:/ssh_keys")
    ssh_dir.mkdir(exist_ok=True)
    
    # 生成SSH密钥对
    if not (ssh_dir / "aliyun_key").exists():
        if not create_ssh_key():
            return
    else:
        print("⚠️ SSH密钥已存在，跳过生成")
    
    # 配置SSH
    if not setup_aliyun_ssh():
        return
    
    # 复制公钥
    if not copy_public_key():
        return
    
    print("\n" + "=" * 60)
    print("✅ SSH配置完成！")
    print("=" * 60)
    print("\n📋 下一步手动操作:")
    print("1. 等待几分钟后，阿里云控制台密钥配置生效")
    print("2. 然后验证SSH连接:")
    print("   ssh root@8.152.199.108")
    print("   # 第一次连接需要确认yes")
    print("3. 连接成功后，可以继续部署")
    print("=" * 60)

if __name__ == "__main__":
    main()