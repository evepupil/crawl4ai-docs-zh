"""
检测器模块，包含各种文档框架的具体检测实现
"""

# 导入所有检测器，方便统一管理
from docslib_detector.detectors.mkdocs import MkDocsDetector
from docslib_detector.detectors.docusaurus import DocusaurusDetector
from docslib_detector.detectors.gitbook import GitBookDetector
from docslib_detector.detectors.readthedocs import ReadTheDocsDetector
from docslib_detector.detectors.custom_backend import CustomBackendDetector
from docslib_detector.detectors.hybrid_api import HybridAPIDetector

# 所有可用的检测器列表
AVAILABLE_DETECTORS = [
    MkDocsDetector,
    DocusaurusDetector,
    GitBookDetector,
    ReadTheDocsDetector,
    CustomBackendDetector,
    HybridAPIDetector
] 