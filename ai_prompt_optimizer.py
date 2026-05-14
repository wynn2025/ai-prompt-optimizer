#!/usr/bin/env python3
"""
AI Prompt 优化器 (AI Prompt Optimizer)
自动评分 + 多轮优化 + A/B对比 + 模板注入
纯Python标准库，零依赖。可选DeepSeek API增强。
"""

import re
import sys
import json
import os
import argparse
import hashlib
from datetime import datetime
from copy import deepcopy

# ============================================================
# 评分引擎 (复用并增强)
# ============================================================

DIMENSION_NAMES = {
    "clarity": "清晰度",
    "specificity": "具体性",
    "context": "上下文",
    "constraints": "约束条件",
    "executability": "可执行性",
}

def _has_any(text, keywords):
    return any(k in text.lower() for k in keywords)

def _count_any(text, keywords):
    return sum(1 for k in keywords if k in text.lower())

def score_clarity(prompt):
    s, issues, tips = 0, [], []
    cl = len(prompt)
    if cl < 20: s += 1; issues.append("Prompt过短"); tips.append("至少20字描述需求")
    elif cl < 50: s += 3; tips.append("可补充更多细节")
    elif cl < 200: s += 6
    else: s += 8; tips.append("注意不要冗余")
    verbs = ["写","生成","分析","总结","翻译","解释","比较","列出","创建","设计","优化","修改",
             "检查","评估","编写","实现","描述","回答","转换","提取","分类","排序","计算","推荐","规划",
             "write","generate","analyze","summarize","translate","explain","compare","list","create",
             "design","optimize","fix","check","evaluate","implement","describe","convert","extract",
             "recommend","plan","help","make","build","draft"]
    if _has_any(prompt, verbs): s += 2
    else: issues.append("缺少指令动词"); tips.append("用明确动词开头：请写.../分析.../帮我...")
    sents = re.split(r'[。！？.!?\n]', prompt)
    sents = [x.strip() for x in sents if x.strip()]
    if len(sents) >= 2: s += 1
    else: tips.append("分多句表述更清晰")
    vague = ["一些","那个","这种","什么的","随便","差不多","大概","something","some","stuff","whatever"]
    vc = _count_any(prompt, vague)
    if vc > 0: s -= 1; issues.append(f"含{vc}个模糊词"); tips.append("替换模糊表述为具体描述")
    return max(1, min(10, s)), issues, tips

def score_specificity(prompt):
    s, issues, tips = 0, [], []
    if re.search(r'\d+', prompt): s += 2
    else: issues.append("缺数字/量化"); tips.append("添加数字：如'写3个'、'200字'")
    fmt_kw = ["格式","模板","JSON","表格","列表","markdown","要点","分段","标题","代码块",
              "format","template","table","list","bullet","section","heading"]
    if _has_any(prompt, fmt_kw): s += 2
    else: tips.append("指定输出格式：表格/列表/JSON")
    aud_kw = ["面向","给","用于","受众","场景","角色","for","target","audience","scenario","role"]
    if _has_any(prompt, aud_kw): s += 2
    else: tips.append("说明受众/场景")
    if re.search(r'(例如|比如|示例|例子|e\.g\.|example|such as)', prompt, re.I): s += 2
    else: tips.append("提供1-2个示例")
    lang_kw = ["中文","英文","Python","Java","JavaScript","C++","Chinese","English","Go","Rust","TypeScript"]
    if any(k in prompt for k in lang_kw): s += 2
    else: tips.append("指定语言/技术栈")
    return max(1, min(10, s)), issues, tips

def score_context(prompt):
    s, issues, tips = 0, [], []
    ctx_kw = ["背景","目前","现状","项目","公司","团队","系统","环境","版本","background","current",
              "project","team","system","environment","version"]
    if _has_any(prompt, ctx_kw): s += 3
    else: issues.append("缺背景信息"); tips.append("添加背景：'我们是一个创业团队...'")
    role_kw = ["你是","作为","扮演","角色","假设你","请你充当","you are","as a","act as","role"]
    if _has_any(prompt, role_kw): s += 3
    else: tips.append("为AI设定角色：'你是一个资深工程师'")
    io_kw = ["输入","输出","参数","返回","接收","input","output","parameter","return"]
    if _has_any(prompt, io_kw): s += 2
    else: tips.append("说明输入/输出格式")
    ref_kw = ["参考","类似","基于","参照","reference","based on","similar to"]
    if _has_any(prompt, ref_kw): s += 2
    else: tips.append("提供参考材料或案例")
    return max(1, min(10, s)), issues, tips

def score_constraints(prompt):
    s, issues, tips = 0, [], []
    len_kw = ["字","行","段","不超过","最多","至少","限制","以内","范围","words","lines","limit","max","min"]
    if _has_any(prompt, len_kw): s += 2
    else: issues.append("无长度限制"); tips.append("添加：'200字以内'、'5-10条'")
    neg_kw = ["不要","避免","禁止","不能","排除","不含","don't","avoid","never","exclude","without"]
    if _has_any(prompt, neg_kw): s += 2
    else: tips.append("说明不该做什么")
    sty_kw = ["风格","语气","正式","专业","幽默","学术","简洁","通俗","style","tone","formal","casual","concise"]
    if _has_any(prompt, sty_kw): s += 2
    else: tips.append("指定语气风格")
    qual_kw = ["质量","准确","精确","完整","正确","原创","quality","accurate","complete","original"]
    if _has_any(prompt, qual_kw): s += 2
    else: tips.append("设定质量标准")
    cond_kw = ["如果","当","条件","否则","优先","情况下","if","when","condition","otherwise","priority"]
    if _has_any(prompt, cond_kw): s += 2
    else: tips.append("添加条件逻辑")
    return max(1, min(10, s)), issues, tips

def score_executability(prompt):
    s, issues, tips = 0, [], []
    goal_kw = ["目标","目的","为了","需要","想要","帮我","请","goal","need","want","please","help"]
    if _has_any(prompt, goal_kw): s += 2
    else: issues.append("未明确目标"); tips.append("明确目标：'我需要...'")
    step_kw = ["步骤","第一","第二","然后","接着","最后","流程","1.","2.","step","first","then","finally"]
    if _has_any(prompt, step_kw): s += 3
    else: tips.append("分解为步骤")
    ver_kw = ["验证","检查","确认","标准","测试","验收","verify","check","criteria","test","validate"]
    if _has_any(prompt, ver_kw): s += 3
    else: tips.append("添加验收标准")
    if re.search(r'(帮我想想|随便|看着办|都行)', prompt): s -= 2; issues.append("含模糊指令")
    return max(1, min(10, s)), issues, tips

SCORERS = {
    "clarity": score_clarity,
    "specificity": score_specificity,
    "context": score_context,
    "constraints": score_constraints,
    "executability": score_executability,
}

def full_score(prompt):
    dims = {}
    for k, fn in SCORERS.items():
        sc, iss, tip = fn(prompt)
        dims[k] = {"name": DIMENSION_NAMES[k], "score": sc, "issues": iss, "tips": tip}
    total = sum(d["score"] for d in dims.values())
    return {"total": total, "max": 50, "pct": round(total/50*100,1),
            "grade": _grade(total), "dims": dims,
            "preview": prompt[:80]+("..." if len(prompt)>80 else "")}

def _grade(s):
    if s>=40: return "S"
    if s>=32: return "A"
    if s>=24: return "B"
    if s>=16: return "C"
    return "D"


# ============================================================
# 优化模板库
# ============================================================

ROLE_TEMPLATES = {
    "程序员": "你是一个资深软件工程师，精通代码设计、架构和最佳实践。",
    "数据分析师": "你是一个高级数据分析师，擅长数据清洗、统计分析和可视化。",
    "技术写作者": "你是一个专业技术文档工程师，擅长编写清晰准确的技术文档。",
    "产品经理": "你是一个经验丰富的产品经理，擅长需求分析、用户研究和产品规划。",
    "翻译专家": "你是一个专业翻译，精通中英双语，熟悉技术术语和本地化。",
    "SEO专家": "你是一个SEO优化专家，精通搜索引擎规则和内容优化策略。",
    "面试教练": "你是一个资深技术面试官，熟悉大厂面试流程和常见问题。",
    "架构师": "你是一个解决方案架构师，擅长系统设计和性能优化。",
    "general": "你是一个专业的AI助手，擅长精准理解和执行任务。",
}

STRUCTURE_TEMPLATES = {
    "standard": "# 角色\n{role}\n\n# 任务\n{task}\n\n# 要求\n{requirements}\n\n# 输出格式\n{format}\n\n# 约束\n- 语言通俗专业\n- 信息准确完整\n- 结构清晰有逻辑",
    "coding": "# 角色\n{role}\n\n# 任务\n{task}\n\n# 输入\n{input_desc}\n\n# 输出要求\n{output_desc}\n\n# 约束\n- 添加类型提示和注释\n- 遵循PEP8规范\n- 处理边界情况\n- 添加单元测试",
    "analysis": "# 角色\n{role}\n\n# 分析目标\n{task}\n\n# 数据来源\n{input_desc}\n\n# 分析维度\n{requirements}\n\n# 输出格式\n- 执行摘要（3-5句）\n- 详细分析（分章节）\n- 结论和建议\n- 数据支撑",
    "writing": "# 角色\n{role}\n\n# 写作任务\n{task}\n\n# 目标读者\n{audience}\n\n# 风格要求\n{style}\n\n# 字数\n{length}\n\n# 禁止\n- 抄袭内容\n- 虚假信息\n- 冗余表述",
    "review": "# 角色\n{role}\n\n# 审查目标\n{task}\n\n# 审查维度\n1. 正确性\n2. 性能\n3. 可读性\n4. 安全性\n5. 最佳实践\n\n# 输出格式\n- 总体评分(1-10)\n- 每个维度的评分和说明\n- 具体改进建议\n- 修改后的版本",
}

# ============================================================
# 自动优化引擎
# ============================================================

class PromptOptimizer:
    def __init__(self, use_api=False, api_key=None):
        self.use_api = use_api
        self.api_key = api_key
        self.history = []

    def optimize(self, prompt, template="standard", role="general", max_rounds=3, target_score=35):
        """多轮自动优化"""
        self.history = []
        current = prompt
        current_score = full_score(current)
        self.history.append({"round": 0, "prompt": current, "score": current_score, "action": "original"})

        for rnd in range(1, max_rounds + 1):
            if current_score["total"] >= target_score:
                break

            # 确定最弱维度
            weakest = min(current_score["dims"].items(), key=lambda x: x[1]["score"])
            weak_key, weak_val = weakest

            # 应用针对性优化
            improved = self._apply_fix(current, weak_key, weak_val, template, role)
            new_score = full_score(improved)

            self.history.append({
                "round": rnd,
                "prompt": improved,
                "score": new_score,
                "action": f"fixed_{weak_key}",
                "improved_dim": weak_key,
                "before": weak_val["score"],
                "after": new_score["dims"][weak_key]["score"],
            })

            current = improved
            current_score = new_score

        return current, current_score

    def _apply_fix(self, prompt, dim_key, dim_val, template, role):
        """根据弱维度应用具体修复"""
        fixes = {
            "clarity": self._fix_clarity,
            "specificity": self._fix_specificity,
            "context": self._fix_context,
            "constraints": self._fix_constraints,
            "executability": self._fix_executability,
        }
        fixer = fixes.get(dim_key)
        if fixer:
            return fixer(prompt, role)
        return prompt

    def _fix_clarity(self, prompt, role):
        parts = [prompt]
        if not re.search(r'^[\u4e00-\u9fff]', prompt.strip()):
            parts.insert(0, "请完成以下任务：")
        if len(prompt) < 100:
            parts.append("请详细描述实现步骤和关键要点。")
        return "\n".join(parts)

    def _fix_specificity(self, prompt, role):
        parts = [prompt]
        if not re.search(r'\d+', prompt):
            parts.append("请给出3-5个具体要点。")
        if not _has_any(prompt, ["格式","列表","表格","JSON","format","list"]):
            parts.append("输出格式：使用清晰的标题和分点列表。")
        if not any(k in prompt for k in ["中文","英文","Python","Java","JavaScript","Chinese","English"]):
            parts.append("使用中文回答。")
        return "\n".join(parts)

    def _fix_context(self, prompt, role):
        parts = []
        role_text = ROLE_TEMPLATES.get(role, ROLE_TEMPLATES["general"])
        if not _has_any(prompt, ["你是","作为","角色","you are","as a","act as"]):
            parts.append(role_text)
        parts.append(prompt)
        return "\n".join(parts)

    def _fix_constraints(self, prompt, role):
        parts = [prompt]
        if not _has_any(prompt, ["字","行","limit","max","min","以内"]):
            parts.append("字数控制在500字左右。")
        if not _has_any(prompt, ["不要","避免","禁止","don't","avoid","never"]):
            parts.append("避免冗余表述和不必要的专业术语。")
        if not _has_any(prompt, ["风格","语气","style","tone","专业","通俗"]):
            parts.append("语气专业但通俗易懂。")
        return "\n".join(parts)

    def _fix_executability(self, prompt, role):
        parts = [prompt]
        if not _has_any(prompt, ["步骤","第一","1.","step","first"]):
            parts.append("请按步骤完成，每个步骤清晰标注。")
        if not _has_any(prompt, ["验证","检查","标准","verify","check","criteria"]):
            parts.append("请确保结果完整准确，可直接使用。")
        return "\n".join(parts)

    def apply_template(self, prompt, template_name="standard", role="general"):
        """将Prompt套入专业模板"""
        tpl = STRUCTURE_TEMPLATES.get(template_name, STRUCTURE_TEMPLATES["standard"])
        role_text = ROLE_TEMPLATES.get(role, ROLE_TEMPLATES["general"])
        result = tpl.replace("{role}", role_text)
        result = result.replace("{task}", prompt)
        result = result.replace("{requirements}", "根据任务自动推断")
        result = result.replace("{format}", "Markdown格式，清晰分段")
        result = result.replace("{input_desc}", "用户提供的文本/数据")
        result = result.replace("{output_desc}", "完整、准确、可直接使用的结果")
        result = result.replace("{audience}", "技术从业者")
        result = result.replace("{style}", "专业但通俗易懂")
        result = result.replace("{length}", "500-1000字")
        return result

    def compare_ab(self, prompt_a, prompt_b):
        """A/B对比两个Prompt"""
        sa = full_score(prompt_a)
        sb = full_score(prompt_b)
        diff = sb["total"] - sa["total"]
        dims_diff = {}
        for k in sa["dims"]:
            dims_diff[k] = sb["dims"][k]["score"] - sa["dims"][k]["score"]
        return {"a": sa, "b": sb, "diff": diff, "dims_diff": dims_diff,
                "winner": "B" if diff > 0 else ("A" if diff < 0 else "Tie")}


# ============================================================
# DeepSeek API 增强
# ============================================================

def api_optimize(prompt, api_key, instruction="optimize"):
    import urllib.request, ssl
    system_msg = {
        "optimize": "你是Prompt优化专家。优化用户的Prompt，使其更清晰、具体、有效。直接返回优化后的Prompt，不要解释。",
        "score": "你是Prompt评估专家。对用户的Prompt打分(1-10)，返回JSON: {\"total\": N, \"comment\": \"...\"}",
        "rewrite": "你是Prompt重写专家。完全重写用户的Prompt为专业版本，保留原始意图。直接返回新Prompt。",
    }.get(instruction, "你是Prompt优化专家。直接返回优化后的Prompt。")

    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
    }).encode()

    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return None

# ============================================================
# 报告生成
# ============================================================

def render_bar(score, width=15):
    filled = int(score / 10 * width)
    return chr(9608) * filled + chr(9617) * (width - filled)

def report_score(result, label=""):
    lines = []
    if label:
        lines.append(f"  [{label}]")
    lines.append(f"  Score: {result['total']}/50 ({result['pct']}%) Grade: {result['grade']}")
    for k, d in result["dims"].items():
        bar = render_bar(d["score"])
        lines.append(f"    {d['name']:6s} [{bar}] {d['score']}/10")
        for t in d.get("tips", []):
            lines.append(f"           tip: {t}")
    return chr(10).join(lines)

def report_optimize(history):
    lines = []
    lines.append("=" * 60)
    lines.append("  AI Prompt Optimizer - Optimization Report")
    lines.append(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)
    for h in history:
        rnd = h["round"]
        if rnd == 0:
            lines.append(f"\n  --- Original (Score: {h['score']['total']}/50 {h['score']['grade']}) ---")
        else:
            act = h.get('action','')
            bef = h.get('before','?')
            aft = h.get('after','?')
            lines.append(f"\n  --- Round {rnd}: {act} ({bef}->{aft}/10) Score: {h['score']['total']}/50 ---")
        lines.append(f"  {h['prompt'][:200]}")
    if len(history) > 1:
        first = history[0]["score"]["total"]
        last = history[-1]["score"]["total"]
        gain = last - first
        lines.append(f"\n  Total improvement: {first} -> {last} (+{gain} points)")
    lines.append("=" * 60)
    return chr(10).join(lines)

def report_ab(compare_result, prompt_a, prompt_b):
    lines = []
    lines.append("=" * 60)
    lines.append("  A/B Comparison Report")
    lines.append("=" * 60)
    lines.append(report_score(compare_result["a"], "Prompt A"))
    lines.append("")
    lines.append(report_score(compare_result["b"], "Prompt B"))
    lines.append("")
    lines.append(f"  Diff: {compare_result['diff']:+d} points")
    lines.append(f"  Winner: {compare_result['winner']}")
    lines.append("")
    lines.append("  Dimension comparison:")
    for k, v in compare_result["dims_diff"].items():
        sign = "+" if v > 0 else ""
        marker = " <<<" if k == max(compare_result["dims_diff"], key=compare_result["dims_diff"].get) else ""
        lines.append(f"    {DIMENSION_NAMES[k]:6s}: {sign}{v}{marker}")
    lines.append("=" * 60)
    return chr(10).join(lines)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="AI Prompt Optimizer - Auto score, optimize and compare prompts")
    parser.add_argument("--prompt", "-p", help="Prompt to optimize")
    parser.add_argument("--optimize", "-o", action="store_true", help="Auto-optimize the prompt")
    parser.add_argument("--rounds", "-r", type=int, default=3, help="Max optimization rounds (default: 3)")
    parser.add_argument("--target", "-t", type=int, default=35, help="Target score (default: 35)")
    parser.add_argument("--template", choices=list(STRUCTURE_TEMPLATES.keys()), help="Apply structure template")
    parser.add_argument("--role", choices=list(ROLE_TEMPLATES.keys()), default="general", help="Role template")
    parser.add_argument("--compare", nargs=2, metavar=("PROMPT_A", "PROMPT_B"), help="A/B compare two prompts")
    parser.add_argument("--file", "-f", help="Batch optimize from file")
    parser.add_argument("--api-key", "-k", help="DeepSeek API key")
    parser.add_argument("--export", help="Export report to file")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY")
    optimizer = PromptOptimizer(use_api=bool(api_key), api_key=api_key)

    if args.prompt:
        prompt = args.prompt

        if args.optimize:
            # Auto optimize
            print(f"  Optimizing (max {args.rounds} rounds, target {args.target})...")
            result_prompt, result_score = optimizer.optimize(
                prompt, template=args.template or "standard",
                role=args.role, max_rounds=args.rounds, target_score=args.target)

            # Optional API enhancement
            if api_key:
                print("  [DeepSeek API] Enhancing optimization...")
                api_result = api_optimize(result_prompt, api_key)
                if api_result:
                    api_score = full_score(api_result)
                    if api_score["total"] > result_score["total"]:
                        result_prompt = api_result
                        result_score = api_score
                        optimizer.history.append({"round": "API", "prompt": result_prompt,
                                                  "score": result_score, "action": "deepseek_api"})

            report = report_optimize(optimizer.history)
            print(report)
            print()
            print("  >> Final Optimized Prompt:")
            print("  " + "-" * 50)
            for line in result_prompt.split(chr(10)):
                print(f"  {line}")

            if args.json:
                print()
                print(json.dumps({
                    "original": prompt,
                    "optimized": result_prompt,
                    "original_score": full_score(prompt),
                    "final_score": result_score,
                    "history": optimizer.history,
                }, ensure_ascii=False, indent=2, default=str))

        elif args.template:
            # Apply template only
            templated = optimizer.apply_template(prompt, args.template, args.role)
            before = full_score(prompt)
            after = full_score(templated)
            print(f"  Template: {args.template} | Role: {args.role}")
            print(f"  Before: {before['total']}/50 -> After: {after['total']}/50 ({after['total']-before['total']:+d})")
            print()
            print(templated)

        elif args.compare:
            # A/B compare (first arg vs prompt)
            cmp = optimizer.compare_ab(args.prompt, args.compare[0])
            print(report_ab(cmp, args.prompt, args.compare[0]))

        else:
            # Just score
            result = full_score(prompt)
            print(report_score(result))
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.file:
        # Batch mode
        with open(args.file, "r", encoding="utf-8") as f:
            prompts = [l.strip() for l in f if l.strip()]
        print(f"  Batch: {len(prompts)} prompts")
        results = []
        for i, p in enumerate(prompts, 1):
            final, score = optimizer.optimize(p, max_rounds=args.rounds, target_score=args.target)
            orig_score = full_score(p)
            gain = score["total"] - orig_score["total"]
            results.append({"idx": i, "original": p[:80], "optimized": final,
                            "before": orig_score["total"], "after": score["total"], "gain": gain})
            print(f"  [{i}/{len(prompts)}] {orig_score['total']} -> {score['total']} ({gain:+d}) {p[:40]}...")
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))

    else:
        # Interactive mode
        print()
        print("=" * 50)
        print("  AI Prompt Optimizer - Interactive")
        print("  Commands: optimize | template | compare | score | quit")
        print("=" * 50)
        while True:
            print()
            print("Enter prompt (empty line to finish):")
            plines = []
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                if not line.strip():
                    break
                if line.strip().lower() == "quit":
                    return
                plines.append(line)
            prompt = chr(10).join(plines).strip()
            if not prompt:
                continue

            print("Action [score/optimize/template/compare]: ", end="")
            try:
                action = input().strip().lower()
            except EOFError:
                action = "score"

            if action in ("o", "opt", "optimize"):
                result_prompt, result_score = optimizer.optimize(prompt, max_rounds=args.rounds)
                print(report_optimize(optimizer.history))
            elif action in ("t", "template"):
                print(f"Template [{','.join(STRUCTURE_TEMPLATES.keys())}]: ", end="")
                try:
                    tpl = input().strip()
                except EOFError:
                    tpl = "standard"
                templated = optimizer.apply_template(prompt, tpl or "standard", args.role)
                print(templated)
            elif action in ("c", "compare"):
                print("Enter second prompt (empty line to finish):")
                plines2 = []
                while True:
                    try:
                        line = input()
                    except EOFError:
                        break
                    if not line.strip():
                        break
                    plines2.append(line)
                p2 = chr(10).join(plines2).strip()
                if p2:
                    cmp = optimizer.compare_ab(prompt, p2)
                    print(report_ab(cmp, prompt, p2))
            else:
                result = full_score(prompt)
                print(report_score(result))

    if args.export:
        with open(args.export, "w", encoding="utf-8") as f:
            f.write(report_optimize(optimizer.history) if optimizer.history else report_score(full_score(args.prompt or "")))
        print(f"  Report saved: {args.export}")


if __name__ == "__main__":
    main()
