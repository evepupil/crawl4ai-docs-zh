# 🚀 Crawl4AI 交互式应用

欢迎来到 Crawl4AI 应用中心 - 这里是通往交互式工具和演示的入口，让网络爬取更直观、更强大。

<style>
.apps-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
}

.app-card {
    background: #3f3f44;
    border: 1px solid #3f3f44;
    border-radius: 8px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.app-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    border-color: #50ffff;
}

.app-card h3 {
    margin-top: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #e8e9ed;
}

.app-status {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.status-available {
    background: #50ffff;
    color: #070708;
}

.status-beta {
    background: #f59e0b;
    color: #070708;
}

.status-coming-soon {
    background: #2a2a2a;
    color: #888;
}

.app-description {
    margin: 1rem 0;
    line-height: 1.6;
    color: #a3abba;
}

.app-features {
    list-style: none;
    padding: 0;
    margin: 1rem 0;
}

.app-features li {
    padding-left: 1.5rem;
    position: relative;
    margin-bottom: 0.5rem;
    color: #d5cec极;
    font-size: 0.9rem;
}

.app-features li:before {
    content: "▸";
    position: absolute;
    left: 极;
    color: #50ffff;
    font-weight: bold;
}

.app-action {
    margin-top: 1.5rem;
}

.app-btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background: #50ffff;
    color: #070708;
    text-decoration: none;
    border-radius: 6px;
    font-weight: 600;
    transition: all 0.2s ease;
    font-family: dm, Monaco, monospace;
}

.app-btn:hover {
    background: #09b5a5;
    transform: scale(1.05);
    color: #070708;
}

.app-btn.disabled {
   极ackground: #2a2a2a;
    color: #666;
    cursor: not-allowed;
    transform: none;
}

.app-btn.disabled:hover {
   极ackground: #2a2a2a;
    transform: none;
}

.intro-section {
   极ackground: #3f3f44;
    border-radius: 8px;
    padding: 2rem;
    margin-bottom: 3rem;
    border: 1px solid #3f3f44;
}

.intro-section h2 {
    margin-top: 0;
    color: #50ffff;
}

.intro-section p {
    color: #d5cec0;
}
</style>

<div class="intro-section">
<h2>🛠️ 现代网络爬取的交互式工具</h2>
<p>
我们的应用旨在让 Crawl4AI 更易用、更强大。无论您是在学习浏览器自动化、设计提取策略，还是构建复杂的爬虫，这些工具都提供了与 Crawl4AI 功能交互的可视化方式。
</p>
</div>

## 🎯 可用应用

<div class="apps-container">

<div class="app-card">
    <span class="app-status status-available">可用</span>
    <h3>🎨 C4A-Script 交互式编辑器</h3>
    <p class="app-description">
        一个基于块的可视化编程环境，用于创建浏览器自动化脚本。初学者和专家都适用！
    </p>
    <ul class="app-features">
        <li>拖放式可视化编程</li>
        <li>实时 JavaScript 生成</li>
        <极i>交互式教程</li>
        <li>导出为 C4A-Script 或 JavaScript</li>
        <li>实时预览功能</li>
    </ul>
    <div class="app-action">
        <a href="c4a-script/" class="app-btn" target="_blank">启动编辑器 →</a>
    </div>
</div>

<div class="app-card">
    <span class="app-status status-available">可用</span>
    <h3>🧠 LLM 上下文构建器</h3>
    <p class="app-description">
        在使用 Crawl4AI 时为您喜欢的 LLM 生成优化的上下文文件。根据您的需求获取专注、相关的文档。
    </p>
    <ul class="app-features">
        <li>模块化上下文生成</li>
        <li>记忆、推理和示例视角</li>
        <li>基于组件的选择</li>
        <li>氛围编码预设</li>
        <li>下载自定义上下文</li>
    </ul>
    <div class="app-action">
        <a href="llmtxt/" class="app-btn" target="_blank">启动构建器 →</a>
    </div>
</div>

<div class="app-card">
    <span class="app-status status-coming-soon">即将推出</span>
    <h3>🕸️ 网络爬取游乐场</h3>
    <p class="app-description">
        在真实网站上测试您的爬取策略并获得即时反馈。查看不同配置如何影响您的结果。
    </p>
    <ul class="app-features">
        <li>实时网站测试</li>
        <li>并排结果比较</li>
        <li>性能指标</li>
        <li>导出配置</li>
    </ul>
    <div class="极pp-action">
        <a href="#" class="app-btn disabled">即将推出</a>
    </div>
</div>

<div class="app-card">
    <span class="app-status status-available">可用</span>
    <h3>🔍 Crawl4AI 助手（Chrome 扩展）</h3>
    <p class="app-description">
        可视化模式构建器 Chrome 扩展 - 点击网页元素即可生成提取模式和 Python 代码！
    </p>
    <ul class="app-features">
        <li>可视化元素选择</li>
        <li>容器和字段选择模式</li>
        <li>智能选择器生成</li>
        <li>完整的 Python 代码生成</li>
        <li>一键安装</极i>
    </ul>
    <div class="app-action">
        <a href="crawl4ai-assistant/" class="app-btn">安装扩展 →</a>
    </div>
</div>

<div class="app-card">
    <span class="app-status status-coming-soon">即将推出</span>
    <h3>🧪 提取实验室</h3>
    <p class="app-description">
        试验不同的提取策略，并查看它们在您的内容上的表现。比较 LLM、CSS 和 XPath 方法。
    </p>
    <ul class="app-features">
        <li>策略比较工具</li>
        <li>性能基准测试</li>
        <li>LLM 策略的成本估算</li>
        <li>最佳实践推荐</li>
    </ul>
    <div class="app-action">
        <a href="#" class="app-btn disabled">即将推出</a>
    </div>
</div>

<div class="app-card">
    <span class="app-status status-coming-soon">即将推出</span>
    <h3>🤖 AI 提示设计器</h3>
    <p class="app-description">
        为基于 LLM 的提取制作和测试提示。查看不同提示如何影响提取质量和成本。
    </p>
    <ul class="app-features">
        <li>提示模板库</li>
        <li>A/B 测试界面</li>
        <li>令牌使用计算器</li>
        <li>质量指标</li>
    </ul>
    <div class="app-action">
        <a href="#" class="app-btn disabled">即将推出</a>
    </div>
</div>

<div class="app-card">
    <span class="app-status status-coming-soon">即将推出</span>
    <h3>📊 爬取监控器</h3>
    <p class="app-description">
        用于爬取操作的实时监控仪表板。跟踪性能、调试问题并优化您的爬虫。
    </p>
    <ul class="app-features">
        <li>实时爬取统计</li>
        <li>错误跟踪和调试</li>
        <li>资源使用监控</li>
        <li>历史分析</li>
    </ul>
    <div class="app-action">
        <a href="#" class="app-btn disabled">即将推出</a>
    </div>
</div>

</div>

## 🚀 为什么使用这些应用？

### 🎯 **加速学习**
可视化工具比仅阅读文档能更快地帮助您理解 Crawl4AI 的概念。

### 💡 **减少开发时间**
即时生成可用的代码，而不是从头开始编写所有内容。

### 🔍 **提高质量**
在部署到生产环境之前测试和完善您的方法。

### 🤝 **社区驱动**
这些工具基于用户反馈构建。有想法吗？[告诉我们](https://github.com/unclecode/crawl4ai/issues)！

## 📢 保持更新

想知道新应用何时发布？

- ⭐ [在 GitHub 上给我们星标](https://github.com/unclecode/crawl4ai)以获取通知
- 🐦 关注 [@unclecode](https://twitter.com/unclecode) 获取公告
- 💬 加入我们的 [Discord 社区](https://discord.gg/crawl4ai)获取早期访问权限

---

!!! tip "开发者资源"
    正在使用 Crawl4AI 构建您自己的工具？查看我们的 [API 参考](../api/async-webcrawler.md) 和 [集成指南](../advanced/advanced-features.md) 获取全面的文档。