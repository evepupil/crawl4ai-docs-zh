# DocsLib Detector

文档仓库部署类型检测工具，用于自动识别开源项目文档使用的框架类型。

## 功能特点

- 自动检测多种文档框架类型
- 提供详细的检测结果和置信度
- 支持命令行参数扩展
- 丰富的日志信息
- 模块化结构，易于扩展

## 支持的文档框架

- 静态生成框架
  - MkDocs
  - Docusaurus
  - GitBook
- 动态渲染框架
  - ReadTheDocs
  - 自定义后端
- 混合型框架
  - 部分静态+API

## 安装

```bash
# 从源码安装
git clone https://github.com/yourusername/docslib-detector.git
cd docslib-detector
pip install -e .

# 或直接通过pip安装
pip install docslib-detector
```

## 使用方法

### 命令行使用

```bash
# 基本用法
docslib-detector /path/to/docs/repo

# 指定输出格式为JSON
docslib-detector /path/to/docs/repo -f json

# 将结果保存到文件
docslib-detector /path/to/docs/repo -o result.txt

# 调整置信度阈值
docslib-detector /path/to/docs/repo -t 0.7

# 输出详细日志
docslib-detector /path/to/docs/repo -v

# 不生成日志文件
docslib-detector /path/to/docs/repo --no-log-file

# 指定日志文件路径
docslib-detector /path/to/docs/repo --log-file custom_log.log
```

### Python API使用

```python
from docslib_detector.core.detector_manager import DetectorManager
from docslib_detector.utils.logger import get_logger

# 配置日志
logger = get_logger("my_app")

# 初始化检测管理器
detector_manager = DetectorManager("/path/to/docs/repo", logger)

# 执行检测
results = detector_manager.detect(threshold=0.5)

# 获取最佳匹配
best_match = detector_manager.get_best_match()
if best_match:
    print(f"检测到框架: {best_match.framework_type}")
    print(f"置信度: {best_match.confidence}")
    print(f"详细信息: {best_match.get_framework_info()}")

# 获取检测摘要
summary = detector_manager.get_detection_summary()
```

## 扩展检测器

要添加新的框架检测器，只需继承`DetectorBase`类并实现相应方法：

```python
from docslib_detector.core.detector_base import DetectorBase

class MyNewDetector(DetectorBase):
    @property
    def framework_type(self) -> str:
        return "my_framework"
    
    def detect(self) -> bool:
        # 实现检测逻辑
        # ...
        return self._confidence > 0.5
    
    def get_framework_info(self) -> dict:
        # 返回框架详细信息
        return {
            "framework": "MyFramework",
            "type": "static",
            # ...其他信息
        }
```

然后将新检测器添加到`docslib_detector/detectors/__init__.py`的`AVAILABLE_DETECTORS`列表中。

## 许可证

MIT 