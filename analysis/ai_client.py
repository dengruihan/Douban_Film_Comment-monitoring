"""
DeepSeek AI客户端封装
用于调用关键词筛选模型
"""

import requests
import logging
import os
import time

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

logger = logging.getLogger(__name__)

# API配置
API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("ZHIPU_AI_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


class DeepSeekAIClient:
    """DeepSeek AI客户端"""

    def __init__(self, api_key=None):
        self.api_key = api_key or API_KEY
        self.api_url = API_URL
        self.model = MODEL

    def chat(
        self, messages, max_tokens=1024, temperature=0.7, timeout=30, max_retries=2
    ):
        """
        调用DeepSeek聊天接口

        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            max_tokens: 最大token数
            temperature: 温度参数，控制随机性

        Returns:
            str: AI返回的文本内容
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    self.api_url, headers=headers, json=payload, timeout=timeout
                )

                if response.status_code == 200:
                    try:
                        result = response.json()
                    except Exception as e:
                        logger.error(
                            f"DeepSeek响应JSON解析失败: {e}; 原始响应前500字符: {response.text[:500]}"
                        )
                        return None

                    choices = (
                        result.get("choices") if isinstance(result, dict) else None
                    )
                    if not choices:
                        logger.error(
                            f"DeepSeek响应缺少choices字段: {str(result)[:500]}"
                        )
                        return None

                    first_choice = choices[0] if isinstance(choices[0], dict) else {}
                    message = (
                        first_choice.get("message", {})
                        if isinstance(first_choice, dict)
                        else {}
                    )
                    finish_reason = first_choice.get("finish_reason")
                    request_id = None
                    if isinstance(result, dict):
                        request_id = result.get("id")

                    content = (
                        message.get("content") if isinstance(message, dict) else None
                    )
                    reasoning_content = (
                        message.get("reasoning_content")
                        if isinstance(message, dict)
                        else None
                    )

                    if not content:
                        logger.error(
                            "DeepSeek响应content为空: "
                            f"finish_reason={finish_reason}, request_id={request_id}, "
                            f"reasoning_length={len(reasoning_content) if reasoning_content else 0}, "
                            f"响应前500字符: {str(result)[:500]}"
                        )

                        if reasoning_content:
                            logger.warning(
                                "检测到reasoning_content非空，使用reasoning_content作为降级返回"
                            )
                            return reasoning_content

                        return None

                    logger.info(f"DeepSeek调用成功，返回内容长度: {len(content)}")
                    logger.info(f"DeepSeek原始返回前300字符: {content[:300]}")
                    return content

                logger.error(
                    "DeepSeek调用失败，"
                    f"状态码: {response.status_code}, "
                    f"响应头x-request-id: {response.headers.get('x-request-id')}, "
                    f"响应: {response.text[:1000]}"
                )
                return None

            except requests.exceptions.Timeout as e:
                if attempt < max_retries:
                    wait_sec = attempt + 1
                    logger.warning(
                        f"DeepSeek调用超时(第 {attempt + 1}/{max_retries + 1} 次)，{wait_sec}s后重试: {e}"
                    )
                    time.sleep(wait_sec)
                    continue
                logger.error(f"DeepSeek调用异常: {e}")
                return None
            except Exception as e:
                logger.error(f"DeepSeek调用异常: {e}")
                return None

    def filter_keywords(self, word_list, top_n=50):
        """
        使用AI筛选关键词

        Args:
            word_list: 词频列表，格式 [(词, 频次), ...]
            top_n: 返回前N个关键词

        Returns:
            list: 筛选后的关键词列表
        """
        # 构建词频字符串
        words_str = ", ".join([f"{word}({count})" for word, count in word_list[:100]])

        prompt = f"""任务：从高频词中筛选关键词。

保留：
1) 形容词（表达评价、感受）
2) 与电影强相关的专有名词（人名、角色名、地名、意象）

删除：副词、代词、连词、语气词、通用动词、通用名词。

输入词表：{words_str}

输出要求：
- 仅输出关键词
- 用英文逗号分隔
- 不要解释、不要序号、不要换行
- 最多{top_n}个"""

        messages = [{"role": "user", "content": prompt}]

        result = self.chat(messages, max_tokens=1200, temperature=0.2)

        if result:
            # 解析返回的关键词
            normalized = (
                result.replace("```", "")
                .replace("关键词", "")
                .replace("：", ":")
                .replace("\n", ",")
                .replace("，", ",")
            )
            keywords = [w.strip() for w in normalized.split(",")]
            # 过滤空字符串和多余字符
            keywords = [
                k.strip("- *1234567890. ") for k in keywords if k and len(k) > 0
            ]
            keywords = [k for k in keywords if k]

            if not keywords:
                logger.warning(f"AI筛选解析后为空。原始返回前500字符: {result[:500]}")
                return []

            logger.info(f"AI筛选完成，返回 {len(keywords)} 个关键词")
            return keywords[:top_n]
        else:
            logger.warning("AI筛选失败，返回空列表")
            return []


# 创建全局客户端实例
ai_client = DeepSeekAIClient()


def ai_filter_keywords(word_list, top_n=50):
    """
    便捷函数：使用AI筛选关键词

    Args:
        word_list: 词频列表
        top_n: 返回前N个关键词

    Returns:
        list: 筛选后的关键词列表
    """
    return ai_client.filter_keywords(word_list, top_n)
