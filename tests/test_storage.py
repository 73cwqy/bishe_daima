#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存储模块测试

测试安全离线存储模块的功能。
"""

import os
import sys
import shutil
import unittest
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage import SecureStorage
from src.utils import generate_quantum_random_bytes


class TestSecureStorage(unittest.TestCase):
    """测试安全离线存储类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录作为测试存储目录
        self.temp_dir = tempfile.mkdtemp()
        # 生成测试密钥
        self.key = generate_quantum_random_bytes(32)
        # 初始化存储类
        self.storage = SecureStorage(self.temp_dir, self.key)
        # 准备测试数据
        self.test_text = "这是测试文本数据"
        self.test_binary = b"This is binary test data"
        self.test_json = {"name": "测试", "value": 123}
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_store_retrieve_text(self):
        """测试文本数据的存储和检索"""
        # 存储文本数据
        data_id = self.storage.store(self.test_text)
        # 检索数据
        retrieved_data, metadata = self.storage.retrieve(data_id)
        # 验证检索的数据与原始数据相同
        self.assertEqual(retrieved_data, self.test_text)
        # 验证元数据
        self.assertEqual(metadata['id'], data_id)
        self.assertIn('created_at', metadata)
        self.assertIn('updated_at', metadata)
    
    def test_store_retrieve_binary(self):
        """测试二进制数据的存储和检索"""
        # 存储二进制数据
        data_id = self.storage.store(self.test_binary)
        # 检索数据
        retrieved_data, metadata = self.storage.retrieve(data_id)
        # 验证检索的数据与原始数据相同
        self.assertEqual(retrieved_data, self.test_binary)
    
    def test_store_retrieve_json(self):
        """测试JSON数据的存储和检索"""
        # 存储JSON数据
        data_id = self.storage.store(self.test_json)
        # 检索数据
        retrieved_data, metadata = self.storage.retrieve(data_id)
        # 验证检索的数据与原始数据相同
        self.assertEqual(retrieved_data, self.test_json)
        # 验证元数据
        self.assertEqual(metadata['content_type'], 'application/json')
    
    def test_update(self):
        """测试数据更新"""
        # 存储原始数据
        data_id = self.storage.store(self.test_text)
        # 更新数据
        updated_text = "这是更新后的文本"
        updated_meta = {"description": "更新测试"}
        self.storage.update(data_id, updated_text, updated_meta)
        # 检索更新后的数据
        retrieved_data, metadata = self.storage.retrieve(data_id)
        # 验证数据和元数据已更新
        self.assertEqual(retrieved_data, updated_text)
        self.assertEqual(metadata.get('description'), "更新测试")
    
    def test_delete(self):
        """测试数据删除"""
        # 存储数据
        data_id = self.storage.store(self.test_text)
        # 删除数据
        self.assertTrue(self.storage.delete(data_id))
        # 验证数据已删除
        with self.assertRaises(FileNotFoundError):
            self.storage.retrieve(data_id)
    
    def test_list_all(self):
        """测试列出所有数据"""
        # 存储多个数据项
        id1 = self.storage.store(self.test_text, {"type": "text"})
        id2 = self.storage.store(self.test_binary, {"type": "binary"})
        id3 = self.storage.store(self.test_json, {"type": "json"})
        # 列出所有数据
        items = self.storage.list_all()
        # 验证数据项数量
        self.assertEqual(len(items), 3)
        # 验证数据项ID
        ids = [item['id'] for item in items]
        self.assertIn(id1, ids)
        self.assertIn(id2, ids)
        self.assertIn(id3, ids)


if __name__ == "__main__":
    unittest.main()