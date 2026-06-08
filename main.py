"""
GitHub Trending / 具身智能资讯总结助手 - 主程序
整合数据抓取、AI分析、邮件推送三大模块
"""
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

from src.ai_analyzer import AI_PROVIDERS, create_analyzer
from src.crawler import GitHubTrendingCrawler
from src.email_sender import EmailSender
from src.news_crawler import EmbodiedAINewsCrawler, parse_sources


class BaseDigest:
    """总结助手基础类，负责环境变量、AI和邮件模块初始化。"""

    def __init__(self, provider: str = None):
        load_dotenv()

        self.provider = provider or os.getenv("AI_PROVIDER", "deepseek")
        self._validate_env()

        self.crawler = self._init_crawler()
        self.analyzer = self._init_analyzer()
        self.email_sender = self._init_email_sender()

    def _validate_env(self):
        provider_config = AI_PROVIDERS.get(self.provider, AI_PROVIDERS["deepseek"])
        api_key_env = provider_config["env_key"]
        required_vars = ["EMAIL_SENDER", "EMAIL_PASSWORD", "EMAIL_RECEIVER"]

        missing_vars = []
        if not os.getenv("AI_API_KEY") and not os.getenv(api_key_env):
            if self.provider == "deepseek" and os.getenv("DEEPSEEK_API_KEY"):
                pass
            else:
                missing_vars.append(api_key_env)

        missing_vars.extend([var for var in required_vars if not os.getenv(var)])

        if missing_vars:
            print("错误: 缺少以下环境变量配置:")
            for var in missing_vars:
                print(f"  - {var}")
            print("\n请在 .env 文件中配置这些变量（参考 .env.example）")

    def _init_crawler(self):
        raise NotImplementedError

    def _init_analyzer(self):
        provider_config = AI_PROVIDERS.get(self.provider)
        if not provider_config:
            print(f"错误: 不支持的 AI 提供商 '{self.provider}'")
            print(f"支持的列表: {list(AI_PROVIDERS.keys())}")
            sys.exit(1)

        env_key = provider_config["env_key"]
        api_key = os.getenv("AI_API_KEY") or os.getenv(env_key)

        if not api_key and self.provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")

        api_base = os.getenv("AI_API_BASE")
        if not api_base and self.provider == "deepseek":
            api_base = os.getenv("DEEPSEEK_API_BASE")

        print(f"初始化 AI 分析模块 (提供商: {self.provider})")

        if not api_key:
            print(f"警告: 未找到 {env_key} 或 AI_API_KEY，AI 分析可能失败")

        return create_analyzer(self.provider, api_key, api_base)

    def _init_email_sender(self) -> EmailSender:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("EMAIL_SENDER")
        sender_password = os.getenv("EMAIL_PASSWORD")

        print(f"初始化邮件发送模块 (SMTP: {smtp_server}:{smtp_port})")
        return EmailSender(smtp_server, smtp_port, sender_email, sender_password)

    def _print_report_preview(self, report: str, max_lines: int = 30):
        print("\n" + "=" * 60)
        print("报告预览（前{}行）".format(max_lines))
        print("=" * 60)

        lines = report.split("\n")
        preview_lines = lines[:max_lines]

        for line in preview_lines:
            try:
                print(line)
            except UnicodeEncodeError:
                print(line.encode("gbk", errors="ignore").decode("gbk"))

        if len(lines) > max_lines:
            print(f"\n... 还有 {len(lines) - max_lines} 行 ...")

        print("=" * 60 + "\n")


class TrendingDigest(BaseDigest):
    """GitHub Trending 总结助手。"""

    def _init_crawler(self) -> GitHubTrendingCrawler:
        language = os.getenv("TRENDING_LANGUAGE", "")
        since = os.getenv("TRENDING_SINCE", "daily")

        print(f"初始化爬虫模块 (语言: {language or '全部'}, 时间: {since})")
        return GitHubTrendingCrawler(language=language, since=since)

    def run(self, top_n: int = 25, send_email: bool = True):
        print("\n" + "=" * 60)
        print("GitHub Trending AI 总结助手")
        print("=" * 60 + "\n")

        try:
            print("[1/3] 抓取GitHub Trending数据...")
            repos = self.crawler.get_top_n(top_n)

            if not repos:
                print("错误: 未能抓取到任何项目数据")
                return

            print(f"成功抓取 {len(repos)} 个项目\n")

            print(f"[2/3] 调用 {self.provider} AI进行分析...")
            report = self.analyzer.generate_summary(repos, max_repos=top_n)
            print("AI分析完成\n")

            self._save_report(report)

            if send_email:
                print("[3/3] 发送邮件...")
                receiver = os.getenv("EMAIL_RECEIVER")
                success = self.email_sender.send_trending_report(receiver, report)

                if success:
                    print("\n[OK] 任务完成！报告已发送到邮箱")
                else:
                    print("\n[ERROR] 邮件发送失败，但报告已保存到本地")
            else:
                print("[3/3] 跳过邮件发送")
                print("\n[OK] 任务完成！报告已保存到本地")

            self._print_report_preview(report)

        except KeyboardInterrupt:
            print("\n\n用户中断执行")
            sys.exit(0)
        except Exception as e:
            print(f"\n[ERROR] 执行失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def _save_report(self, report: str):
        os.makedirs("reports", exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"reports/github_trending_{date_str}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"报告已保存: {filename}")


class EmbodiedNewsDigest(BaseDigest):
    """具身智能资讯总结助手。"""

    def _validate_env(self):
        provider_config = AI_PROVIDERS.get(self.provider, AI_PROVIDERS["deepseek"])
        api_key_env = provider_config["env_key"]

        if not os.getenv("AI_API_KEY") and not os.getenv(api_key_env):
            if not (self.provider == "deepseek" and os.getenv("DEEPSEEK_API_KEY")):
                print("警告: 缺少 AI 配置，完整 AI 分析可能失败:")
                print(f"  - {api_key_env}")

    def _init_crawler(self) -> EmbodiedAINewsCrawler:
        raw_sources = os.getenv("NEWS_SOURCES", "")
        raw_keywords = os.getenv("NEWS_KEYWORDS", "")

        sources = parse_sources(raw_sources) if raw_sources.strip() else None
        keywords = [keyword.strip() for keyword in raw_keywords.split(",") if keyword.strip()] if raw_keywords.strip() else None

        source_count = len(sources) if sources is not None else len(EmbodiedAINewsCrawler().sources)
        print(f"初始化具身智能资讯爬虫 (资讯源: {source_count} 个)")
        return EmbodiedAINewsCrawler(sources=sources, keywords=keywords)

    def run(self, top_n: int = 25, send_email: bool = True):
        print("\n" + "=" * 60)
        print("具身智能最新资讯总结助手")
        print("=" * 60 + "\n")

        try:
            print("[1/3] 抓取具身智能相关资讯...")
            items = self.crawler.fetch_latest(top_n)

            if not items:
                print("错误: 未能抓取到任何具身智能相关资讯")
                return

            print(f"成功抓取 {len(items)} 条资讯\n")

            print(f"[2/3] 调用 {self.provider} AI进行资讯分析...")
            report = self.analyzer.generate_news_summary(items, max_items=top_n)
            print("AI资讯分析完成\n")

            self._save_report(report)

            if send_email:
                print("[3/3] 发送邮件...")
                receiver = os.getenv("EMAIL_RECEIVER")
                date = datetime.now().strftime("%Y年%m月%d日")
                subject = f"具身智能最新资讯 - {date}"
                success = self.email_sender.send_text_email(receiver, subject, report)

                if success:
                    print("\n[OK] 任务完成！报告已发送到邮箱")
                else:
                    print("\n[ERROR] 邮件发送失败，但报告已保存到本地")
            else:
                print("[3/3] 跳过邮件发送")
                print("\n[OK] 任务完成！报告已保存到本地")

            self._print_report_preview(report)

        except KeyboardInterrupt:
            print("\n\n用户中断执行")
            sys.exit(0)
        except Exception as e:
            print(f"\n[ERROR] 执行失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def _save_report(self, report: str):
        os.makedirs("reports", exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"reports/embodied_ai_news_{date_str}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"报告已保存: {filename}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="GitHub Trending / 具身智能资讯总结助手")
    parser.add_argument(
        "--mode",
        choices=["github-trending", "embodied-news"],
        default="github-trending",
        help="运行模式: github-trending 或 embodied-news (默认: github-trending)",
    )
    parser.add_argument(
        "-n",
        "--top-n",
        type=int,
        default=25,
        help="抓取的项目或资讯数量 (默认: 25)",
    )
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="不发送邮件，仅生成报告",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="测试模式（只抓取10个项目或资讯）",
    )
    parser.add_argument(
        "-p",
        "--provider",
        type=str,
        choices=list(AI_PROVIDERS.keys()),
        help=f'AI 提供商: {", ".join(AI_PROVIDERS.keys())} (默认: deepseek)',
    )

    args = parser.parse_args()

    if args.test:
        args.top_n = 10
        print("*** 测试模式 ***\n")

    try:
        if args.mode == "embodied-news":
            digest = EmbodiedNewsDigest(provider=args.provider)
        else:
            digest = TrendingDigest(provider=args.provider)
        digest.run(top_n=args.top_n, send_email=not args.no_email)
    except Exception as e:
        print(f"程序启动失败: {e}")


if __name__ == "__main__":
    main()
