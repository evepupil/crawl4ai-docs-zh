<div class="ask-ai-container">
<iframe id="ask-ai-frame" src="../../ask_ai/index.html" width="100%" style="border:none; display: block;" title="Crawl4AI Assistant"></iframe>
</div>

<script>
// Iframe高度调整
function resizeAskAiIframe() {
  const iframe = document.getElementById('ask-ai-frame');
  if (iframe) {
    const headerHeight = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header-height') || '55');
    // 页脚已被下方JS移除，因此基于页眉高度+缓冲值计算高度
    const topOffset = headerHeight + 20; // 页眉高度 + 缓冲边距

    const availableHeight = window.innerHeight - topOffset;
    iframe.style.height = Math.max(600, availableHeight) + 'px'; // 最小高度600px
  }
}

// 立即执行并在调整大小/加载时运行
resizeAskAiIframe(); // 初始调用
let resizeTimer;
window.addEventListener('load', resizeAskAiIframe);
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(resizeAskAiIframe, 150);
});

// 从父页面移除页脚和水平分割线（DOM Ready更安全）
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => { // 添加短暂延迟以防元素渲染缓慢
        const footer = window.parent.document.querySelector('footer'); // 目标父文档
        if (footer) {
            const hrBeforeFooter = footer.previousElementSibling;
            if (hrBeforeFooter && hrBeforeFooter.tagName === 'HR') {
                hrBeforeFooter.remove();
            }
            footer.remove();
            // 移除页脚后再次触发调整大小
            resizeAskAiIframe();
        } else {
             console.warn("Ask AI Page: Could not find footer in parent document to remove.");
        }
    }, 100); // 较短延迟
});
</script>

<style>
#terminal-mkdocs-main-content {
    padding: 0 !important;
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden; /* 防止主体出现滚动条，面板处理滚动 */
}

/* 确保iframe容器占据全部空间 */
#terminal-mkdocs-main-content .ask-ai-container {
    /* 如果页脚移除处理了空间，则移除负边距 */
     margin: 0;
    padding: 0;
    max-width: none;
    /* 让JS设置高度 */
    /* height: 600px; 初始备用高度 */
    overflow: hidden; /* 在JS调整大小前隐藏潜在溢出 */
}

/* 隐藏标题/段落（如果它们是markdown的一部分） */
/* 或者直接从.md文件中移除它们 */
/* #terminal-mkdocs-main-content > h1,
#terminal-mkdocs-main-content > p:first-of-type {
    display: none;
} */

</style>