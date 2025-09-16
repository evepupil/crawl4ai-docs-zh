# 分块策略
分块策略对于将大文本分割成可管理部分至关重要，能够实现高效的内容处理和提取。这些策略是基于余弦相似度的提取技术的基础，使用户能够仅检索与给定查询最相关的内容块。此外，它们还有助于直接集成到 RAG（检索增强生成）系统中，以实现结构化和可扩展的工作流程。

### 为何使用分块？
1. **余弦相似度与查询相关性**：为语义相似度分析准备文本块。
2. **RAG 系统集成**：无缝处理和存储块以供检索。
3. **结构化处理**：支持多种分割方法，例如基于句子、基于主题或滑动窗口方法。

### 分块方法

#### 1. 基于正则表达式的分块
根据正则表达式模式分割文本，适用于粗粒度分割。

**代码示例**：
```python
class RegexChunking:
    def __init__(self, patterns=None):
        self.patterns = patterns or [r'\n\n']  # 默认段落模式

    def chunk(self, text):
        paragraphs = [text]
        for pattern in self.patterns:
            paragraphs = [seg for p in paragraphs for seg in re.split(pattern, p)]
        return paragraphs

# 使用示例
text = """This is the first paragraph.

This is the second paragraph."""
chunker = RegexChunking()
print(chunker.chunk(text))
```

#### 2. 基于句子的分块
使用 NLP 工具将文本分割成句子，非常适合提取有意义的语句。

**代码示例**：
```python
from nltk.tokenize import sent_tokenize

class NlpSentenceChunking:
    def chunk(self, text):
        sentences = sent_tokenize(text)
        return [sentence.strip() for sentence in sentences]

# 使用示例
text = "This is sentence one. This is sentence two."
chunker = NlpSentenceChunking()
print(chunker.chunk(text))
```

#### 3. 基于主题的分割
使用 TextTiling 等算法创建主题连贯的文本块。

**代码示例**：
```python
from nltk.tokenize import TextTilingTokenizer

class TopicSegmentationChunking:
    def __init__(self):
        self.tokenizer = TextTilingTokenizer()

    def chunk(self, text):
        return self.tokenizer.tokenize(text)

# 使用示例
text = """This is an introduction.
This is a detailed discussion on the topic."""
chunker = TopicSegmentationChunking()
print(chunker.chunk(text))
```

#### 4. 固定长度词分块
将文本分割成固定词数的文本块。

**代码示例**：
```python
class FixedLengthWordChunking:
    def __init__(self, chunk_size=100):
        self.chunk_size = chunk_size

    def chunk(self, text):
        words = text.split()
        return [' '.join(words[i:i + self.chunk_size]) for i in range(0, len(words), self.chunk_size)]

# 使用示例
text = "This is a long text with many words to be chunked into fixed sizes."
chunker = FixedLengthWordChunking(chunk_size=5)
print(chunker.chunk(text))
```

#### 5. 滑动窗口分块
生成重叠的文本块以获得更好的上下文连贯性。

**代码示例**：
```python
class SlidingWindowChunking:
    def __init__(self, window_size=100, step=50):
        self.window_size = window_size
        self.step = step

    def chunk(self, text):
        words = text.split()
        chunks = []
        for i in range(0, len(words) - self.window_size + 1, self.step):
            chunks.append(' '.join(words[i:i + self.window_size]))
        return chunks

# 使用示例
text = "This is a long text to demonstrate sliding window chunking."
chunker = SlidingWindowChunking(window_size=5, step=2)
print(chunker.chunk(text))
```

### 将分块与余弦相似度结合使用
为了增强提取内容的相关性，可以将分块策略与余弦相似度技术结合使用。以下是一个示例工作流程：

**代码示例**：
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CosineSimilarityExtractor:
    def __init__(self, query):
        self.query = query
        self.vectorizer = TfidfVectorizer()

    def find_relevant_chunks(self, chunks):
        vectors = self.vectorizer.fit_transform([self.query] + chunks)
        similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
        return [(chunks[i], similarities[i]) for i in range(len(chunks))]

# 工作流程示例
text = """This is a sample document. It has multiple sentences. 
We are testing chunking and similarity."""

chunker = SlidingWindowChunking(window_size=5, step=3)
chunks = chunker.chunk(text)
query = "testing chunking"
extractor = CosineSimilarityExtractor(query)
relevant_chunks = extractor.find_relevant_chunks(chunks)

print(relevant_chunks)
```