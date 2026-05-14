# AI Prompt 优化器 (AI Prompt Optimizer)

> 自动评分 + 多轮优化 + A/B对比 + 模板注入，让Prompt效果提升10倍

## 核心功能

- **5维度评分**: 清晰度/具体性/上下文/约束条件/可执行性，每项满分10
- **多轮自动优化**: 自动找到最弱维度，逐轮修复，直到达到目标分数
- **9种角色模板**: 程序员/数据分析师/技术写作者/产品经理/翻译专家/SEO专家/面试教练/架构师
- **5种结构模板**: 标准/编程/分析/写作/审查，一键套用专业格式
- **A/B对比**: 两个Prompt直接对比，找出谁更强
- **DeepSeek API增强**: 可选接入AI进行高级优化
- **零依赖**: 纯Python标准库

## 快速开始

```bash
# 自动优化（核心功能）
python ai_prompt_optimizer.py --prompt "写一个Python函数" --optimize

# 指定优化轮数和目标分数
python ai_prompt_optimizer.py --prompt "你的prompt" --optimize --rounds 5 --target 40

# 套用专业模板
python ai_prompt_optimizer.py --prompt "分析销售数据" --template analysis --role 数据分析师

# A/B对比
python ai_prompt_optimizer.py --prompt "prompt A" --compare "prompt B"

# 批量优化
python ai_prompt_optimizer.py --file prompts.txt --optimize

# 仅评分
python ai_prompt_optimizer.py --prompt "你的prompt"
```

## 使用示例

### 示例1: 自动优化一个简单Prompt

```bash
python ai_prompt_optimizer.py --prompt "写一个Python函数" --optimize
```

输出：
```
  --- Original (Score: 8/50 D) ---
  写一个Python函数

  --- Round 1: fixed_context (1->3/10) Score: 16/50 ---
  你是一个专业的AI助手...

  --- Round 2: fixed_executability (1->5/10) Score: 25/50 ---

  --- Round 3: fixed_specificity (2->8/10) Score: 33/50 ---

  Total improvement: 8 -> 33 (+25 points)
```

### 示例2: 套用专业模板

```bash
python ai_prompt_optimizer.py --prompt "分析销售数据趋势" --template analysis --role 数据分析师
```

自动生成包含角色/任务/输入/输出/约束的完整专业Prompt。

### 示例3: 批量处理

```bash
python ai_prompt_optimizer.py --file prompts.txt --optimize --json > results.json
```

## 定价

| 版本 | 价格 | 说明 |
|------|------|------|
| 基础版 | 29元 | 本地评分+优化+模板 |
| Pro版 | 49元 | 含DeepSeek API增强优化 |

## 项目结构

```
ai-prompt-optimizer/
├── ai_prompt_optimizer.py   # 主脚本 (572行)
├── main.py                  # 入口
├── product.json             # 产品信息
├── requirements.txt         # 依赖(无)
├── LICENSE                  # MIT
└── README.md
```

## License

MIT
