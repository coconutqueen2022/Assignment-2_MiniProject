import json
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
import os
import random
from loguru import logger
from stackapi import StackAPI, StackAPIError


class StackExchangeCollector:
    """Stack Exchange API 数据收集器"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        site: str = "stackoverflow",
        page_size: int = 100,
        max_pages: int = 5,
        rate_limit: int = 30,
        use_mock_data: bool = False,
    ):
        """
        初始化数据收集器

        Args:
            api_key: Stack Exchange API key（可选）
            site: 要收集数据的站点（默认为 stackoverflow）
            page_size: 每页的问题数量
            max_pages: 最大页数限制
            rate_limit: API 速率限制（每秒请求数）
            use_mock_data: 是否使用模拟数据
        """
        self.use_mock_data = use_mock_data
        self.page_size = page_size
        self.rate_limit = rate_limit
        
        if not use_mock_data:
            try:
                # 如果没有提供 API 密钥，则不使用密钥参数
                if api_key:
                    self.api = StackAPI(site, key=api_key)
                else:
                    logger.warning("未提供 API 密钥，将使用无密钥模式（请求限制为每天 300 次）")
                    self.api = StackAPI(site)
                    
                self.api.page_size = page_size
                self.api.max_pages = max_pages
            except StackAPIError as e:
                logger.error(f"初始化 StackAPI 失败: {str(e)}")
                raise
        else:
            logger.warning("使用模拟数据模式，不会发送实际的 API 请求")

    def _generate_mock_questions(self, count: int) -> List[Dict[str, Any]]:
        """生成模拟问题数据"""
        questions = []
        nlp_topics = ["tokenization", "word embeddings", "named entity recognition", 
                     "sentiment analysis", "text classification", "machine translation",
                     "question answering", "summarization", "speech recognition", "BERT"]
        
        for i in range(1, count + 1):
            # 随机选择2-4个话题作为标签
            tags = ["nlp"] + random.sample(nlp_topics, random.randint(1, 3))
            
            question = {
                "question_id": i,
                "title": f"如何在 NLP 项目中实现 {random.choice(nlp_topics)}?",
                "body": f"我正在尝试使用 Python 和 {random.choice(['NLTK', 'spaCy', 'HuggingFace', 'TensorFlow', 'PyTorch'])} 实现 {random.choice(nlp_topics)} 功能，但遇到了一些问题...",
                "score": random.randint(0, 50),
                "answer_count": random.randint(1, 5),
                "creation_date": int((datetime.now().timestamp() - random.randint(0, 30*24*60*60))),  # 过去30天内的随机时间
                "tags": tags,
                "accepted_answer_id": i * 100
            }
            questions.append(question)
            
        return questions

    def _generate_mock_answers(self, question_id: int) -> List[Dict[str, Any]]:
        """生成模拟回答数据"""
        answers = []
        answer_count = random.randint(1, 5)
        libraries = ["NLTK", "spaCy", "Transformers", "TensorFlow", "PyTorch", "Gensim"]
        
        for i in range(1, answer_count + 1):
            answer_id = question_id * 100 + i
            accepted = (i == 1)  # 第一个回答为采纳的回答
            
            answer = {
                "answer_id": answer_id,
                "body": f"你可以使用 {random.choice(libraries)} 库来解决这个问题。以下是示例代码:\n```python\nimport {random.choice(libraries).lower()}\n\n# 你的代码逻辑\n```\n希望这个回答对你有帮助！",
                "score": random.randint(0, 30),
                "is_accepted": accepted,
                "creation_date": int(datetime.now().timestamp()) - random.randint(0, 15*24*60*60),  # 过去15天内的随机时间
                "owner": {
                    "user_id": random.randint(1000, 9999),
                    "display_name": f"NLP专家{random.randint(1, 100)}"
                }
            }
            answers.append(answer)
            
        return answers

    def collect_questions(
        self,
        tag: str,
        min_answers: int = 1,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        min_score: int = 0,
        max_count: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        收集带有指定标签的问题

        Args:
            tag: 问题标签
            min_answers: 最少答案数
            from_date: 开始日期
            to_date: 结束日期
            min_score: 最低分数
            max_count: 最大问题数量

        Returns:
            问题列表
        """
        if self.use_mock_data:
            logger.info(f"使用模拟数据生成 {max_count} 个带有 [{tag}] 标签的问题...")
            questions = self._generate_mock_questions(max_count)
            logger.info(f"已生成 {len(questions)} 个模拟问题")
            return questions
            
        # 设置请求参数
        params = {
            'tagged': tag,
            'sort': 'creation',
            'order': 'desc',
            'min': min_answers,
            'min_score': min_score,
            'filter': '!-*jbN0CeyLXX',  # 包含问题体和其他详细信息的过滤器
        }

        if from_date:
            params['fromdate'] = int(from_date.timestamp())
        if to_date:
            params['todate'] = int(to_date.timestamp())

        # 设置收集数量限制
        self.api.max_pages = (max_count + self.api.page_size - 1) // self.api.page_size

        try:
            # 获取问题
            logger.info(f"开始收集带有 [{tag}] 标签的问题...")
            questions_response = self.api.fetch('questions', **params)
            questions = questions_response['items']
            
            logger.info(f"已收集 {len(questions)} 个问题")

            # 如果结果超过预期，截断列表
            if len(questions) > max_count:
                questions = questions[:max_count]
                
            return questions
        except StackAPIError as e:
            logger.error(f"收集问题时出错: {str(e)}")
            return []

    def collect_answers_for_question(self, question_id: int) -> List[Dict[str, Any]]:
        """
        收集指定问题的回答

        Args:
            question_id: 问题ID

        Returns:
            回答列表
        """
        if self.use_mock_data:
            logger.info(f"为问题 ID {question_id} 生成模拟回答...")
            answers = self._generate_mock_answers(question_id)
            logger.info(f"已生成 {len(answers)} 个模拟回答")
            return answers
            
        # 添加一个小延迟避免频繁请求
        time.sleep(1 / self.rate_limit)
        
        # 设置过滤器以获取完整的回答内容
        params = {
            'filter': '!-*jbN0CeYX4I',  # 包含回答体和其他详细信息的过滤器
            'sort': 'votes',
            'order': 'desc',
        }
        
        try:
            logger.info(f"收集问题 ID {question_id} 的回答...")
            answers_response = self.api.fetch(f'questions/{question_id}/answers', **params)
            return answers_response['items']
        except StackAPIError as e:
            logger.error(f"获取问题 {question_id} 的回答时出错: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            return []

    def collect_questions_with_answers(
        self,
        tag: str,
        min_answers: int = 1,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        min_score: int = 0,
        max_count: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        收集带有指定标签的问题及其回答

        Args:
            tag: 问题标签
            min_answers: 最少答案数
            from_date: 开始日期
            to_date: 结束日期
            min_score: 最低分数
            max_count: 最大问题数量

        Returns:
            包含回答的问题列表
        """
        # 先获取问题
        questions = self.collect_questions(
            tag, min_answers, from_date, to_date, min_score, max_count
        )
        
        if not questions:
            logger.warning("没有找到符合条件的问题")
            return []
            
        total_questions = len(questions)
        questions_with_answers = []
        
        # 为每个问题获取回答
        for i, question in enumerate(questions):
            question_id = question['question_id']
            
            # 获取回答
            answers = self.collect_answers_for_question(question_id)
            question['answers'] = answers
            
            questions_with_answers.append(question)
            
            logger.info(f"进度: {i+1}/{total_questions} - 问题 ID {question_id} 有 {len(answers)} 个回答")
            
            # 每收集10个问题保存一次，避免数据丢失
            if (i + 1) % 10 == 0 or i == total_questions - 1:
                self.save_to_json(
                    questions_with_answers, f"data/raw/nlp_questions_temp_{i+1}.json"
                )
        
        return questions_with_answers

    def save_to_json(self, data: List[Dict[str, Any]], file_path: str) -> None:
        """
        将数据保存为 JSON 文件

        Args:
            data: 要保存的数据
            file_path: 文件路径
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存至 {file_path}")


def main():
    """主函数"""
    # 从环境变量获取 API key
    import os
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv()
    
    # 尝试获取 API 密钥，如果不存在则设置为 None
    api_key = os.getenv("STACK_EXCHANGE_API_KEY")
    if api_key == "your_api_key_here":
        api_key = None
    
    site = os.getenv("STACK_EXCHANGE_SITE", "stackoverflow")
    page_size = int(os.getenv("STACK_EXCHANGE_BATCH_SIZE", 100))
    max_pages = int(os.getenv("STACK_EXCHANGE_MAX_PAGES", 5))
    rate_limit = int(os.getenv("STACK_EXCHANGE_RATE_LIMIT", 30))
    
    tag = os.getenv("TAG", "nlp")
    min_answers = int(os.getenv("MIN_ANSWERS", 1))
    min_score = int(os.getenv("MIN_SCORE", 0))
    max_count = int(os.getenv("MAX_COUNT", 10))
    
    # 检查是否要使用模拟数据（环境变量或API受限时）
    use_mock_data = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

    try:
        # 初始化收集器
        collector = StackExchangeCollector(
            api_key=api_key,
            site=site,
            page_size=page_size,
            max_pages=max_pages,
            rate_limit=rate_limit,
            use_mock_data=use_mock_data,
        )

        # 收集带有 [nlp] 标签的问题及其回答
        questions_with_answers = collector.collect_questions_with_answers(
            tag=tag, 
            min_answers=min_answers, 
            min_score=min_score,
            max_count=max_count
        )

        # 保存数据为 JSON
        if questions_with_answers:
            output_file = "data/raw/nlp_questions_with_answers.json"
            collector.save_to_json(questions_with_answers, output_file)
            logger.success(f"收集完成! 共获取了 {len(questions_with_answers)} 个问题及其回答。")
            logger.success(f"数据已保存到: {output_file}")
        else:
            logger.error("未能收集到任何数据")
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")


if __name__ == "__main__":
    # 配置日志
    logger.add("logs/collector_{time}.log", rotation="100 MB")
    
    main()
