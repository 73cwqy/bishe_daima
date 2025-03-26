#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基本使用示例

展示量子增强的安全离线存储系统的基本使用方法。
"""

import os
import sys
import base64
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage import SecureStorage
from src.utils import generate_quantum_random_bytes, logger


def main():
    """基本使用示例"""
    print("量子增强的安全离线存储系统 - 基本使用示例")
    print("-" * 50)
    
    # 创建存储目录
    storage_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'storage_demo')
    os.makedirs(storage_dir, exist_ok=True)
    
    # 生成密钥
    key = generate_quantum_random_bytes(32)
    print(f"生成的量子随机密钥: {base64.b64encode(key).decode('utf-8')}")
    
    # 初始化存储系统
    storage = SecureStorage(storage_dir, key)
    print(f"存储系统已初始化，存储目录: {storage.storage_dir}")
    
    # 存储文本数据
    text_data = "这是一段测试文本，将被安全地存储在离线存储系统中。"
    text_metadata = {"type": "text", "language": "zh-CN", "description": "测试文本数据"}
    text_id = storage.store(text_data, text_metadata)
    print(f"文本数据已存储，ID: {text_id}")
    
    # 存储二进制数据
    binary_data = os.urandom(1024)  # 生成1KB随机二进制数据
    binary_metadata = {"type": "binary", "size": len(binary_data), "description": "随机二进制数据"}
    binary_id = storage.store(binary_data, binary_metadata)
    print(f"二进制数据已存储，ID: {binary_id}")
    
    # 存储JSON数据
    json_data = {"name": "测试对象", "values": [1, 2, 3, 4, 5], "nested": {"key": "value"}}
    json_metadata = {"type": "json", "description": "测试JSON数据"}
    json_id = storage.store(json_data, json_metadata)
    print(f"JSON数据已存储，ID: {json_id}")
    
    # 列出所有存储的数据
    print("\n存储的所有数据:")
    for item in storage.list_all():
        print(f"ID: {item['id']}")
        print(f"  类型: {item.get('type', '未知')}")
        print(f"  描述: {item.get('description', '无')}")
        print(f"  创建时间: {item.get('created_at')}")
    
    # 检索数据
    print("\n检索文本数据:")
    retrieved_text, text_meta = storage.retrieve(text_id)
    print(f"检索到的文本: {retrieved_text}")
    print(f"元数据: {text_meta}")
    
    print("\n检索JSON数据:")
    retrieved_json, json_meta = storage.retrieve(json_id)
    print(f"检索到的JSON: {retrieved_json}")
    print(f"元数据: {json_meta}")
    
    # 更新数据
    print("\n更新文本数据:")
    updated_text = "这是更新后的文本内容。"
    updated_meta = {"description": "已更新的文本数据"}
    storage.update(text_id, updated_text, updated_meta)
    
    # 检索更新后的数据
    retrieved_updated_text, updated_text_meta = storage.retrieve(text_id)
    print(f"更新后的文本: {retrieved_updated_text}")
    print(f"更新后的元数据: {updated_text_meta}")
    
    # 安全删除数据
    print("\n安全删除二进制数据:")
    storage.delete(binary_id, secure=True)
    print(f"数据已安全删除，ID: {binary_id}")
    
    # 创建备份
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backup_demo')
    print(f"\n创建备份到: {backup_dir}")
    count = storage.backup(backup_dir)
    print(f"已备份 {count} 项数据")
    
    print("\n示例完成")


if __name__ == "__main__":
    main()