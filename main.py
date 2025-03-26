#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子增强的安全离线存储方案 - 主程序

提供命令行界面，用于管理安全存储系统。
"""

import os
import sys
import argparse
import getpass
import base64
from src.storage import SecureStorage
from src.utils import logger, generate_quantum_random_bytes


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="量子增强的安全离线存储系统")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 初始化命令
    init_parser = subparsers.add_parser("init", help="初始化存储系统")
    init_parser.add_argument("--dir", help="存储目录路径，默认为./data")
    init_parser.add_argument("--key-file", help="密钥文件路径，如果不存在则创建新密钥")
    
    # 存储命令
    store_parser = subparsers.add_parser("store", help="存储数据")
    store_parser.add_argument("--file", help="要存储的文件路径")
    store_parser.add_argument("--text", help="要存储的文本内容")
    store_parser.add_argument("--meta", help="元数据，格式为key1=value1,key2=value2")
    store_parser.add_argument("--key-file", required=True, help="密钥文件路径")
    
    # 检索命令
    retrieve_parser = subparsers.add_parser("retrieve", help="检索数据")
    retrieve_parser.add_argument("id", help="数据ID")
    retrieve_parser.add_argument("--output", help="输出文件路径，不指定则输出到标准输出")
    retrieve_parser.add_argument("--key-file", required=True, help="密钥文件路径")
    
    # 列表命令
    list_parser = subparsers.add_parser("list", help="列出所有存储的数据")
    list_parser.add_argument("--key-file", required=True, help="密钥文件路径")
    
    # 删除命令
    delete_parser = subparsers.add_parser("delete", help="删除数据")
    delete_parser.add_argument("id", help="数据ID")
    delete_parser.add_argument("--secure", action="store_true", help="安全删除，默认为True")
    delete_parser.add_argument("--key-file", required=True, help="密钥文件路径")
    
    # 备份命令
    backup_parser = subparsers.add_parser("backup", help="备份所有数据")
    backup_parser.add_argument("dir", help="备份目录路径")
    backup_parser.add_argument("--key-file", required=True, help="密钥文件路径")
    
    # 恢复命令
    restore_parser = subparsers.add_parser("restore", help="从备份恢复数据")
    restore_parser.add_argument("dir", help="备份目录路径")
    restore_parser.add_argument("--key-file", required=True, help="密钥文件路径")
    
    return parser.parse_args()


def load_key(key_file):
    """从文件加载密钥"""
    try:
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return base64.b64decode(f.read())
        else:
            # 生成新密钥
            key = generate_quantum_random_bytes(32)
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(key_file)), exist_ok=True)
            # 保存密钥
            with open(key_file, 'wb') as f:
                f.write(base64.b64encode(key))
            logger.info(f"已生成新的量子随机密钥并保存到: {key_file}")
            return key
    except Exception as e:
        logger.error(f"加载密钥失败: {str(e)}")
        sys.exit(1)


def parse_metadata(meta_str):
    """解析元数据字符串"""
    if not meta_str:
        return {}
    
    result = {}
    pairs = meta_str.split(',')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            result[key.strip()] = value.strip()
    
    return result


def main():
    """主函数"""
    args = parse_args()
    
    if not args.command:
        print("请指定命令。使用 --help 查看帮助信息。")
        sys.exit(1)
    
    # 初始化命令
    if args.command == "init":
        storage_dir = args.dir
        key_file = args.key_file or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'key.bin')
        
        # 加载或生成密钥
        key = load_key(key_file)
        
        # 初始化存储系统
        storage = SecureStorage(storage_dir, key)
        print(f"存储系统已初始化，存储目录: {storage.storage_dir}")
        print(f"密钥已保存到: {key_file}")
        print("警告: 请妥善保管密钥文件，密钥丢失将导致数据无法恢复！")
    
    # 其他命令需要加载密钥
    elif args.command in ["store", "retrieve", "list", "delete", "backup", "restore"]:
        if not os.path.exists(args.key_file):
            print(f"错误: 密钥文件不存在: {args.key_file}")
            sys.exit(1)
        
        # 加载密钥
        key = load_key(args.key_file)
        
        # 初始化存储系统
        storage = SecureStorage(key=key)
        
        # 存储命令
        if args.command == "store":
            if args.file and os.path.exists(args.file):
                # 从文件读取数据
                with open(args.file, 'rb') as f:
                    data = f.read()
                metadata = parse_metadata(args.meta)
                metadata['filename'] = os.path.basename(args.file)
                data_id = storage.store(data, metadata)
                print(f"数据已安全存储，ID: {data_id}")
            elif args.text:
                # 存储文本数据
                metadata = parse_metadata(args.meta)
                data_id = storage.store(args.text, metadata)
                print(f"数据已安全存储，ID: {data_id}")
            else:
                print("错误: 请提供要存储的文件或文本内容")
                sys.exit(1)
        
        # 检索命令
        elif args.command == "retrieve":
            try:
                data, metadata = storage.retrieve(args.id)
                
                if args.output:
                    # 输出到文件
                    with open(args.output, 'wb') as f:
                        if isinstance(data, bytes):
                            f.write(data)
                        else:
                            f.write(str(data).encode('utf-8'))
                    print(f"数据已保存到: {args.output}")
                else:
                    # 输出到标准输出
                    if isinstance(data, bytes):
                        try:
                            print(data.decode('utf-8'))
                        except UnicodeDecodeError:
                            print("[二进制数据，无法显示]")
                    else:
                        print(data)
                
                # 显示元数据
                print("\n元数据:")
                for key, value in metadata.items():
                    if key not in ['id', 'created_at', 'updated_at']:
                        print(f"  {key}: {value}")
                print(f"  创建时间: {metadata.get('created_at')}")
                print(f"  更新时间: {metadata.get('updated_at')}")
            
            except FileNotFoundError:
                print(f"错误: 数据不存在，ID: {args.id}")
                sys.exit(1)
            except ValueError as e:
                print(f"错误: {str(e)}")
                sys.exit(1)
        
        # 列表命令
        elif args.command == "list":
            items = storage.list_all()
            if not items:
                print("存储为空，没有数据")
            else:
                print(f"共有 {len(items)} 项数据:")
                for item in items:
                    print(f"ID: {item['id']}")
                    if 'filename' in item:
                        print(f"  文件名: {item['filename']}")
                    if 'content_type' in item:
                        print(f"  内容类型: {item['content_type']}")
                    print(f"  创建时间: {item.get('created_at')}")
                    print(f"  更新时间: {item.get('updated_at')}")
                    print()
        
        # 删除命令
        elif args.command == "delete":
            if storage.delete(args.id, args.secure):
                print(f"数据已{'安全' if args.secure else ''}删除，ID: {args.id}")
            else:
                print(f"错误: 数据不存在，ID: {args.id}")
                sys.exit(1)
        
        # 备份命令
        elif args.command == "backup":
            count = storage.backup(args.dir)
            print(f"备份完成，共备份 {count} 项数据到: {args.dir}")
        
        # 恢复命令
        elif args.command == "restore":
            try:
                count = storage.restore(args.dir)
                print(f"恢复完成，共恢复 {count} 项数据")
            except ValueError as e:
                print(f"错误: {str(e)}")
                sys.exit(1)


if __name__ == "__main__":
    main()