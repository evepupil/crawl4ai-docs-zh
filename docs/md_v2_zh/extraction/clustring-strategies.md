# 余弦策略

Crawl4AI 中的余弦策略采用基于相似度的聚类方法，从网页中识别并提取相关内容片段。该策略在需要基于语义相似性而非结构模式来查找和提取内容时特别有用。

## 工作原理

余弦策略：
1. 将页面内容分解为有意义的文本块
2. 将文本转换为向量表示
3. 计算文本块之间的相似度
4. 将相似内容聚类在一起
5. 基于相关性对内容进行排序和过滤

## 基本用法

```python
from crawl4ai import CosineStrategy

strategy = CosineStrategy(
    semantic_filter="product reviews",    # 目标内容类型
    word_count_threshold=10,             # 每个聚类的最小单词数
    sim_threshold=0.3                    # 相似度阈值
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
        url="https://example.com/reviews",
        extraction_strategy=strategy
    )
    
    content = result.extracted_content
```

## 配置选项

### 核心参数

```python
CosineStrategy(
    # 内容过滤
    semantic_filter: str = None,       # 用于内容过滤的关键词/主题
    word_count_threshold: int = 10,    # 每个聚类的最小单词数
    sim_threshold: float = 0.3,        # 相似度阈值（0.0 到 1.0）
    
    # 聚类参数
    max_dist: float = 0.2,            # 聚类的最大距离
    linkage_method: str = 'ward',      # 聚类连接方法
    top_k: int = 3,                   # 要提取的顶级类别数量
    
    # 模型配置
    model_name: str = 'sentence-transformers/all-MiniLM-L6-v2',  # 嵌入模型
    
    verbose: bool = False             # 启用日志记录
)
```

### 参数详情

1. **semantic_filter**
   - 设置目标主题或内容类型
   - 使用与所需内容相关的关键词
   - 示例："technical specifications", "user reviews", "pricing information"

2. **sim_threshold**
   - 控制内容必须有多相似才能被分组
   - 较高的值（例如 0.8）意味着更严格的匹配
   - 较低的值（例如 0.3）允许更多变化
   ```python
   # 严格匹配
   strategy = CosineStrategy(sim_threshold=0.8)
   
   # 宽松匹配
   strategy = CosineStrategy(sim_threshold=0.3)
   ```

3. **word_count_threshold**
   - 过滤掉短内容块
   - 有助于消除噪音和无关内容
   ```python
   # 仅考虑实质性段落
   strategy = CosineStrategy(word_count_threshold=50)
   ```

4. **top_k**
   - 要返回的顶级内容聚类数量
   - 较高的值返回更多样化的内容
   ```python
   # 获取前 5 个最相关的内容聚类
   strategy = CosineStrategy(top_k=5)
   ```

## 使用场景

### 1. 文章内容提取
```python
strategy = CosineStrategy(
    semantic_filter="main article content",
    word_count_threshold=100,  # 文章需要更长的文本块
    top_k=1                   # 通常只需要单一主要内容
)

result = await crawler.arun(
    url="https://example.com/blog/post",
    extraction_strategy=strategy
)
```

### 2. 产品评论分析
```python
strategy = CosineStrategy(
    semantic_filter="customer reviews and ratings",
    word_count_threshold=20,   # 评论可以较短
    top_k=10,                 # 获取多个评论
    sim_threshold=0.4         # 允许评论内容多样化
)
```

### 3. 技术文档
```python
strategy = CosineStrategy(
    semantic_filter="technical specifications documentation",
    word_count_threshold=30,
    sim_threshold=0.6,        # 对技术内容采用更严格的匹配
    max_dist=0.3             # 允许相关技术部分
)
```

## 高级功能

### 自定义聚类
```python
strategy = CosineStrategy(
    linkage_method='complete',  # 替代聚类方法
    max_dist=0.4,              # 更大的聚类
    model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'  # 多语言支持
)
```

### 内容过滤管道
```python
strategy = CosineStrategy(
    semantic_filter="pricing plans features",
    word_count_threshold=15,
    sim_threshold=0.5,
    top_k=3
)

async def extract_pricing_features(url: str):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
            extraction_strategy=strategy
        )
        
        if result.success:
            content = json.loads(result.extracted_content)
            return {
                'pricing_features': content,
                'clusters': len(content),
                'similarity_scores': [item['score'] for item in content]
            }
```

## 最佳实践

1. **迭代调整阈值**
   - 从默认值开始
   - 根据结果进行调整
   - 监控聚类质量

2. **选择合适的单词数阈值**
   - 文章使用较高值（100+）
   - 评论/留言使用较低值（20+）
   - 产品描述使用中等值（50+）

3. **优化性能**
   ```python
   strategy = CosineStrategy(
       word_count_threshold=10,  # 提前过滤
       top_k=5,                 # 限制结果数量
       verbose=True             # 监控性能
   )
   ```

4. **处理不同的内容类型**
   ```python
   # 对于混合内容页面
   strategy = CosineStrategy(
       semantic_filter="product features",
       sim_threshold=0.4,      # 更灵活的匹配
       max_dist=0.3,          # 更大的聚类
       top_k=3                # 多个相关部分
   )
   ```

## 错误处理

```python
try:
    result = await crawler.arun(
        url="https://example.com",
        extraction_strategy=strategy
    )
    
    if result.success:
        content = json.loads(result.extracted_content)
        if not content:
            print("未找到相关内容")
    else:
        print(f"提取失败: {result.error_message}")
        
except Exception as e:
    print(f"提取过程中出错: {str(e)}")
```

余弦策略在以下情况下特别有效：
- 内容结构不一致
- 需要语义理解
- 需要查找相似的内容块
- 基于结构（CSS/XPath）的提取不可靠

它可以与其他策略良好配合，并可用作基于 LLM 提取的预处理步骤。