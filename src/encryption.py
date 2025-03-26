#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子增强加密模块

本模块实现了基于量子原理的加密算法，结合经典加密方法提供高强度的数据保护。
"""

import os
import hashlib
import hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from src.utils import generate_quantum_random_bytes, logger


class QuantumEnhancedEncryption:
    """量子增强加密类，提供基于量子随机数的加密和解密功能"""
    
    def __init__(self, key, backend=None):
        """初始化加密类
        
        Args:
            key (bytes): 加密密钥
            backend: 加密后端，默认使用系统提供的后端
        """
        self.key = key
        self.backend = backend or default_backend()
        # 使用密钥的哈希作为实际加密密钥，确保长度合适
        self.encryption_key = hashlib.sha256(key).digest()
        logger.debug(f"初始化量子增强加密模块，密钥哈希: {self.encryption_key[:8].hex()}...")
    
    def _generate_iv(self):
        """生成初始化向量，使用量子随机数生成器"""
        # 使用量子随机数生成16字节的初始化向量
        return generate_quantum_random_bytes(16)
    
    def _pad_data(self, data):
        """对数据进行填充，使其长度符合加密算法的要求"""
        padder = padding.PKCS7(128).padder()
        return padder.update(data) + padder.finalize()
    
    def _unpad_data(self, padded_data):
        """移除数据的填充"""
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded_data) + unpadder.finalize()
    
    def _create_hmac(self, data):
        """创建HMAC用于验证数据完整性"""
        h = hmac.new(self.key, data, hashlib.sha256)
        return h.digest()
    
    def encrypt(self, data):
        """加密数据
        
        Args:
            data (bytes): 需要加密的数据
            
        Returns:
            bytes: 加密后的数据，格式为: IV + 加密数据 + HMAC
        """
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        
        # 生成初始化向量
        iv = self._generate_iv()
        logger.debug(f"生成初始化向量: {iv.hex()}")
        
        # 填充数据
        padded_data = self._pad_data(data)
        
        # 创建加密器
        encryptor = Cipher(
            algorithms.AES(self.encryption_key),
            modes.CBC(iv),
            backend=self.backend
        ).encryptor()
        
        # 加密数据
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # 组合IV和加密数据
        result = iv + encrypted_data
        
        # 添加HMAC用于验证
        mac = self._create_hmac(result)
        result += mac
        
        logger.debug(f"数据加密完成，原始大小: {len(data)}字节，加密后大小: {len(result)}字节")
        return result
    
    def decrypt(self, encrypted_data):
        """解密数据
        
        Args:
            encrypted_data (bytes): 加密的数据，格式为: IV + 加密数据 + HMAC
            
        Returns:
            bytes: 解密后的原始数据
            
        Raises:
            ValueError: 如果数据被篡改或密钥不正确
        """
        # 验证数据长度
        if len(encrypted_data) < 16 + 32:  # IV(16) + 最小加密块 + HMAC(32)
            raise ValueError("加密数据格式不正确或已损坏")
        
        # 提取HMAC
        mac_received = encrypted_data[-32:]
        data_to_verify = encrypted_data[:-32]
        
        # 验证HMAC
        mac_calculated = self._create_hmac(data_to_verify)
        if not hmac.compare_digest(mac_calculated, mac_received):
            raise ValueError("数据完整性验证失败，数据可能被篡改或密钥不正确")
        
        # 提取IV和加密数据
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:-32]
        
        # 创建解密器
        decryptor = Cipher(
            algorithms.AES(self.encryption_key),
            modes.CBC(iv),
            backend=self.backend
        ).decryptor()
        
        # 解密数据
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 移除填充
        try:
            data = self._unpad_data(padded_data)
            logger.debug(f"数据解密完成，解密后大小: {len(data)}字节")
            return data
        except Exception as e:
            logger.error(f"解密过程中出错: {str(e)}")
            raise ValueError("解密失败，可能是密钥不正确或数据已损坏") from e