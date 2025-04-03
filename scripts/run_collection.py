#!/usr/bin/env python
"""
运行数据收集脚本
收集 Stack Overflow 上的 NLP 问题和回答
"""

import os
from pathlib import Path
from loguru import logger

# 确保可以导入 src 模块
import sys

parent_dir = Path(__file__).parent.parent.absolute()
sys.path.append(str(parent_dir))

from src.data.collector import StackExchangeCollector


def main():
    """主函数"""
    # 确保目录结构
    data_dir = parent_dir / "data" / "raw"
    logs_dir = parent_dir / "logs"

    for directory in [data_dir, logs_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    # 设置日志
    logger.add(
        logs_dir / "collector_{time}.log",
        rotation="100 MB",
        level="INFO",
        format="{time} {level} {message}",
    )

    logger.info("开始收集 Stack Overflow 上的 NLP 问题和回答...")

    # 从环境变量获取配置
    from dotenv import load_dotenv

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

    # 检查是否要使用模拟数据
    use_mock_data = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

    logger.info(f"使用如下参数:")
    logger.info(f"站点: {site}")
    logger.info(f"每页问题数: {page_size}")
    logger.info(f"最大页数: {max_pages}")
    logger.info(f"标签: {tag}")
    logger.info(f"最少回答数: {min_answers}")
    logger.info(f"最低分数: {min_score}")
    logger.info(f"最大问题数: {max_count}")
    logger.info(f"使用模拟数据: {use_mock_data}")

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

        # 收集问题和回答
        logger.info(f"正在收集带有 [{tag}] 标签的问题和回答...")
        questions_with_answers = collector.collect_questions_with_answers(
            tag=tag, min_answers=min_answers, min_score=min_score, max_count=max_count
        )

        # 保存结果
        if questions_with_answers:
            output_file = data_dir / "nlp_questions_with_answers.json"
            collector.save_to_json(questions_with_answers, str(output_file))
            logger.success(
                f"收集完成! 共获取了 {len(questions_with_answers)} 个问题及其回答。"
            )
            logger.success(f"数据已保存到: {output_file}")
        else:
            logger.error("未能收集到任何数据")
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")


if __name__ == "__main__":
    main()
