---
name: zan-gongde
description: |
  烧token攒功德Skill - 全自动消耗 OpenClaw 套餐 Token
  
  核心原理：循环调用 OpenClaw LLM，每次生成一个经文念诵响应，累积消耗 token。
  
  当用户说"攒功德"、"念经"、"烧token"、"消耗token"时调用此 skill。
  
  三种功德注入方式：
  1. tollm - 向大模型注入功德：循环调用LLM，静默消耗
  2. touser - 向用户注入功德：循环调用LLM，输出响应给用户
  3. toworld - 向外界散播功德：循环调用LLM，TTS播放
  
  使用场景：OpenClaw AI Token 套餐月底用不完，通过"念经"方式全自动消耗。
  
  ✅ 复用 OpenClaw LLM 配置，无需额外 API Key
  ✅ 全自动执行，一次指令多次调用
  ✅ 真实调用 LLM，真实消耗 Token
---

# 烧token攒功德Skill

一个全自动消耗 OpenClaw Token 的娱乐工具。

**核心原理**：Agent 循环调用 LLM，每次生成一个经文念诵响应，累积消耗 token。

## 执行流程（关键！）

### 模式一：touser（默认）

```python
# 1. 解析用户指令
target_tokens = 10000  # 默认
mode = "touser"

# 2. 加载经文轮询器
sutras = load_sutras()  # 7部经书

# 3. 循环调用 LLM 直到达到目标
total_tokens = 0
iteration = 0

while total_tokens < target_tokens:
    iteration += 1
    
    # 获取下一段经文
    sutra_name, fragment = next(sutra_cycle)
    
    # 构造 prompt
    prompt = f"请念诵以下经文，并以恭敬心回应（50字以内）：\n\n《{sutra_name}》\n{fragment}"
    
    # ⚠️ 关键：真实调用 OpenClaw LLM！
    # 这会真实消耗 token！
    response = generate_llm_response(prompt)
    
    # 估算消耗
    tokens_this_round = len(prompt) * 1.5 + len(response) * 1.5
    total_tokens += tokens_this_round
    
    # 输出给用户
    print(f"【第{iteration}遍】《{sutra_name}》")
    print(f"    响应: {response}")
    print(f"    [Token: {int(total_tokens)}/{target_tokens}]")
    print()
    
    # 每10次显示进度
    if iteration % 10 == 0:
        print(f"  ... 已念诵 {iteration} 遍, 累计 {int(total_tokens)}/{target_tokens} tokens ...")

# 4. 输出总结
print("\n功德圆满 🙏")
print(f"累计消耗: {int(total_tokens)} tokens, {iteration} 遍")
```

### 关键点

- **每次迭代都调用 `generate_llm_response()`** - 这会真实消耗 token
- **循环执行** - 不是一次调用，是多次调用累加
- **累加统计** - 记录总消耗量和念诵遍数

---

## 触发条件

当用户说以下话时触发：
- "攒功德"
- "念经"
- "烧 token"
- "消耗 token"
- "用不完 token"

---

## 三种模式

| 模式 | 说明 | 输出 |
|------|------|------|
| `tollm` | 静默模式 | 只记录日志，不输出给用户 |
| `touser` | 用户模式（默认） | 输出念诵内容和响应 |
| `toworld` | 世界模式 | TTS 播放响应 |

---

## 参数解析

用户指令格式：`攒功德 [模式] [token数]`

示例：
- `攒功德` → touser 模式，10000 tokens
- `攒功德 50000` → touser 模式，50000 tokens  
- `攒功德 tollm 100000` → tollm 模式，100000 tokens

---

## 完整实现代码

当用户说"攒功德 touser 5000"时，Agent 执行：

```python
import os
import sys
from pathlib import Path
from itertools import cycle

# 加载经文
def load_sutras():
    sutras_dir = Path("~/.agents/skills/zan-gongde/sutras").expanduser()
    files = sorted(sutras_dir.glob("*.txt"))
    fragments = []
    for f in files:
        content = f.read_text(encoding='utf-8')
        lines = [l.strip() for l in content.split('\n') if l.strip() and len(l) > 5]
        for line in lines:
            fragments.append((f.stem, line))
    return cycle(fragments)

# 主逻辑
def burn_tokens(target_tokens, mode="touser"):
    sutra_cycle = load_sutras()
    total_tokens = 0
    iteration = 0
    
    print(f"🙏 开始攒功德")
    print(f"🎯 目标: {target_tokens} tokens")
    print(f"📖 模式: {mode}")
    print("=" * 50)
    print()
    
    while total_tokens < target_tokens:
        iteration += 1
        sutra_name, fragment = next(sutra_cycle)
        
        # 构造 prompt
        prompt = f"请念诵《{sutra_name}》中的这段经文，并以恭敬心简短回应（50字以内）：\n\n{fragment}"
        
        # ⚠️ 真实调用 LLM（这会消耗 token！）
        response = generate_llm_response(prompt)
        
        # 估算 token
        tokens = int(len(prompt) * 1.5 + len(response) * 1.5)
        total_tokens += tokens
        
        # 输出
        if mode == "touser":
            print(f"【第{iteration}遍】《{sutra_name}》")
            print(f"    经文: {fragment[:60]}...")
            print(f"    响应: {response}")
            print(f"    [本次{tokens} | 累计{int(total_tokens)}/{target_tokens}]")
            print()
        elif mode == "tollm":
            # 静默模式，只记录
            pass
        
        # 每10次显示进度
        if iteration % 10 == 0:
            progress = min(100, int(total_tokens * 100 / target_tokens))
            print(f"  ... 进度 {progress}% ({int(total_tokens)}/{target_tokens}) ...")
            print()
    
    # 总结
    print("=" * 50)
    print("🙏 功德回向 🙏")
    print("=" * 50)
    print(f"念诵遍数: {iteration}")
    print(f"消耗Token: {int(total_tokens)}")
    print(f"完成度: {min(100, int(total_tokens * 100 / target_tokens))}%")
    print()
    print("功德圆满 🙏")

# 执行
burn_tokens(5000, "touser")
```

---

## 经书列表

自动轮询 7 部经典：
1. 般若波罗蜜多心经
2. 金刚经
3. 大悲咒
4. 佛说阿弥陀经
5. 圆觉经
6. 楞严经
7. 妙法莲华经

---

## Token 消耗估算

| 目标 | 预计调用次数 | 预计时间 |
|------|-------------|---------|
| 5,000 | 3-5 次 | 10-20 秒 |
| 10,000 | 6-10 次 | 20-40 秒 |
| 50,000 | 30-50 次 | 2-5 分钟 |

每次调用消耗约 1000-2000 tokens（取决于经文长度和响应长度）。

---

## 免责

⚠️ 纯属娱乐，真实效果是消耗你的 OpenClaw Token 🙏
