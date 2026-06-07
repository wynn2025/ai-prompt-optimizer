# AI Prompt 优化器 (AI Prompt Optimizer)

<p align="center">
  <a href="https://github.com/wynn2025/ai-prompt-optimizer/stargazers">
    <img src="https://img.shields.io/github/stars/wynn2025/ai-prompt-optimizer?style=social" alt="GitHub Stars">
  </a>
  <a href="https://github.com/wynn2025/ai-prompt-optimizer/watchers">
    <img src="https://img.shields.io/github/watchers/wynn2025/ai-prompt-optimizer?style=social" alt="GitHub Watchers">
  </a>
  <a href="https://github.com/wynn2025/ai-prompt-optimizer/forks">
    <img src="https://img.shields.io/github/forks/wynn2025/ai-prompt-optimizer?style=social" alt="GitHub Forks">
  </a>
  <a href="https://github.com/wynn2025/ai-prompt-optimizer/issues">
    <img src="https://img.shields.io/github/issues/wynn2025/ai-prompt-optimizer" alt="GitHub Issues">
  </a>
  <a href="https://github.com/wynn2025/ai-prompt-optimizer/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/wynn2025/ai-prompt-optimizer" alt="License">
  </a>
</p>

<p align="center">
  <strong>⭐ 如果这个项目对你有帮助，请给一个Star！你的支持是我持续更新的动力 ⭐</strong>
</p>

<p align="center">
  <a href="https://github.com/wynn2025/ai-prompt-optimizer"><strong>🚀 立即使用</strong></a> •
  <a href="https://github.com/wynn2025/ai-prompt-optimizer/issues"><strong>🐛 报告Bug</strong></a> •
  <a href="https://github.com/wynn2025/ai-prompt-optimizer/issues"><strong>💡 功能建议</strong></a> •
  <a href="#贡献指南"><strong>🤝 贡献代码</strong></a>
</p>

---

> 自动评分 + 多轮优化 + A/B对比 + 模板注入，让Prompt效果提升10倍。零依赖，纯Python标准库。

---

## ✨ 核心功能

- **📊 5维度评分** - 清晰度/具体性/上下文/约束条件/可执行性，每项满分10
- **🔄 多轮自动优化** - 自动找到最弱维度，逐轮修复，直到达到目标分数
- **👤 9种角色模板** - 程序员/数据分析师/技术写作者/产品经理/翻译专家/SEO专家/面试教练/架构师
- **📝 5种结构模板** - 标准/编程/分析/写作/审查，一键套用专业格式
- **⚖️ A/B对比** - 两个Prompt直接对比，找出谁更强
- **🤖 DeepSeek API增强** - 可选接入AI进行高级优化
- **⚡ 零依赖** - 纯Python标准库，无需安装任何包

---

## 🎯 适用场景

| 场景 | 说明 | 收益 |
|------|------|------|
| **AI应用开发** - 构建高质量AI应用，提升用户体验 | 提升AI输出质量，减少调试时间 |
| **程序员/开发者** - 获得更准确的代码生成和调试建议 | 代码更准确，问题更快解决 |
| **内容创作者** - 写文章、写文案、写脚本，质量翻倍 | 内容质量提升，阅读量增长 |
| **研究人员** - 数据分析、文献综述、学术写作 | 研究效率提升，成果更专业 |
| **学生党** - 论文写作、作业辅导、知识梳理 | 学业成绩提升，学习更高效 |
| **所有AI工具用户** - 让ChatGPT/文心一言等更好用 | AI工具价值最大化 |

---

## 🚀 快速开始

### 安装

```bash
# Python 3.7+ 无需任何依赖
python ai_prompt_optimizer.py
```

### 使用示例

#### 1. 自动优化（核心功能）

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

#### 2. 指定优化轮数和目标分数

```bash
python ai_prompt_optimizer.py --prompt "你的prompt" --optimize --rounds 5 --target 40
```

#### 3. 套用专业模板

```bash
python ai_prompt_optimizer.py --prompt "分析销售数据" --template analysis --role 数据分析师
```

自动生成包含角色/任务/输入/输出/约束的完整专业Prompt。

#### 4. A/B对比

```bash
python ai_prompt_optimizer.py --prompt "prompt A" --compare "prompt B"
```

#### 5. 批量优化

```bash
python ai_prompt_optimizer.py --file prompts.txt --optimize --json > results.json
```

#### 6. 仅评分

```bash
python ai_prompt_optimizer.py --prompt "你的prompt"
```

---

## 📋 角色模板

| 角色 | 适用场景 | 特点 |
|------|----------|------|
| 程序员 | 代码生成、调试、算法设计 | 专业代码规范，最佳实践 |
| 数据分析师 | 数据分析、可视化、报告 | 结构化思维，数据驱动 |
| 技术写作者 | 技术文档、教程、API文档 | 清晰易懂，逻辑严密 |
| 产品经理 | 需求分析、PRD、竞品分析 | 用户视角，商业价值 |
| 翻译专家 | 多语言翻译、本地化 | 准确地道，术语统一 |
| SEO专家 | 内容优化、关键词布局 | 搜索引擎友好，提升排名 |
| 面试教练 | 模拟面试、简历优化 | 面试技巧，突出优势 |
| 架构师 | 系统设计、技术选型 | 全局视角，架构思维 |

---

## 🏆 项目结构

```
ai-prompt-optimizer/
├── ai_prompt_optimizer.py   # 主脚本 (572行)
├── main.py                  # 入口
├── product.json             # 产品信息
├── requirements.txt         # 依赖(无)
├── LICENSE                  # MIT
└── README.md
```

---

## 🌟 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 开源协议

MIT License

---

<div align="center">

## 💰 购买支持

如果这个项目对你有帮助，可以考虑：

- ⭐ **给个Star** - 这是对我最大的支持！
- 💰 **闲鱼购买** - 获取Pro版完整源码 + 详细文档 + 终身更新
- 🤝 **赞助项目** - 支持持续开发

---

**⭐ 如果觉得有用，请给一个Star！你的支持是我持续更新的动力 ⭐**

[![GitHub Stars](https://img.shields.io/github/stars/wynn2025/ai-prompt-optimizer?style=social)](https://github.com/wynn2025/ai-prompt-optimizer/stargazers)

</div>
