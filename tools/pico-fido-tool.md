# Pico FIDO 工具使用文档

`pico-fido-tool.py` 是一个用于管理和配置 Pico FIDO 设备的命令行工具。该工具提供多种功能，包括设备认证、备份管理和物理配置设置等。

## 环境要求

在使用该工具之前，请确保已安装以下 Python 包：

```bash
pip install fido2 cryptography
```

## 命令行选项

### 基本用法
```bash
python pico-fido-tool.py -p <PIN> [命令] [选项]
```

所有命令都需要提供设备的 PIN 码。使用 `-p` 或 `--pin` 参数指定：
```bash
python pico-fido-tool.py -p 123456 [命令] [选项]
```

### 可用命令

#### 1. 安全操作
```bash
python pico-fido-tool.py -p <PIN> secure <子命令>
```
可用子命令：
- `enable`: 启用设备认证
- `disable`: 禁用设备认证
- `unlock`: 解锁设备

示例：
```bash
# 启用设备认证
python pico-fido-tool.py -p 123456 secure enable

# 禁用设备认证
python pico-fido-tool.py -p 123456 secure disable

# 解锁设备
python pico-fido-tool.py -p 123456 secure unlock
```

#### 2. 备份操作
```bash
python pico-fido-tool.py -p <PIN> backup <子命令> <文件名>
```
可用子命令：
- `save <文件名>`: 创建设备配置备份
- `load <文件名>`: 从备份文件恢复配置

示例：
```bash
# 创建备份
python pico-fido-tool.py -p 123456 backup save my_backup.bin

# 从备份恢复
python pico-fido-tool.py -p 123456 backup load my_backup.bin
```

#### 3. 证书管理
```bash
python pico-fido-tool.py -p <PIN> attestation <子命令> [选项]
```
可用子命令：
- `csr`: 生成证书签名请求
  - `--filename <文件名>`: 可选，指定要上传的证书文件

示例：
```bash
# 生成 CSR
python pico-fido-tool.py -p 123456 attestation csr

# 上传证书
python pico-fido-tool.py -p 123456 attestation csr --filename cert.der
```

#### 4. 物理配置（PHY）
```bash
python pico-fido-tool.py -p <PIN> phy <子命令> [值]
```
可用子命令：
- `vidpid <VID:PID>`: 设置 USB VID/PID（使用冒号分隔）
- `led_gpio <GPIO编号>`: 配置 LED GPIO 引脚
- `led_brightness <亮度值>`: 设置 LED 亮度（0-15）
- `wcid <enable|disable>`: 启用/禁用 Web CCID 接口
- `led_dimmable <enable|disable>`: 启用/禁用 LED 调光功能

示例：
```bash
# 设置 USB VID/PID
python pico-fido-tool.py -p 123456 phy vidpid 1234:5678

# 配置 LED GPIO
python pico-fido-tool.py -p 123456 phy led_gpio 25

# 设置 LED 亮度
python pico-fido-tool.py -p 123456 phy led_brightness 128

# 启用 WCID
python pico-fido-tool.py -p 123456 phy wcid enable

# 启用 LED 调光
python pico-fido-tool.py -p 123456 phy led_dimmable enable
```

#### 5. 设备 PIN 管理
```bash
python pico-fido-tool.py --set-pin <PIN>
```
示例：
```bash
# 设置设备 PIN
python pico-fido-tool.py --set-pin 123456
```

#### 6. PIN 操作
```bash
python pico-fido-tool.py pin <子命令>
```
可用子命令：
- `set`: 设置新的设备 PIN
- `change`: 更改现有的设备 PIN

示例：
```bash
# 设置新的设备 PIN
python pico-fido-tool.py pin set --new-pin 654321

# 更改现有的设备 PIN
python pico-fido-tool.py pin change --current-pin 123456 --new-pin 654321
```

#### 7. 重置设备

重置命令会擦除设备上的所有凭证和 PIN。使用此命令时要格外小心。

```bash
# 重置设备(会提示确认)
python pico-fido-tool.py reset

# 强制重置设备(不提示确认)
python pico-fido-tool.py reset --force
```

注意事项:
1. 重置后所有存储的凭证和 PIN 将被永久删除
2. 重置需要物理接触设备(通常需要按住按钮)
3. 重置后需要重新设置 PIN 和重新注册凭证
4. 建议在重置前备份重要数据

示例输出:
```bash
# 普通重置
$ python pico-fido-tool.py reset
警告: 这将擦除所有凭证和 PIN。输入 "RESET" 确认: RESET
设备已成功重置

# 取消重置
$ python pico-fido-tool.py reset
警告: 这将擦除所有凭证和 PIN。输入 "RESET" 确认: no
已取消重置

# 强制重置
$ python pico-fido-tool.py reset --force
设备已成功重置
```

可能的错误:
- "错误: 设备不允许重置。请确保没有用户在场。" - 需要按住设备按钮
- "错误: PIN 认证当前被锁定。请稍后再试。" - 等待一段时间后重试

## 常用 VID/PID 参考表

以下是一些常用的 VID/PID 组合及其对应的设置命令。请注意，在使用这些值时应确保它们不会与其他设备冲突。

### FIDO 设备标准 VID/PID

| 设备类型 | VID | PID | 说明 | 设置命令 |
|---------|-----|-----|------|----------|
| FIDO2 标准设备 | 0x2C97 | 0x0001 | 标准 FIDO2 认证器 | `python pico-fido-tool.py -p 123456 phy vidpid 2C97:0001` |
| U2F 标准设备 | 0x2C97 | 0x0002 | 仅 U2F 功能 | `python pico-fido-tool.py -p 123456 phy vidpid 2C97:0002` |
| CCID 模式 | 0x2C97 | 0x0003 | 智能卡读卡器模式 | `python pico-fido-tool.py -p 123456 phy vidpid 2C97:0003` |

### 开发测试用 VID/PID

| 设备类型 | VID | PID | 说明 | 设置命令 |
|---------|-----|-----|------|----------|
| 开发模式 | 0x0483 | 0xA2CA | 开发测试专用 | `python pico-fido-tool.py -p 123456 phy vidpid 0483:A2CA` |
| 调试模式 | 0x0483 | 0xA2CB | 调试功能启用 | `python pico-fido-tool.py -p 123456 phy vidpid 0483:A2CB` |

### 自定义 VID/PID 示例

| 设备类型 | VID | PID | 说明 | 设置命令 |
|---------|-----|-----|------|----------|
| 自定义设备 1 | 0x1234 | 0x5678 | 通用自定义设置 | `python pico-fido-tool.py -p 123456 phy vidpid 1234:5678` |
| 自定义设备 2 | 0xABCD | 0xEF01 | 备用自定义设置 | `python pico-fido-tool.py -p 123456 phy vidpid ABCD:EF01` |

### 商用 FIDO 设备 VID/PID

#### Yubico 设备

| 设备型号 | VID | PID | 说明 | 设置命令 |
|---------|-----|-----|------|----------|
| YubiKey 5 NFC | 0x1050 | 0x0407 | FIDO2 + NFC 功能 | `python pico-fido-tool.py -p 123456 phy vidpid 1050:0407` |
| YubiKey 5C | 0x1050 | 0x0407 | USB-C 接口版本 | `python pico-fido-tool.py -p 123456 phy vidpid 1050:0407` |
| YubiKey 5C NFC | 0x1050 | 0x0407 | USB-C + NFC | `python pico-fido-tool.py -p 123456 phy vidpid 1050:0407` |
| YubiKey 5 Nano | 0x1050 | 0x0407 | 超小型设计 | `python pico-fido-tool.py -p 123456 phy vidpid 1050:0407` |
| YubiKey Bio | 0x1050 | 0x0407 | 指纹识别版本 | `python pico-fido-tool.py -p 123456 phy vidpid 1050:0407` |
| Security Key NFC | 0x1050 | 0x0120 | 仅 FIDO 功能 | `python pico-fido-tool.py -p 123456 phy vidpid 1050:0120` |
| YubiKey 4 | 0x1050 | 0x0406 | 旧版本设备 | `python pico-fido-tool.py -p 123456 phy vidpid 1050:0406` |
| YubiKey NEO | 0x1050 | 0x0116 | 经典版本 | `python pico-fido-tool.py -p 123456 phy vidpid 1050:0116` |

#### Nitrokey 设备

| 设备型号 | VID | PID | 说明 | 设置命令 |
|---------|-----|-----|------|----------|
| Nitrokey FIDO2 | 0x20A0 | 0x42B1 | 基础 FIDO2 功能 | `python pico-fido-tool.py -p 123456 phy vidpid 20A0:42B1` |
| Nitrokey Pro 2 | 0x20A0 | 0x4108 | 专业版本 | `python pico-fido-tool.py -p 123456 phy vidpid 20A0:4108` |
| Nitrokey Storage 2 | 0x20A0 | 0x4109 | 带存储功能 | `python pico-fido-tool.py -p 123456 phy vidpid 20A0:4109` |
| Nitrokey Start | 0x20A0 | 0x4211 | 入门版本 | `python pico-fido-tool.py -p 123456 phy vidpid 20A0:4211` |
| Nitrokey HSM 2 | 0x20A0 | 0x4230 | 企业级 HSM | `python pico-fido-tool.py -p 123456 phy vidpid 20A0:4230` |

#### 其他厂商设备

| 设备型号 | VID | PID | 说明 | 设置命令 |
|---------|-----|-----|------|----------|
| Feitian ePass FIDO | 0x096E | 0x085B | FIDO 安全密钥 | `python pico-fido-tool.py -p 123456 phy vidpid 096E:085B` |
| Feitian BioPass FIDO2 | 0x096E | 0x0850 | 生物识别版本 | `python pico-fido-tool.py -p 123456 phy vidpid 096E:0850` |
| SoloKey | 0x0483 | 0xA2CA | 开源安全密钥 | `python pico-fido-tool.py -p 123456 phy vidpid 0483:A2CA` |
| Google Titan | 0x18D1 | 0x5026 | Google 安全密钥 | `python pico-fido-tool.py -p 123456 phy vidpid 18D1:5026` |
| Thetis FIDO2 | 0x311F | 0x4A2A | 标准 FIDO2 密钥 | `python pico-fido-tool.py -p 123456 phy vidpid 311F:4A2A` |
| HyperFIDO | 0x2581 | 0xF1D0 | 基础 FIDO 设备 | `python pico-fido-tool.py -p 123456 phy vidpid 2581:F1D0` |

### 设备模式说明

许多 FIDO 设备支持多种操作模式，可能会在不同模式下使用不同的 PID：

1. **OTP 模式**：用于一次性密码功能
2. **FIDO 模式**：用于 U2F 和 FIDO2 功能
3. **CCID 模式**：用于智能卡功能
4. **FIDO+CCID 模式**：组合模式

### 模式切换提示

- 部分设备支持通过特定操作切换模式（如按住按钮插入设备）
- 模式切换可能会改变设备的 PID
- 建议参考具体设备的用户手册了解支持的模式和切换方法

### 注意事项

1. VID（Vendor ID）通常是由 USB-IF 组织分配的厂商标识符
2. PID（Product ID）是由厂商自行分配的产品标识符
3. 在生产环境中使用自定义 VID/PID 时，需要确保：
   - 不与现有设备冲突
   - 遵守 USB-IF 的规范
   - 在产品文档中明确记录所使用的值
4. 建议在开发测试时使用开发专用的 VID/PID，在正式发布时使用正式分配的值

## 高级用法

### 设备认证
设备认证功能为设备提供额外的安全层。启用后，设备在执行敏感操作时需要认证。

```bash
# 启用认证（自动生成密钥）
python pico-fido-tool.py -p 123456 secure enable

# 禁用认证
python pico-fido-tool.py -p 123456 secure disable
```

### 备份管理
建议定期备份以保存设备配置和凭证信息。

```bash
# 创建带时间戳的备份
python pico-fido-tool.py -p 123456 backup save backup_$(date +%Y%m%d).bin

# 恢复到最后一个已知的正确配置
python pico-fido-tool.py -p 123456 backup load last_known_good.bin
```

### LED 配置
根据需求调整设备 LED 行为：

```bash
# 设置 LED 中等亮度并启用调光
python pico-fido-tool.py -p 123456 phy led_brightness 128 led_dimmable enable

# 最大亮度，禁用调光
python pico-fido-tool.py -p 123456 phy led_brightness 255 led_dimmable disable
```

## Windows 系统特别说明

在 Windows 系统上使用 Pico FIDO 工具需要以下设置：

1. 安装 HID 设备驱动
   - 打开设备管理器
   - 找到 "人体学输入设备" 或 "Human Interface Devices"
   - 确保设备被识别为 HID 设备
   - 如果显示为未知设备，需要安装 HID 驱动

2. 安装 WINUSB 驱动
   - 下载并安装 [Zadig](https://zadig.akeo.ie/)
   - 运行 Zadig
   - 从设备列表中选择 Pico FIDO 设备
   - 选择 "WinUSB" 驱动
   - 点击 "Install Driver" 或 "Replace Driver"

3. 环境设置
   ```bash
   # 确保安装了所有必需的包
   pip install fido2 cryptography hidapi
   ```

4. 以管理员身份运行
   - 右键点击 PowerShell 或 CMD
   - 选择 "以管理员身份运行"
   - 导航到工具目录
   - 运行命令

5. 常见的 Windows 特定问题：

   a. 设备未被识别为 HID 设备
   ```
   解决方法：
   1. 在设备管理器中找到设备
   2. 右键选择"更新驱动程序"
   3. 选择"自动搜索驱动程序"
   ```

   b. 权限问题
   ```
   解决方法：
   1. 以管理员身份运行命令提示符
   2. 确保当前用户有 HID 设备的访问权限
   ```

   c. 驱动程序冲突
   ```
   解决方法：
   1. 卸载现有的设备驱动
   2. 使用 Zadig 重新安装 WinUSB 驱动
   3. 重新插入设备
   ```

### 使用 Zadig 安装驱动的详细步骤

1. 下载并运行 Zadig
2. 菜单中选择 "Options" -> "List All Devices"
3. 从下拉菜单中找到 Pico FIDO 设备
   - 可能显示为 "Unknown Device" 或 "HID Device"
   - 检查 USB ID 是否匹配（VID:PID）
4. 在驱动选项中选择 "WinUSB"
5. 点击 "Install Driver" 或 "Replace Driver"
6. 等待安装完成
7. 拔出并重新插入设备
8. 重新运行 Pico FIDO 工具

### 验证设备连接

在 Windows PowerShell 中运行以下命令来验证设备是否被正确识别：

```powershell
# 检查 USB 设备
Get-PnpDevice -Class USB

# 或使用 Python 检查
python -c "from fido2.hid import CtapHidDevice; print(list(CtapHidDevice.list_devices()))"
```

如果设备被正确识别，第二个命令应该会显示设备信息。如果显示空列表，说明设备未被正确识别为 FIDO 设备。

## 错误处理

### 设备连接问题

如果遇到以下错误：
```
AttributeError: 'NoneType' object has no attribute 'capabilities'
```

这表示工具无法找到或连接到 Pico FIDO 设备。请按以下步骤排查：

1. 确保设备已正确连接到 USB 端口
2. 检查设备是否被系统识别：
   - Windows: 在设备管理器中查看是否有未识别的设备
   - Linux: 运行 `lsusb` 命令查看设备是否列出
3. 尝试以下操作：
   - 拔出并重新插入设备
   - 尝试使用其他 USB 端口
   - 检查 USB 线缆是否完好
4. 确保设备处于正确的模式：
   - 设备应该处于 FIDO 模式而不是其他模式（如 CCID 模式）
   - 如果设备有模式切换按钮，请确保在正确的模式下

如果问题仍然存在：
1. 检查是否已正确安装所有依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 确保使用的是最新版本的 Pico FIDO 固件
3. 如果设备完全无响应，可能需要重新刷写固件

### 其他常见错误

1. PIN 错误
```
Error: PIN verification failed
```
- 确保输入的 PIN 正确
- 如果连续输错多次，设备可能会锁定
- 使用 `secure unlock` 命令解锁设备

2. 命令格式错误
```
Error: Invalid command format
```
- 检查命令语法是否正确
- 确保所有必需的参数都已提供
- 参考文档中的示例命令

3. VID/PID 格式错误
```
Error: Invalid VID/PID format
```
- 确保使用正确的格式：`VID:PID`
- VID 和 PID 应该是 4 位十六进制数
- 不要使用 `0x` 前缀

## 最佳实践

1. 在进行配置更改前务必创建备份
2. 使用包含日期的有意义的备份文件名
3. 将 LED 亮度保持在舒适水平
4. 记录部署中使用的自定义 VID/PID 组合

## 安全注意事项

1. 安全存储备份文件
2. 在生产环境中使用设备认证
3. 定期更新设备固件
4. 保持工具和其依赖项为最新版本