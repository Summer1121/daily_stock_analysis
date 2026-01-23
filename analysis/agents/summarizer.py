# -*- coding: utf-8 -*-
"""
===================================
A股自选股智能分析系统 - 摘要 Agent (小模型)
===================================

职责：
1. 封装小模型（Gemini/OpenAI兼容API/Ollama）调用逻辑
2. 对原始新闻、公告等非结构化信息进行预处理和摘要
3. 降低大模型的 Token 负担
"""

import json
import logging
import time
from typing import Optional, Dict, Any, List

from tenacity import (
    retry_if_exception_type,
)

# 导入配置和提示词
from config import get_config, Config
from analysis.prompts import SUMMARIZER_AGENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class SummarizerAgent:
    """
    摘要 Agent (小模型)
    
    职责：
    对原始新闻、公告等非结构化信息进行预处理和摘要。
    """
    
    SYSTEM_PROMPT = SUMMARIZER_AGENT_SYSTEM_PROMPT # 从 prompts.py 导入
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化摘要 Agent
        
        支持 Gemini, OpenAI 兼容 API, Ollama
        """
        self.config = config if config else get_config()
        self._model_type = self.config.summarizer_model_type
        self._model_name = self.config.summarizer_model_name
        self._api_key = self.config.summarizer_api_key
        self._base_url = self.config.summarizer_base_url
        
        self._model = None
        self._llm_client = None # 用于 OpenAI 和 Ollama
        self._current_model_name = None  # 当前使用的模型名称
        
        self._initialize_llm_client()
        
        if not self.is_available():
            logger.warning("摘要 Agent 未配置或初始化失败，摘要功能将不可用")
    
    def _initialize_llm_client(self) -> None:
        """
        根据配置初始化 LLM 客户端
        """
        if self._model_type == 'gemini':
            self._init_gemini_client()
        elif self._model_type == 'openai':
            self._init_openai_client()
        elif self._model_type == 'ollama':
            self._init_ollama_client()
        else:
            logger.error(f"不支持的摘要 Agent 模型类型: {self._model_type}")
    
    def _init_gemini_client(self) -> None:
        """
        初始化 Gemini 客户端
        """
        if not self._api_key:
            self._api_key = self.config.gemini_api_key # 如果摘要agent没有独立key，则尝试使用主模型的key
        
        gemini_key_valid = self._api_key and not self._api_key.startswith('your_') and len(self._api_key) > 10
        if not gemini_key_valid:
            logger.debug("摘要 Agent 的 Gemini API Key 未配置或无效")
            return
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel(
                model_name=self._model_name,
                system_instruction=self.SYSTEM_PROMPT,
            )
            self._current_model_name = self._model_name
            logger.info(f"摘要 Agent 的 Gemini 模型初始化成功 (模型: {self._model_name})")
        except Exception as e:
            logger.error(f"摘要 Agent 的 Gemini 模型初始化失败: {e}")
            self._model = None
    
    def _init_openai_client(self) -> None:
        """
        初始化 OpenAI 兼容客户端
        """
        if not self._api_key:
            self._api_key = self.config.openai_api_key # 如果摘要agent没有独立key，则尝试使用主模型的key
        
        openai_key_valid = self._api_key and not self._api_key.startswith('your_') and len(self._api_key) > 10
        if not openai_key_valid:
            logger.debug("摘要 Agent 的 OpenAI API Key 未配置或无效")
            return
        
        try:
            from openai import OpenAI
            client_kwargs = {"api_key": self._api_key}
            if self._base_url and self._base_url.startswith('http'):
                client_kwargs["base_url"] = self._base_url
            
            self._llm_client = OpenAI(**client_kwargs)
            self._current_model_name = self._model_name
            logger.info(f"摘要 Agent 的 OpenAI 兼容客户端初始化成功 (base_url: {self._base_url}, model: {self._model_name})")
        except ImportError:
            logger.error("未安装 openai 库，请运行: pip install openai")
        except Exception as e:
            logger.error(f"摘要 Agent 的 OpenAI 兼容客户端初始化失败: {e}")

    def _init_ollama_client(self) -> None:
        """
        初始化 Ollama 客户端
        """
        try:
            # Ollama 通常通过 HTTP API 调用，这里假设使用 OpenAI 兼容接口
            # 或者直接使用 requests 库，这里为了简化，沿用 OpenAI 客户端的结构
            from openai import OpenAI
            client_kwargs = {"base_url": self._base_url if self._base_url else "http://localhost:11434/v1"}
            # Ollama 通常不需要 API Key，但如果需要，可以在这里传入
            # if self._api_key: client_kwargs["api_key"] = self._api_key
            
            self._llm_client = OpenAI(**client_kwargs)
            self._current_model_name = self._model_name
            logger.info(f"摘要 Agent 的 Ollama 客户端初始化成功 (base_url: {self._base_url}, model: {self._model_name})")
        except ImportError:
            logger.error("未安装 openai 库，请运行: pip install openai")
        except Exception as e:
            logger.error(f"摘要 Agent 的 Ollama 客户端初始化失败: {e}")
    
    def is_available(self) -> bool:
        """检查摘要 Agent 是否可用"""
        return self._model is not None or self._llm_client is not None
    
    def _call_gemini_api(self, prompt: str, generation_config: dict) -> str:
        """
        调用 Gemini API
        """
        config = self.config
        max_retries = config.gemini_max_retries # 复用主模型的重试配置
        base_delay = config.gemini_retry_delay
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = base_delay * (2 ** (attempt - 1))
                    delay = min(delay, 30) # 摘要模型重试延时可以短一些
                    logger.info(f"[SummarizerAgent-Gemini] 第 {attempt + 1} 次重试，等待 {delay:.1f} 秒...")
                    time.sleep(delay)
                
                response = self._model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    request_options={"timeout": 60} # 摘要任务超时短一些
                )
                
                if response and response.text:
                    return response.text
                else:
                    raise ValueError("Gemini 返回空响应")
                    
            except Exception as e:
                error_str = str(e)
                is_rate_limit = '429' in error_str or 'quota' in error_str.lower() or 'rate' in error_str.lower()
                logger.warning(f"[SummarizerAgent-Gemini] API 调用失败，第 {attempt + 1}/{max_retries} 次尝试: {error_str[:100]}")
                
                if attempt == max_retries - 1:
                    raise
        raise Exception("摘要 Agent 的 Gemini API 调用失败，已达最大重试次数")

    def _call_openai_ollama_api(self, prompt: str, generation_config: dict) -> str:
        """
        调用 OpenAI 兼容或 Ollama API
        """
        config = self.config
        max_retries = config.gemini_max_retries # 复用主模型的重试配置
        base_delay = config.gemini_retry_delay

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = base_delay * (2 ** (attempt - 1))
                    delay = min(delay, 30)
                    logger.info(f"[SummarizerAgent-OpenAI/Ollama] 第 {attempt + 1} 次重试，等待 {delay:.1f} 秒...")
                    time.sleep(delay)

                response = self._llm_client.chat.completions.create(
                    model=self._current_model_name,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=generation_config.get('temperature', 0.5), # 摘要可以更低温度
                    max_tokens=generation_config.get('max_output_tokens', 2048), # 摘要输出通常较短
                )

                if response and response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content
                else:
                    raise ValueError(f"{self._model_type} API 返回空响应")

            except Exception as e:
                error_str = str(e)
                is_rate_limit = '429' in error_str or 'rate' in error_str.lower() or 'quota' in error_str.lower()
                logger.warning(f"[SummarizerAgent-OpenAI/Ollama] API 调用失败，第 {attempt + 1}/{max_retries} 次尝试: {error_str[:100]}")
                
                if attempt == max_retries - 1:
                    raise
        raise Exception(f"摘要 Agent 的 {self._model_type} API 调用失败，已达最大重试次数")
    
    def summarize(self, raw_text: str, stock_code: str, stock_name: str) -> Optional[str]:
        """
        对原始文本进行摘要。

        Args:
            raw_text (str): 原始新闻或公告文本。
            stock_code (str): 股票代码。
            stock_name (str): 股票名称。

        Returns:
            Optional[str]: 摘要后的文本，如果失败则返回 None。
        """
        if not self.is_available():
            logger.warning(f"摘要 Agent 不可用，跳过 {stock_name}({stock_code}) 的新闻摘要。")
            return None
        
        # 请求前增加延时
        request_delay = self.config.gemini_request_delay # 复用主模型延时
        if request_delay > 0:
            logger.debug(f"[SummarizerAgent] 请求前等待 {request_delay:.1f} 秒...")
            time.sleep(request_delay)

        prompt = f"""请摘要以下关于 {stock_name}({stock_code}) 的新闻或公告。
重点提取：事件、影响（利好/利空/中性）、时间、相关方。
请用 200 字以内、条理清晰的中文进行总结。

```
{raw_text}
```
"""
        generation_config = {
            "temperature": 0.5,  # 摘要任务可以更低温度，更确定性
            "max_output_tokens": 2048, # 摘要输出长度
        }
        
        logger.info(f"========== 摘要 Agent 处理 {stock_name}({stock_code}) ==========")
        logger.info(f"[LLM配置] 模型: {self._current_model_name}")
        logger.info(f"[LLM配置] Prompt 长度: {len(prompt)} 字符")
        
        try:
            start_time = time.time()
            if self._model_type == 'gemini' and self._model:
                response_text = self._call_gemini_api(prompt, generation_config)
            elif (self._model_type == 'openai' or self._model_type == 'ollama') and self._llm_client:
                response_text = self._call_openai_ollama_api(prompt, generation_config)
            else:
                raise RuntimeError("摘要 Agent 未正确初始化或模型类型不支持。")
            
            elapsed = time.time() - start_time
            logger.info(f"[LLM返回] 摘要 Agent API 响应成功, 耗时 {elapsed:.2f}s, 响应长度 {len(response_text)} 字符")
            
            # 移除响应中的 markdown 代码块
            if response_text and '```' in response_text:
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            return response_text
        except Exception as e:
            logger.error(f"摘要 Agent 处理 {stock_name}({stock_code}) 失败: {e}")
            return None
