"""
智谱AI客户端封装
用于调用GLM-4.7-flash模型进行关键词筛选
"""
import requests
import logging
import json

logger = logging.getLogger(__name__)

# API配置
API_KEY = "0f78e182d87b4873826b6193bc1bdf23.tNbBqoxMsMOq8ilC"
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-4-flash"


class ZhipuAIClient:
    """智谱AI客户端"""

    def __init__(self, api_key=None):
        self.api_key = api_key or API_KEY
        self.api_url = API_URL
        self.model = MODEL

    def chat(self, messages, max_tokens=1024, temperature=0.7):
        """
        调用智谱AI聊天接口

        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            max_tokens: 最大token数
            temperature: 温度参数，控制随机性

        Returns:
            str: AI返回的文本内容
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                logger.info(f"智谱AI调用成功，返回内容长度: {len(content)}")
                return content
            else:
                logger.error(f"智谱AI调用失败，状态码: {response.status_code}, 响应: {response.text}")
                return None

        except Exception as e:
            logger.error(f"智谱AI调用异常: {e}")
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

        prompt = f"""从以下高频词中筛选出能代表电影核心评价的关键词。

只保留以下两类词：
1. 形容词：描述感受、评价、特质，如感动、震撼、精彩、失望、无聊、经典、荒诞、压抑、细腻、浪漫
2. 特定名词：与该电影直接相关的人名、地名、专有名词、核心概念，如角色名、导演名、关键意象

严格删除以下类型（即使它们看似有用也必须删除）：
- 副词/虚词：终于、完全、其实、确实、好像、似乎、已经、依然、始终、根本、完全、实在、几乎
- 代词/量词：一种、这个、那种、一些、每个、所有、任何、自己、他人
- 通用动词：看、说、做、觉得、感觉、作为、成为、开始、希望、知道、认为、理解
- 通用名词：角色、电影、故事、人物、剧情、画面、内容、情节、场面、部分、方面、观众
- 连词/介词/语气词：因为、所以、虽然、但是、如果、还是、不过、然而、而且、那么

高频词列表（词(频次)）：
{words_str}

只返回筛选后的关键词，用逗号分隔，不要解释、序号、引号。返回{top_n}个最重要的词。
示例：感动,震撼,经典,压抑,救赎,安迪,监狱"""

        messages = [{"role": "user", "content": prompt}]

        result = self.chat(messages, max_tokens=512, temperature=0.3)

        if result:
            # 解析返回的关键词
            keywords = [w.strip() for w in result.replace('，', ',').split(',')]
            # 过滤空字符串和多余字符
            keywords = [k for k in keywords if k and len(k) > 0]
            logger.info(f"AI筛选完成，返回 {len(keywords)} 个关键词")
            return keywords[:top_n]
        else:
            logger.warning("AI筛选失败，返回空列表")
            return []


# 创建全局客户端实例
ai_client = ZhipuAIClient()


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
