# 量子增强的安全离线存储方案

本项目实现了一个基于量子加密技术的安全离线数据存储系统，提供高强度的数据保护和管理功能。

## 特性

- **量子增强加密**：利用量子随机数生成技术，提供更高强度的加密保护
- **安全离线存储**：数据本地存储，无需网络连接，避免网络攻击风险
- **完整性验证**：使用HMAC确保数据完整性，防止篡改
- **元数据管理**：支持为存储的数据添加自定义元数据
- **安全删除**：提供安全删除功能，多次覆盖文件内容确保数据不可恢复
- **备份与恢复**：支持数据的备份和恢复功能

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 初始化存储系统

```bash
python main.py init [--dir 存储目录] [--key-file 密钥文件路径]
```

### 存储数据

```bash
# 存储文件
python main.py store --file 文件路径 --key-file 密钥文件路径 [--meta 元数据]

# 存储文本
python main.py store --text "要存储的文本" --key-file 密钥文件路径 [--meta 元数据]
```

元数据格式为 `key1=value1,key2=value2`

### 检索数据

```bash
# 输出到标准输出
python main.py retrieve 数据ID --key-file 密钥文件路径

# 输出到文件
python main.py retrieve 数据ID --output 输出文件路径 --key-file 密钥文件路径
```

### 列出所有数据

```bash
python main.py list --key-file 密钥文件路径
```

### 删除数据

```bash
# 安全删除（默认）
python main.py