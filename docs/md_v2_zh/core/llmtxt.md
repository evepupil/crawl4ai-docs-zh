<div class="llmtxt-container">
<iframe id="llmtxt-frame" src="../../llmtxt/index.html" width="100%" style="border:none; display: block;" title="Crawl4AI LLM Context Builder"></iframe>
</div>

<script>
// Iframe高度调整
function resizeLLMtxtIframe() {
  const iframe = document.getElementById('llmtxt-frame');
  if (iframe) {
    const headerHeight = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header-height') || '55');
    const topOffset = headerHeight + 20;
    const availableHeight = window.innerHeight - topOffset;
    iframe.style.height = Math.max(800, availableHeight) + 'px';
  }
}

// 立即执行并在调整大小/加载时运行
resizeLLMtxtIframe();
let resizeTimer;
window.addEventListener('load', resizeLLMtxtIframe);
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(resizeLLMtxtIframe, 150);
});

// 从父页面移除页脚和水平分割线
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const footer = window.parent.document.querySelector('footer');
        if (footer) {
            const hrBeforeFooter = footer.previousElementSibling;
            if (hrBeforeFooter && hrBeforeFooter.tagName === 'HR') {
                hrBeforeFooter.remove();
            }
            footer.remove();
            resizeLLMtxtIframe();
        }
    }, 100);
});
</script>

<style>
#terminal-mkdocs-main-content {
    padding: 0 !important;
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

#terminal-mkdocs-main-content .llmtxt-container {
    margin: 0;
    padding: 0;
    max-width: none;
    overflow: hidden;
}

#terminal-mkdocs-toc-panel {
    display: none !important;
}
</style>