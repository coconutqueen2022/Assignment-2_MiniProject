# NLP

## 要求

### 1. 数据收集 📊

- 使用 Stack Exchange API 从 Stack Overflow 上收集带有 [nlp] 标签的帖子
- 需要收集至少 20,000 个帖子
- 数据需要包含以下列：
  - 帖子标题
  - 帖子描述
  - 标签
  - 至少一个被采纳的答案
  - 更多被采纳的答案（可选）

### 2. 数据预处理 🧹

- 需要进行至少 4 种预处理任务，比如：
  - 删除标点符号
  - 转换为小写
  - 删除特殊符号
  - 分词
  - 删除截图

### 3. 数据可视化 📈

- 使用 WordCloud 生成帖子标题中最常用词汇的词云
- 需要确保词云真实反映重要的 NLP 术语

### 4. 帖子分类 📑

- 需要对收集到的帖子进行分类
- 每个类别至少要包含 10 个帖子
- 总共要分类至少 100 个帖子
- 可以按照以下方式分类：
  - 实现问题（包含 "how to" 的帖子）
  - 任务类型（如文本相似度计算、分词等）
  - 理解问题（包含 "what" 的帖子）
  - 技术工具（如 spaCy, NLTK, hugging face 等）

### 5. 代码实现 💻

- 代码需要清晰易懂
- 有良好的注释
- 可执行

## 实现思路

### 1. 数据收集阶段 📊

- 使用 `stackapi` Python 包来调用 Stack Exchange API
- 主要思路：
  - 先获取带 [nlp] 标签的所有问题 ID
  - 分批获取详细信息（因为 API 有请求限制）
  - 将数据存储在 Pandas DataFrame 中
  - 使用异步请求来加速数据收集
- 数据存直接保存为 JSON 格式

### 2. 数据预处理阶段 🧹

- 使用 NLTK 和 spaCy 库进行文本预处理
- 预处理步骤：
  - 使用正则表达式移除代码块和 HTML 标签
  - 移除 URLs 和图片链接
  - 文本标准化（转小写）
  - 分词和词形还原
  - 移除停用词
- 对于代码部分，单独保存，不进行文本预处理

### 3. 可视化阶段 📈

- 使用 WordCloud 和 matplotlib 进行可视化
- 改进思路：
  - 自定义停用词列表，加入 NLP 领域特定的常见词
  - 使用 TF-IDF 来识别重要术语
  - 设计特别的配色方案，让词云更美观
  - 可能还要加入时间序列分析，看看问题趋势

### 4. 分类系统设计 🗂

- 采用多层分类方法：
  1. 第一层：问题类型
     - 实现问题（How-to questions）
     - 概念理解（What-is questions）
     - 错误处理（Error-related）
     - 最佳实践（Best practices）
  
  2. 第二层：技术领域
     - 文本预处理
     - 文本分类
     - 命名实体识别
     - 情感分析
     - 机器翻译
     - 等等...

  3. 第三层：技术栈
     - NLTK
     - spaCy
     - Transformers
     - Word2Vec
     - BERT
     - 等等...

### 分类实现思路 🤔

1. **规则基础方法**
   - 关键词匹配
   - 正则表达式模式
   - 启发式规则

2. **机器学习方法**
   - 使用 sentence-transformers 计算文本相似度
   - 可能使用 LDA 主题建模
   - 考虑用 BERT 做多标签分类

### 项目管理 📝

- 使用 Git 进行版本控制
- 模块化设计，便于维护和扩展
- 添加详细的文档说明
- 使用配置文件管理参数
- 加入日志系统，方便调试

### 性能优化考虑 ⚡️

- 使用多进程处理大量数据
- 实现数据缓存机制
- 采用批处理方式处理大量请求
- 考虑使用数据库存储而不是 CSV（如果数据量真的很大）

## 项目结构

```text
./
├── .gitignore                # Git 忽略文件
├── README.md                 # 项目说明文档
├── pyproject.toml           # 项目依赖管理
├── requirements.txt         # 依赖列表（用于部署）
├── config/
│   └── config.yaml         # 配置文件（API keys, 参数等）
│
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── collector.py    # Stack Exchange API 数据收集
│   │   └── preprocessor.py # 数据预处理
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── classifier.py   # 分类模型
│   │
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── visualizer.py   # 词云和其他可视化
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py       # 日志工具
│       └── helpers.py      # 通用辅助函数
│
├── data/
│   ├── raw/                # 原始数据
│   ├── processed/          # 处理后的数据
│   └── output/             # 输出结果（词云图等）
│
├── tests/
│   ├── __init__.py
│   ├── test_collector.py
│   ├── test_preprocessor.py
│   └── test_classifier.py
│
└── scripts/
    ├── run_collection.py   # 数据收集脚本
    ├── run_processing.py   # 数据处理脚本
    └── run_analysis.py     # 分析和可视化脚本
```

### 代码风格和质量控制 🎯

- 使用 `ruff format` 进行代码检查

### 主要模块功能 🔧

1. **data/collector.py**
   - Stack Exchange API 的封装
   - 异步数据收集
   - 数据验证和初步清理

2. **data/preprocessor.py**
   - 文本清理和标准化
   - 分词和词形还原
   - 特征提取

3. **models/classifier.py**
   - 分类规则实现
   - 文本相似度计算
   - 分类结果验证

4. **visualization/visualizer.py**
   - 词云生成
   - 分类统计可视化
   - 时间序列分析图表

5. **utils/**
   - 日志配置
   - 通用工具函数
   - 配置文件处理

### 使用建议 💡

1. 使用 `uv` 创建虚拟环境：

```bash
uv sync
```

2. 运行脚本：

```bash
python scripts/run_collection.py
python scripts/run_processing.py
python scripts/run_analysis.py
```

