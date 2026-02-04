# Windows文件名乱码解决方案

## 📌 问题分析
Windows与Mac/Linux系统在文件编码处理上存在差异，特别是对于包含中文的文件名。

## 🔧 解决方案

### 方案1: 重命名文件（推荐）
将中文文件名改为英文，这是最可靠的解决方案：

```bash
# 将 "使用说明.md" 重命名为 "usage.md"
mv "使用说明.md" "usage.md"
```

### 方案2: 修改Windows系统区域设置
1. 打开"控制面板" → "区域和语言"
2. 选择"管理"标签页
3. 点击"更改系统区域设置"
4. 勾选"Beta版：使用Unicode UTF-8提供全球语言支持"
5. 重启电脑

### 方案3: 使用Git配置（如果使用Git）
在Windows Git Bash中设置：
```bash
git config --global core.quotepath false
git config --global i18n.logoutputencoding utf8
```

### 方案4: 代码中的编码处理
如果程序需要处理中文字符，确保使用UTF-8编码：

```python
# 读取文件时指定编码
with open('文件名', 'r', encoding='utf-8') as f:
    content = f.read()

# 写入文件时指定编码
with open('文件名', 'w', encoding='utf-8') as f:
    f.write(content)
```

## 📝 当前项目建议
对于 `使用说明.md` 文件，建议：
1. **重命名为英文**：`README.md` 或 `usage.md`
2. **如果必须保留中文**：确保Windows系统启用UTF-8支持

## 🔄 重命名操作
```bash
# Linux/Mac 终端
mv "使用说明.md" "README.md"

# Windows PowerShell
Rename-Item "使用说明.md" "README.md"
```

选择方案1（重命名为英文）是最简单有效的解决方法。