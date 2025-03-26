#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具模块

提供量子随机数生成和日志记录等通用功能。
"""

import os
import logging
import numpy as np
from datetime import datetime

# 配置日志记录器
logger = logging.getLogger('quantum_storage')
logger.setLevel(logging.DEBUG)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建文件处理器
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'quantum_storage_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 添加处理器到日志记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)


def generate_quantum_random_bytes(num_bytes):
    """
    生成基于量子原理的随机字节
    
    在实际量子计算机上，这将使用量子随机数生成器。
    在模拟环境中，我们使用高质量的伪随机数生成器模拟量子随机性。
    
    Args:
        num_bytes (int): 需要生成的随机字节数
        
    Returns:
        bytes: 生成的随机字节
    """
    try:
        # 在这里，我们模拟量子随机数生成
        # 在实际应用中，这里应该调用量子随机数生成器API或硬件
        logger.debug(f"生成{num_bytes}字节的量子随机数")
        
        # 使用numpy的高质量随机数生成器模拟量子随机性
        # 在实际应用中，这应该替换为真正的量子随机数源
        random_array = np.random.bytes(num_bytes)
        
        # 在实际量子系统中，这里应该进行量子态叠加和测量的模拟
        # 为了模拟量子效应，我们可以添加一些额外的熵
        entropy_source = os.urandom(num_bytes // 2)
        
        # 将两种随机源结合，模拟量子纠缠效应
        result = bytearray(num_bytes)
        for i in range(num_bytes):
            if i < len(entropy_source):
                # 模拟量子纠缠，将两个随机源的比特进行XOR操作
                result[i] = random_array[i] ^ entropy_source[i]
            else:
                result[i] = random_array[i]
        
        return bytes(result)
    except Exception as e:
        logger.error(f"生成量子随机数时出错: {str(e)}")
        # 如果量子随机数生成失败，回退到操作系统的随机数生成器
        logger.warning("回退到操作系统随机数生成器")
        return os.urandom(num_bytes)


def secure_delete_file(file_path, passes=3):
    """
    安全删除文件，通过多次覆盖文件内容确保数据不可恢复
    
    Args:
        file_path (str): 要删除的文件路径
        passes (int): 覆盖次数，默认为3次
    """
    if not os.path.exists(file_path):
        logger.warning(f"文件不存在，无法安全删除: {file_path}")
        return
    
    try:
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        logger.debug(f"安全删除文件: {file_path}，大小: {file_size}字节，覆盖次数: {passes}")
        
        # 多次覆盖文件内容
        for i in range(passes):
            with open(file_path, 'wb') as f:
                # 第一次使用随机数据覆盖
                if i == 0:
                    f.write(generate_quantum_random_bytes(file_size))
                # 第二次使用全1覆盖
                elif i == 1:
                    f.write(b'\xFF' * file_size)
                # 第三次使用全0覆盖
                else:
                    f.write(b'\x00' * file_size)
            
            # 强制将数据写入磁盘
            os.fsync(f.fileno())
        
        # 最后删除文件
        os.remove(file_path)
        logger.info(f"文件已安全删除: {file_path}")
    except Exception as e:
        logger.error(f"安全删除文件时出错: {str(e)}")
        # 如果安全删除失败，尝试常规删除
        try:
            os.remove(file_path)
            logger.warning(f"回退到常规删除: {file_path}")
        except Exception as e2:
            logger.error(f"常规删除也失败: {str(e2)}")