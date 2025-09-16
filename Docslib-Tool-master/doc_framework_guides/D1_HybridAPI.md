# 混合型文档（部分静态+API）翻译指南

## 文件翻译范围

混合型文档系统结合了静态生成和动态API内容，主要翻译内容包括：

1. **静态部分**：
   - 静态生成的HTML、Markdown或其他格式文件
   - 页面模板中的固定文本
   - 导航菜单、页脚等固定UI元素

2. **API部分**：
   - API返回的动态内容
   - 错误消息和状态描述
   - 动态加载的帮助文本和提示

3. **配置文件**：
   - 前端配置文件（如`config.js`、`settings.json`等）
   - 国际化资源文件
   - API端点配置

4. **客户端脚本**：
   - JavaScript文件中的用户界面文本
   - 客户端验证消息
   - 交互提示和通知

5. **静态资源**：
   - 图片中的文本
   - 图表和图形中的标签
   - 下载文件中的内容

## 部署步骤

### 准备工作

1. 获取前端和API源代码
```bash
git clone https://github.com/原始项目/前端仓库.git frontend
git clone https://github.com/原始项目/API仓库.git api
```

2. 安装依赖
```bash
# 前端依赖
cd frontend
npm install

# API依赖
cd ../api
pip install -r requirements.txt  # Python API示例
```

### 翻译流程

#### 前端静态内容翻译

1. 识别国际化框架（如React-i18next、Vue-i18n等）

2. 提取待翻译文本
```bash
# 示例：使用i18next
npm run i18n-extract

# 或手动提取
i18next-scanner --config i18next-scanner.config.js 'src/**/*.{js,jsx,ts,tsx}'
```

3. 翻译语言文件
   - 编辑`locales/zh/`目录下的翻译文件
   - 或使用翻译管理工具导入/导出

4. 更新前端配置支持新语言
```javascript
// 示例配置
const i18nConfig = {
  supportedLngs: ['en', 'zh'],
  defaultLng: 'en',
  // ...其他配置
};
```

#### API内容翻译

1. 识别API国际化机制
   - 基于Accept-Language头的内容协商
   - 基于URL参数的语言选择
   - 基于用户设置的语言偏好

2. 翻译API响应内容
   - 翻译语言资源文件（如`.json`、`.po`文件等）
   - 翻译数据库中的内容（如需要）
   - 更新API文档中的示例响应

3. 配置API支持多语言
```python
# Python Flask示例
from flask_babel import Babel

app = Flask(__name__)
babel = Babel(app)

@babel.localeselector
def get_locale():
    return request.args.get('lang', 'en')
```

### 构建与测试

1. 构建前端应用
```bash
npm run build
```

2. 启动API服务
```bash
# Python示例
python app.py
```

3. 测试完整系统
   - 测试语言切换功能
   - 验证API响应的翻译
   - 测试动态加载内容的翻译

### 部署方法

1. **前端部署**：
   - 部署构建好的静态文件到CDN或Web服务器
   - 配置语言相关的路由规则

2. **API部署**：
   - 更新API服务器代码
   - 部署翻译资源文件
   - 配置语言检测和内容协商

3. **集成部署**：
   - 确保前端和API之间的语言设置一致
   - 配置跨域资源共享（CORS）支持多语言请求

## 注意事项

1. **前后端一致性**：
   - 确保前端和API使用相同的语言代码（如'zh-CN'vs'zh'）
   - 保持术语翻译在前端和API之间的一致性

2. **动态内容缓存**：
   - 考虑针对不同语言的缓存策略
   - 确保缓存键包含语言信息

3. **内容协商**：
   - 正确处理Accept-Language头
   - 提供语言回退机制

4. **URL策略**：
   - 决定是使用路径前缀（如`/zh/docs`）还是查询参数（如`?lang=zh`）
   - 确保所有内部链接正确处理语言参数

5. **用户语言偏好**：
   - 保存用户语言选择
   - 在前端和API之间同步语言设置

6. **混合内容处理**：
   - 确保静态内容和动态内容的语言切换同步
   - 处理部分翻译内容缺失的情况

7. **搜索功能**：
   - 确保搜索能处理多语言内容
   - 考虑语言特定的搜索优化

## 自动化工具建议

1. 创建端到端测试确保翻译完整性
2. 使用翻译管理系统统一管理前端和API翻译
3. 建立翻译同步工具，保持前端和API翻译的一致性
4. 设置监控系统检测翻译缺失或不匹配

## 维护更新

1. 建立前端和API翻译的同步更新流程
2. 创建翻译审核机制，确保质量和一致性
3. 监控用户反馈，特别是与语言相关的问题
4. 定期检查翻译覆盖率，识别需要更新的内容 