#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
安全离线存储模块

提供数据的安全存储、检索和管理功能，结合量子加密技术确保数据安全。
"""

import os
import json
import uuid
import shutil
from datetime import datetime
from src.encryption import QuantumEnhancedEncryption
from src.utils import generate_quantum_random_bytes, secure_delete_file, logger


class SecureStorage:
    """安全离线存储类，提供数据的加密存储和检索功能"""
    
    def __init__(self, storage_dir=None, key=None):
        """初始化存储类
        
        Args:
            storage_dir (str): 存储目录路径，默认为代码目录下的data目录
            key (bytes): 加密密钥，如果不提供则自动生成
        """
        # 设置存储目录
        if storage_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            storage_dir = os.path.join(base_dir, 'data')
        
        self.storage_dir = storage_dir
        self.meta_dir = os.path.join(storage_dir, 'meta')
        self.data_dir = os.path.join(storage_dir, 'data')
        
        # 创建必要的目录
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(self.meta_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 设置或生成加密密钥
        if key is None:
            # 生成32字节(256位)的量子随机密钥
            key = generate_quantum_random_bytes(32)
            logger.info("已生成新的量子随机密钥")
        
        self.key = key
        self.encryption = QuantumEnhancedEncryption(key)
        
        logger.info(f"安全存储初始化完成，存储目录: {self.storage_dir}")
    
    def store(self, data, metadata=None, data_id=None):
        """存储数据
        
        Args:
            data: 要存储的数据，可以是字符串、字节或其他可序列化对象
            metadata (dict): 与数据关联的元数据
            data_id (str): 数据ID，如果不提供则自动生成
            
        Returns:
            str: 数据ID，可用于后续检索
        """
        # 生成唯一ID
        if data_id is None:
            data_id = str(uuid.uuid4())
        
        # 准备元数据
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'id': data_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        })
        
        # 将数据转换为字节
        if isinstance(data, str):
            data = data.encode('utf-8')
        elif not isinstance(data, bytes):
            # 如果是其他类型，尝试JSON序列化
            try:
                data = json.dumps(data).encode('utf-8')
                metadata['content_type'] = 'application/json'
            except Exception as e:
                logger.error(f"数据序列化失败: {str(e)}")
                raise ValueError("无法序列化数据，请提供字符串、字节或可JSON序列化的对象")
        else:
            metadata['content_type'] = 'application/octet-stream'
        
        # 加密数据
        encrypted_data = self.encryption.encrypt(data)
        
        # 存储加密数据
        data_path = os.path.join(self.data_dir, f"{data_id}.bin")
        with open(data_path, 'wb') as f:
            f.write(encrypted_data)
        
        # 存储元数据
        meta_path = os.path.join(self.meta_dir, f"{data_id}.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已安全存储，ID: {data_id}，大小: {len(encrypted_data)}字节")
        return data_id
    
    def retrieve(self, data_id):
        """检索数据
        
        Args:
            data_id (str): 数据ID
            
        Returns:
            tuple: (数据, 元数据)
            
        Raises:
            FileNotFoundError: 如果数据不存在
            ValueError: 如果数据解密失败
        """
        # 检查数据是否存在
        data_path = os.path.join(self.data_dir, f"{data_id}.bin")
        meta_path = os.path.join(self.meta_dir, f"{data_id}.json")
        
        if not os.path.exists(data_path) or not os.path.exists(meta_path):
            logger.error(f"数据不存在，ID: {data_id}")
            raise FileNotFoundError(f"数据不存在，ID: {data_id}")
        
        # 读取元数据
        with open(meta_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 读取加密数据
        with open(data_path, 'rb') as f:
            encrypted_data = f.read()
        
        # 解密数据
        try:
            data = self.encryption.decrypt(encrypted_data)
            
            # 根据内容类型转换数据
            content_type = metadata.get('content_type')
            if content_type == 'application/json':
                data = json.loads(data.decode('utf-8'))
            
            logger.info(f"数据已成功检索，ID: {data_id}")
            return data, metadata
        except Exception as e:
            logger.error(f"数据解密失败，ID: {data_id}，错误: {str(e)}")
            raise ValueError(f"数据解密失败: {str(e)}")
    
    def update(self, data_id, data, metadata=None):
        """更新数据
        
        Args:
            data_id (str): 数据ID
            data: 新的数据
            metadata (dict): 新的元数据，如果提供则与现有元数据合并
            
        Returns:
            str: 数据ID
            
        Raises:
            FileNotFoundError: 如果数据不存在
        """
        # 检查数据是否存在
        meta_path = os.path.join(self.meta_dir, f"{data_id}.json")
        if not os.path.exists(meta_path):
            logger.error(f"数据不存在，无法更新，ID: {data_id}")
            raise FileNotFoundError(f"数据不存在，ID: {data_id}")
        
        # 读取现有元数据
        with open(meta_path, 'r', encoding='utf-8') as f:
            existing_metadata = json.load(f)
        
        # 更新元数据
        if metadata:
            existing_metadata.update(metadata)
        
        existing_metadata['updated_at'] = datetime.now().isoformat()
        
        # 存储新数据
        return self.store(data, existing_metadata, data_id)
    
    def delete(self, data_id, secure=True):
        """删除数据
        
        Args:
            data_id (str): 数据ID
            secure (bool): 是否安全删除，默认为True
            
        Returns:
            bool: 是否成功删除
        """
        # 检查数据是否存在
        data_path = os.path.join(self.data_dir, f"{data_id}.bin")
        meta_path = os.path.join(self.meta_dir, f"{data_id}.json")
        
        if not os.path.exists(data_path) and not os.path.exists(meta_path):
            logger.warning(f"数据不存在，无法删除，ID: {data_id}")
            return False
        
        # 删除数据文件
        if os.path.exists(data_path):
            if secure:
                secure_delete_file(data_path)
            else:
                os.remove(data_path)
        
        # 删除元数据文件
        if os.path.exists(meta_path):
            if secure:
                secure_delete_file(meta_path)
            else:
                os.remove(meta_path)
        
        logger.info(f"数据已{'安全' if secure else ''}删除，ID: {data_id}")
        return True
    
    def list_all(self):
        """列出所有存储的数据
        
        Returns:
            list: 元数据列表
        """
        result = []
        
        # 遍历元数据目录
        for filename in os.listdir(self.meta_dir):
            if filename.endswith('.json'):
                meta_path = os.path.join(self.meta_dir, filename)
                try:
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    result.append(metadata)
                except Exception as e:
                    logger.error(f"读取元数据失败，文件: {filename}，错误: {str(e)}")
        
        return result
    
    def backup(self, backup_dir):
        """备份所有数据
        
        Args:
            backup_dir (str): 备份目录路径
            
        Returns:
            int: 备份的数据项数量
        """
        # 创建备份目录
        os.makedirs(backup_dir, exist_ok=True)
        backup_meta_dir = os.path.join(backup_dir, 'meta')
        backup_data_dir = os.path.join(backup_dir, 'data')
        os.makedirs(backup_meta_dir, exist_ok=True)
        os.makedirs(backup_data_dir, exist_ok=True)
        
        # 复制所有文件
        count = 0
        for filename in os.listdir(self.meta_dir):
            if filename.endswith('.json'):
                data_id = filename[:-5]  # 移除.json后缀
                
                # 复制元数据
                src_meta = os.path.join(self.meta_dir, filename)
                dst_meta = os.path.join(backup_meta_dir, filename)
                shutil.copy2(src_meta, dst_meta)
                
                # 复制数据
                src_data = os.path.join(self.data_dir, f"{data_id}.bin")
                dst_data = os.path.join(backup_data_dir, f"{data_id}.bin")
                if os.path.exists(src_data):
                    shutil.copy2(src_data, dst_data)
                    count += 1
        
        logger.info(f"数据备份完成，备份目录: {backup_dir}，数据项数量: {count}")
        return count
    
    def restore(self, backup_dir):
        """从备份恢复数据
        
        Args:
            backup_dir (str): 备份目录路径
            
        Returns:
            int: 恢复的数据项数量
        """
        # 检查备份目录是否存在
        backup_meta_dir = os.path.join(backup_dir, 'meta')
        backup_data_dir = os.path.join(backup_dir, 'data')
        
        if not os.path.exists(backup_meta_dir) or not os.path.exists(backup_data_dir):
            logger.error(f"备份目录结构不正确: {backup_dir}")
            raise ValueError(f"备份目录结构不正确: {backup_dir}")
        
        # 复制所有文件
        count = 0
        for filename in os.listdir(backup_meta_dir):
            if filename.endswith('.json'):
                data_id = filename[:-5]  # 移除.json后缀
                
                # 复制元数据
                src_meta = os.path.join(backup_meta_dir, filename)
                dst_meta = os.path.join(self.meta_dir, filename)
                shutil.copy2(src_meta, dst_meta)
                
                # 复制数据
                src_data = os.path.join(backup_data_dir, f"{data_id}.bin")
                dst_data = os.path.join(self.data_dir, f"{data_id}.bin")
                if os.path.exists(src_data):
                    shutil.copy2(src_data, dst_data)
                    count += 1
        
        logger.info(f"数据恢复完成，备份目录: {backup_dir}，数据项数量: {count}")
        return count