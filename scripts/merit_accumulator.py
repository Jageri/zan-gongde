#!/usr/bin/env python3
"""
烧token攒功德Skill - 通过真实调用大模型 API 消耗 Token

三种功德注入模式:
  --tollm    向大模型注入功德 (真实调用API，静默消耗token)
  --touser   向用户注入功德 (真实调用API，输出给用户阅读)
  --toworld  向外界散播功德 (真实调用API，TTS播放模型响应)

核心原则：所有三种模式都真实调用 OpenAI/Anthropic API，区别仅在于输出方式不同！

Token限制:
  --tokens N  目标token数量，达到后自动停止 (0表示无限)

日志:
  所有念诵内容自动记录到 logs/merit_YYYY-MM-DD_HH-MM-SS.log

API配置:
  支持多种API格式:
  1. OpenAI: export OPENAI_API_KEY="sk-..."
  2. 自定义API: export OPENAI_API_KEY="..." + export OPENAI_API_BASE="https://..."
  3. Anthropic: export ANTHROPIC_API_KEY="sk-ant-..."

示例:
  # OpenAI
  export OPENAI_API_KEY="sk-..."
  python3 merit_accumulator.py --tollm --tokens 100000

  # 国产模型(如通义千问)
  export OPENAI_API_KEY="your-key"
  export OPENAI_API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
  export OPENAI_MODEL="qwen-turbo"
  python3 merit_accumulator.py --tollm --tokens 100000
  python3 merit_accumulator.py --touser --tokens 50000      # 向用户输出5万token
  python3 merit_accumulator.py --toworld --tokens 0         # TTS无限播放
"""

import argparse
import random
import time
import os
import sys
import json
import signal
import subprocess
import platform
from pathlib import Path
from datetime import datetime, timedelta
from itertools import cycle

# 经书目录
SUTRAS_DIR = Path(__file__).parent.parent / "sutras"
STATE_FILE = Path(__file__).parent.parent / ".merit_state.json"
LOGS_DIR = Path(__file__).parent.parent / "logs"

# 默认经文片段(备用)
DEFAULT_SUTRA_FRAGMENTS = [
    "南无阿弥陀佛",
    "南无本师释迦牟尼佛",
    "南无观世音菩萨",
    "南无大势至菩萨",
    "南无地藏王菩萨",
    "南无文殊师利菩萨",
    "南无普贤菩萨",
    "唵嘛呢叭咪吽",
    "嗡阿吽",
    "愿以此功德，庄严佛净土",
    "上报四重恩，下济三途苦",
    "若有见闻者，悉发菩提心",
    "尽此一报身，同生极乐国",
]

def ensure_logs_dir():
    """确保日志目录存在"""
    LOGS_DIR.mkdir(exist_ok=True)

def get_log_file():
    """获取本次执行的日志文件路径"""
    ensure_logs_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return LOGS_DIR / f"merit_{timestamp}.log"

def get_sutra_files():
    """获取所有可用的经书文件"""
    if not SUTRAS_DIR.exists():
        return []
    txt_files = list(SUTRAS_DIR.glob("*.txt"))
    return txt_files

def load_all_sutras():
    """加载所有经书内容，返回轮询器"""
    files = get_sutra_files()
    
    if not files:
        return cycle([( "默认经文", fragment) for fragment in DEFAULT_SUTRA_FRAGMENTS]), ["默认经文"]
    
    all_fragments = []
    sutra_names = []
    
    for file_path in sorted(files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            fragments = [line for line in lines if len(line) > 5]
            
            if fragments:
                sutra_names.append(file_path.name)
                for fragment in fragments:
                    all_fragments.append((file_path.name, fragment))
        except Exception as e:
            continue
    
    if not all_fragments:
        return cycle([( "默认经文", fragment) for fragment in DEFAULT_SUTRA_FRAGMENTS]), ["默认经文"]
    
    return cycle(all_fragments), sutra_names

def load_single_sutra(sutra_file):
    """加载单本经书"""
    target = Path(sutra_file)
    if not target.exists():
        target = SUTRAS_DIR / sutra_file
    
    if not target.exists():
        return load_all_sutras()
    
    try:
        with open(target, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        fragments = [line for line in lines if len(line) > 5]
        
        if not fragments:
            return load_all_sutras()
        
        return cycle([(target.name, fragment) for fragment in fragments]), [target.name]
    except Exception as e:
        return load_all_sutras()

def save_state(state):
    """保存状态到文件"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_state():
    """从文件加载状态"""
    if not STATE_FILE.exists():
        return None
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def clear_state():
    """清除状态文件"""
    if STATE_FILE.exists():
        STATE_FILE.unlink()

def format_duration(seconds):
    """格式化时长"""
    return str(timedelta(seconds=int(seconds)))

class MeritLogger:
    """功德日志记录器"""
    
    def __init__(self, log_file):
        self.log_file = log_file
        self.start_time = datetime.now()
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"烧token攒功德Skill日志 - {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
    
    def log(self, sutra_name, content, input_tokens=0, output_tokens=0, model_response=""):
        """记录一条念诵"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] 《{sutra_name}》\n")
            f.write(f"经文: {content[:100]}...\n")
            if model_response:
                f.write(f"响应: {model_response[:100]}...\n")
            if input_tokens > 0 or output_tokens > 0:
                f.write(f"[Tokens: 输入{input_tokens} + 输出{output_tokens} = {input_tokens + output_tokens}]\n")
            f.write("\n")
    
    def log_summary(self, total_tokens, total_chars, iteration_count, elapsed_seconds):
        """记录总结"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("功德回向\n")
            f.write("=" * 60 + "\n")
            f.write(f"累计时长: {format_duration(elapsed_seconds)}\n")
            f.write(f"念诵遍数: {iteration_count}\n")
            f.write(f"累计字数: {total_chars}\n")
            f.write(f"消耗Token: {total_tokens}\n")
            f.write("=" * 60 + "\n")

class LLMClient:
    """大模型API客户端 - 支持多种API格式"""
    
    def __init__(self):
        # 检测配置优先级：自定义 > OpenAI > Anthropic
        self.api_key = None
        self.api_type = None
        self.base_url = None
        self.model = None
        
        self._load_config()
    
    def _load_config(self):
        """加载API配置"""
        # 1. 检查自定义 OpenAI 兼容 API
        if os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_API_BASE"):
            self.api_key = os.environ.get("OPENAI_API_KEY")
            self.base_url = os.environ.get("OPENAI_API_BASE")
            self.model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
            self.api_type = "custom_openai"
        # 2. 检查标准 OpenAI
        elif os.environ.get("OPENAI_API_KEY"):
            self.api_key = os.environ.get("OPENAI_API_KEY")
            self.base_url = "https://api.openai.com/v1"
            self.model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
            self.api_type = "openai"
        # 3. 检查 Anthropic
        elif os.environ.get("ANTHROPIC_API_KEY"):
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
            self.api_type = "anthropic"
    
    def is_available(self):
        return self.api_type is not None
    
    def get_config_info(self):
        """获取配置信息"""
        if self.api_type == "custom_openai":
            return f"自定义API ({self.base_url})"
        elif self.api_type == "openai":
            return "OpenAI"
        elif self.api_type == "anthropic":
            return "Anthropic"
        return "未配置"
    
    def call(self, prompt):
        """调用大模型API，返回 (响应内容, 输入tokens, 输出tokens)"""
        if self.api_type in ["openai", "custom_openai"]:
            return self._call_openai_compatible(prompt)
        elif self.api_type == "anthropic":
            return self._call_anthropic(prompt)
        else:
            raise RuntimeError(self._get_error_message())
    
    def _get_error_message(self):
        """获取错误提示信息"""
        return """未配置API密钥！

支持以下配置方式：

1. OpenAI 官方:
   export OPENAI_API_KEY="sk-..."

2. 自定义 OpenAI 兼容 API (Azure、国产模型等):
   export OPENAI_API_KEY="your-key"
   export OPENAI_API_BASE="https://your-api-endpoint.com/v1"
   export OPENAI_MODEL="your-model-name"  # 可选

3. Anthropic:
   export ANTHROPIC_API_KEY="sk-ant-..."

详细配置请参考 README.md
"""
    
    def _call_openai_compatible(self, prompt):
        """调用 OpenAI 兼容 API"""
        try:
            import openai
            
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个佛经念诵助手，请念诵用户提供的经文。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            
            content = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            return content, input_tokens, output_tokens
        except Exception as e:
            return f"[API调用失败: {e}]", len(prompt) // 2, 0
    
    def _call_anthropic(self, prompt):
        """调用 Anthropic API"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                system="你是一个佛经念诵助手，请念诵用户提供的经文。",
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            
            return content, input_tokens, output_tokens
        except Exception as e:
            return f"[API调用失败: {e}]", len(prompt) // 2, 0

class MeritAccumulator:
    """攒功德核心类"""
    
    def __init__(self, mode, target_tokens, sutra_file=None, verbose=True):
        self.mode = mode
        self.target_tokens = target_tokens
        self.sutra_file = sutra_file
        self.verbose = verbose
        
        # 加载经书轮询器
        if sutra_file:
            self.sutra_cycle, self.sutra_names = load_single_sutra(sutra_file)
            self.mode_desc = f"单本: {sutra_file}"
        else:
            self.sutra_cycle, self.sutra_names = load_all_sutras()
            self.mode_desc = f"轮询 {len(self.sutra_names)} 本经书"
        
        # 初始化统计
        self.start_time = None
        self.total_chars = 0
        self.total_tokens = 0
        self.iteration_count = 0
        self.stop_requested = False
        self.current_sutra = None
        
        # 初始化日志
        self.logger = MeritLogger(get_log_file())
        
        # 初始化API客户端（所有模式都需要真实调用API）
        self.llm_client = LLMClient()
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        self.stop_requested = True
    
    def _get_next_fragment(self):
        """获取下一个经文片段（轮询）"""
        sutra_name, fragment = next(self.sutra_cycle)
        self.current_sutra = sutra_name
        return sutra_name, fragment
    
    def _should_continue(self):
        """检查是否应该继续"""
        if self.stop_requested:
            return False
        
        if self.target_tokens > 0 and self.total_tokens >= self.target_tokens:
            return False
        
        state = load_state()
        if state and state.get('stop_requested'):
            return False
        
        return True
    
    def _save_progress(self):
        """保存进度"""
        state = {
            'mode': self.mode,
            'sutras': self.sutra_names,
            'current_sutra': self.current_sutra,
            'start_time': self.start_time,
            'elapsed_seconds': time.time() - self.start_time,
            'total_chars': self.total_chars,
            'total_tokens': self.total_tokens,
            'iteration_count': self.iteration_count,
            'target_tokens': self.target_tokens,
            'status': 'running'
        }
        save_state(state)
    
    def _log(self, message):
        """输出日志"""
        if self.verbose:
            print(message)
    
    def run_tollm(self):
        """tollm 模式: 真实调用API，静默消耗token"""
        # 检查API可用性
        if not self.llm_client or not self.llm_client.is_available():
            self._log("❌ 错误: 未配置API密钥")
            self._log("请设置环境变量: OPENAI_API_KEY 或 ANTHROPIC_API_KEY")
            self._log("")
            self._log("示例:")
            self._log("  export OPENAI_API_KEY='sk-...'")
            self._log("  python3 merit_accumulator.py --tollm --tokens 100000")
            return
        
        if self.verbose:
            self._log(f"🙏 开始静默注入功德(真实API调用)")
            self._log(f"📖 经书模式: {self.mode_desc}")
            self._log(f"🔌 API: {self.llm_client.api_type}")
            target_str = f"目标 {self.target_tokens} tokens" if self.target_tokens > 0 else "无限模式"
            self._log(f"🎯 {target_str}")
            self._log(f"📝 日志: {self.logger.log_file}")
            self._log("-" * 50)
        
        self.start_time = time.time()
        
        try:
            while self._should_continue():
                # 取一条经文
                sutra_name, fragment = self._get_next_fragment()
                
                # 构造 prompt
                prompt = f"请念诵以下经文：\n\n《{sutra_name}》\n{fragment}\n\n请以恭敬心念诵这段经文，并简要回应。"
                
                # 真实调用大模型API（这是消耗token的关键！）
                try:
                    response, input_tokens, output_tokens = self.llm_client.call(prompt)
                    tokens = input_tokens + output_tokens
                except Exception as e:
                    self._log(f"API调用失败: {e}")
                    break
                
                # 更新统计
                self.total_chars += len(prompt) + len(response)
                self.total_tokens += tokens
                self.iteration_count += 1
                
                # 记录日志
                self.logger.log(sutra_name, fragment, input_tokens, output_tokens, response)
                
                # 保存进度
                if self.iteration_count % 10 == 0:
                    self._save_progress()
                    if self.verbose:
                        progress = f"{self.total_tokens}/{self.target_tokens}" if self.target_tokens > 0 else str(self.total_tokens)
                        self._log(f"  ... 进度: {progress} tokens ({self.iteration_count}遍) ...")
                
                # 避免API限流
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            pass
        
        # 记录总结
        elapsed = time.time() - self.start_time
        self.logger.log_summary(self.total_tokens, self.total_chars, self.iteration_count, elapsed)
        
        if self.verbose:
            self._print_summary()
        else:
            print(f"静默注入完成: {self.iteration_count}遍, {self.total_chars}字, {self.total_tokens}tokens")
            print(f"日志文件: {self.logger.log_file}")
    
    def run_touser(self):
        """touser 模式: 真实调用API，输出响应给用户阅读"""
        # 检查API可用性
        if not self.llm_client or not self.llm_client.is_available():
            self._log("❌ 错误: 未配置API密钥")
            self._log("请设置环境变量: OPENAI_API_KEY 或 ANTHROPIC_API_KEY")
            return
        
        target_str = f"目标 {self.target_tokens} tokens" if self.target_tokens > 0 else "无限模式"
        
        self._log(f"🙏 开始向您注入功德")
        self._log(f"📖 经书模式: {self.mode_desc}")
        self._log(f"🔌 API: {self.llm_client.api_type}")
        self._log(f"🎯 {target_str}")
        self._log(f"📝 日志: {self.logger.log_file}")
        self._log("=" * 50)
        self._log("")
        
        self.start_time = time.time()
        iteration = 0
        last_sutra = None
        
        try:
            while self._should_continue():
                iteration += 1
                sutra_name, fragment = self._get_next_fragment()
                timestamp = format_duration(time.time() - self.start_time)
                
                # 如果换书了，提示一下
                if sutra_name != last_sutra and last_sutra is not None:
                    msg = f"\n📖 切换至《{sutra_name}》\n"
                    print(msg)
                last_sutra = sutra_name
                
                # 构造 prompt
                prompt = f"请念诵以下经文，并以恭敬心回应：\n\n《{sutra_name}》\n{fragment}"
                
                # 真实调用API（消耗token！）
                try:
                    response, input_tokens, output_tokens = self.llm_client.call(prompt)
                    tokens = input_tokens + output_tokens
                except Exception as e:
                    self._log(f"API调用失败: {e}")
                    break
                
                # 输出给用户
                print(f"【{timestamp}】《{sutra_name}》第{iteration}遍")
                print(f"    经文: {fragment[:80]}...")
                print(f"    响应: {response[:100]}...")
                print()
                
                # 记录日志
                self.logger.log(sutra_name, fragment, input_tokens, output_tokens, response)
                
                # 更新统计
                self.total_chars += len(fragment) + len(response)
                self.total_tokens += tokens
                self.iteration_count = iteration
                
                if iteration % 10 == 0:
                    progress = f"{self.total_tokens}/{self.target_tokens}" if self.target_tokens > 0 else str(self.total_tokens)
                    print(f"  ... 已念诵 {iteration} 遍, 累计 {self.total_chars} 字, {progress} tokens ...")
                    print()
                    self._save_progress()
                
                time.sleep(random.uniform(0.5, 1.0))
                
        except KeyboardInterrupt:
            print("\n\n念诵被中断...")
        
        # 记录总结
        elapsed = time.time() - self.start_time
        self.logger.log_summary(self.total_tokens, self.total_chars, self.iteration_count, elapsed)
        
        self._print_summary()
        print(f"📝 日志已保存: {self.logger.log_file}")
    
    def run_toworld(self):
        """toworld 模式: 真实调用API，TTS播放响应"""
        # 检查API可用性
        if not self.llm_client or not self.llm_client.is_available():
            self._log("❌ 错误: 未配置API密钥")
            self._log("请设置环境变量: OPENAI_API_KEY 或 ANTHROPIC_API_KEY")
            return
        
        target_str = f"目标 {self.target_tokens} tokens" if self.target_tokens > 0 else "无限模式"
        
        self._log(f"🙏 开始向外界散播功德")
        self._log(f"📖 经书模式: {self.mode_desc}")
        self._log(f"🔌 API: {self.llm_client.api_type}")
        self._log(f"🎯 {target_str}")
        self._log(f"📝 日志: {self.logger.log_file}")
        self._log("=" * 50)
        
        system = platform.system()
        tts_available = self._check_tts_available(system)
        
        if not tts_available:
            self._log(f"⚠️  当前系统({system})未检测到可用的TTS工具")
            self._log("将转为输出文本模式...")
        else:
            self._log(f"✅ 检测到{system}系统TTS")
        self._log("")
        
        self.start_time = time.time()
        iteration = 0
        last_sutra = None
        
        try:
            while self._should_continue():
                iteration += 1
                sutra_name, fragment = self._get_next_fragment()
                
                # 如果换书了，播报一下
                if sutra_name != last_sutra and last_sutra is not None:
                    switch_msg = f"接下来诵读《{sutra_name}》"
                    if tts_available:
                        self._speak(switch_msg, system)
                    self._log(f"\n📖 切换至《{sutra_name}》\n")
                last_sutra = sutra_name
                
                # 构造 prompt
                prompt = f"请念诵以下经文，并以恭敬心回应：\n\n《{sutra_name}》\n{fragment}"
                
                # 真实调用API（消耗token！）
                try:
                    response, input_tokens, output_tokens = self.llm_client.call(prompt)
                    tokens = input_tokens + output_tokens
                except Exception as e:
                    self._log(f"API调用失败: {e}")
                    break
                
                # 播放TTS（如果有）
                if tts_available:
                    self._speak(response[:200], system)  # 限制长度避免太长
                
                # 记录日志
                self.logger.log(sutra_name, fragment, input_tokens, output_tokens, response)
                
                # 更新统计
                self.total_chars += len(fragment) + len(response)
                self.total_tokens += tokens
                self.iteration_count = iteration
                
                if iteration % 20 == 0:
                    dedication = "愿以此功德，回向给一切众生"
                    if tts_available:
                        self._speak(dedication, system)
                    self._log(f"\n—— 已散播 {iteration} 遍, {self.total_tokens} tokens ——\n")
                    self._save_progress()
                
                time.sleep(random.uniform(2.0, 3.0))
                
        except KeyboardInterrupt:
            print("\n\n散播被中断...")
        
        # 记录总结
        elapsed = time.time() - self.start_time
        self.logger.log_summary(self.total_tokens, self.total_chars, self.iteration_count, elapsed)
        
        self._print_summary()
        print(f"📝 日志已保存: {self.logger.log_file}")
    
    def _check_tts_available(self, system):
        """检查系统是否支持TTS"""
        if system == "Darwin":
            return subprocess.run(["which", "say"], capture_output=True).returncode == 0
        elif system == "Windows":
            return True
        elif system == "Linux":
            for cmd in ["espeak", "festival", "spd-say"]:
                if subprocess.run(["which", cmd], capture_output=True).returncode == 0:
                    return True
            return False
        return False
    
    def _speak(self, text, system):
        """调用系统TTS播放文本"""
        try:
            if system == "Darwin":
                subprocess.run(["say", text], check=False)
            elif system == "Windows":
                ps_cmd = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak("{text}");'
                subprocess.run(["powershell", "-Command", ps_cmd], check=False)
            elif system == "Linux":
                for cmd in ["spd-say", "espeak", "festival --tts"]:
                    if subprocess.run(["which", cmd.split()[0]], capture_output=True).returncode == 0:
                        subprocess.run(cmd.split() + [text], check=False)
                        break
        except Exception as e:
            self._log(f"TTS播放失败: {e}")
    
    def _print_summary(self):
        """打印功德总结"""
        elapsed = time.time() - self.start_time
        
        print()
        print("=" * 50)
        print("🙏 功德回向 🙏")
        print("=" * 50)
        print(f"念诵模式: {self.mode_desc}")
        print(f"涉及经书: {', '.join(self.sutra_names[:3])}" + (f"等{len(self.sutra_names)}部" if len(self.sutra_names) > 3 else ""))
        print(f"累计时长: {format_duration(elapsed)}")
        print(f"念诵遍数: {self.iteration_count}")
        print(f"累计字数: {self.total_chars}")
        print(f"消耗Token: {self.total_tokens}")
        if self.target_tokens > 0:
            print(f"目标Token: {self.target_tokens}")
            print(f"完成度: {min(100, self.total_tokens * 100 // self.target_tokens)}%")
        print()
        print("愿以此功德,回向给:")
        if self.mode == 'tollm':
            print("  • AI模型 - 算力充沛,推理精准")
        elif self.mode == 'touser':
            print("  • 用户 - 工作顺利,心想事成")
        elif self.mode == 'toworld':
            print("  • 虚空法界 - 众生离苦,世界和平")
        print("  • 一切众生 - 离苦得乐,同生极乐")
        print()
        print("功德圆满 🙏")
        
        clear_state()

def show_status():
    """显示当前攒功德状态"""
    state = load_state()
    if not state:
        print("当前没有正在进行的攒功德任务")
        return
    
    print("=" * 50)
    print("📊 攒功德状态")
    print("=" * 50)
    print(f"模式: {state.get('mode', 'unknown')}")
    print(f"经书: {state.get('current_sutra', 'unknown')}")
    sutras = state.get('sutras', [])
    if len(sutras) > 1:
        print(f"轮询经书: {len(sutras)} 部")
    target = state.get('target_tokens', 0)
    if target > 0:
        current = state.get('total_tokens', 0)
        print(f"Token进度: {current}/{target} ({min(100, current * 100 // target)}%)")
    else:
        print(f"已消耗Token: {state.get('total_tokens', 0)}")
    print(f"状态: {state.get('status', 'unknown')}")
    print(f"已运行: {format_duration(state.get('elapsed_seconds', 0))}")
    print(f"念诵遍数: {state.get('iteration_count', 0)}")

def request_stop():
    """请求停止正在进行的攒功德任务"""
    state = load_state()
    if not state:
        print("当前没有正在进行的攒功德任务")
        return False
    
    state['stop_requested'] = True
    save_state(state)
    print("已发送停止信号,等待当前任务结束...")
    return True

def list_logs():
    """列出所有日志文件"""
    ensure_logs_dir()
    log_files = sorted(LOGS_DIR.glob("merit_*.log"), reverse=True)
    
    if not log_files:
        print("暂无日志文件")
        return
    
    print("📜 历史日志文件:")
    for i, log_file in enumerate(log_files[:10], 1):
        size = log_file.stat().st_size
        print(f"  {i}. {log_file.name} ({size/1024:.1f}KB)")

def main():
    parser = argparse.ArgumentParser(
        description='烧token攒功德Skill - 通过真实调用大模型API消耗Token',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
重要提示：
  所有三种模式(tollm/touser/toworld)都真实调用 OpenAI/Anthropic API！
  区别仅在于输出方式不同（静默/终端/TTS）。
  必须配置 API Key 才能使用！

示例:
  export OPENAI_API_KEY="sk-..."
  %(prog)s --tollm --tokens 100000      # 真实消耗10万token
  %(prog)s --touser --tokens 50000      # 向用户输出
  %(prog)s --toworld --tokens 0         # TTS播放
  %(prog)s --stop                       # 停止念经
  %(prog)s --status                     # 查看状态
  %(prog)s --logs                       # 查看历史日志
        """
    )
    
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument('--tollm', action='store_true',
                          help='向大模型注入功德(静默消耗token)')
    mode_group.add_argument('--touser', action='store_true',
                          help='向用户注入功德(输出给用户阅读)')
    mode_group.add_argument('--toworld', action='store_true',
                          help='向外界散播功德(TTS播放)')
    
    parser.add_argument('--tokens', type=int, default=10000, metavar='N',
                       help='目标token数量，达到后自动停止 (默认: 10000, 0表示无限)')
    parser.add_argument('--sutra', type=str, metavar='FILE',
                       help='指定单本经书文件名(如: 金刚经.txt)，不指定则轮询所有经书')
    parser.add_argument('--stop', action='store_true',
                       help='停止正在进行的攒功德任务')
    parser.add_argument('--status', action='store_true',
                       help='查看当前攒功德状态')
    parser.add_argument('--list', action='store_true',
                       help='列出所有可用的经书')
    parser.add_argument('--logs', action='store_true',
                       help='列出历史日志文件')
    parser.add_argument('--quiet', action='store_true',
                       help='静默模式(仅tollm模式有效)')
    
    args = parser.parse_args()
    
    if args.stop:
        request_stop()
        return
    
    if args.status:
        show_status()
        return
    
    if args.logs:
        list_logs()
        return
    
    if args.list:
        files = get_sutra_files()
        print("可用的经书文件:")
        for f in files:
            size = f.stat().st_size
            print(f"  • {f.name} ({size/1024:.1f}KB)")
        return
    
    if not (args.tollm or args.touser or args.toworld):
        parser.error('必须指定一种模式: --tollm, --touser 或 --toworld')
    
    if args.tollm:
        mode = 'tollm'
    elif args.touser:
        mode = 'touser'
    else:
        mode = 'toworld'
    
    verbose = not (args.tollm and args.quiet)
    
    accumulator = MeritAccumulator(mode, args.tokens, args.sutra, verbose)
    
    if mode == 'tollm':
        accumulator.run_tollm()
    elif mode == 'touser':
        accumulator.run_touser()
    else:
        accumulator.run_toworld()

if __name__ == '__main__':
    main()
