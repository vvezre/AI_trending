"""
GitHub Trending AI 总结助手 - 主程序
整合数据抓取、AI分析、邮件推送三大模块
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# 导入自定义模块
from src.crawler import GitHubTrendingCrawler
from src.ai_analyzer import DeepSeekAnalyzer
from src.email_sender import EmailSender


class TrendingDigest:
    """GitHub Trending 总结助手主类"""

    def __init__(self):
        """初始化，加载环境变量"""
        # 加载环境变量
        load_dotenv()

        # 验证必需的环境变量
        self._validate_env()

        # 初始化各个模块
        self.crawler = self._init_crawler()
        self.analyzer = self._init_analyzer()
        self.email_sender = self._init_email_sender()

    def _validate_env(self):
        """验证环境变量是否配置完整"""
        required_vars = [
            'DEEPSEEK_API_KEY',
            'EMAIL_SENDER',
            'EMAIL_PASSWORD',
            'EMAIL_RECEIVER'
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            print(f"错误: 缺少以下环境变量配置:")
            for var in missing_vars:
                print(f"  - {var}")
            print("\n请在 .env 文件中配置这些变量（参考 .env.example）")
            sys.exit(1)

    def _init_crawler(self) -> GitHubTrendingCrawler:
        """初始化爬虫模块"""
        language = os.getenv('TRENDING_LANGUAGE', '')
        since = os.getenv('TRENDING_SINCE', 'daily')

        print(f"初始化爬虫模块 (语言: {language or '全部'}, 时间: {since})")
        return GitHubTrendingCrawler(language=language, since=since)

    def _init_analyzer(self) -> DeepSeekAnalyzer:
        """初始化AI分析模块"""
        api_key = os.getenv('DEEPSEEK_API_KEY')
        api_base = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com')

        print("初始化DeepSeek AI分析模块")
        return DeepSeekAnalyzer(api_key=api_key, api_base=api_base)

    def _init_email_sender(self) -> EmailSender:
        """初始化邮件发送模块"""
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('EMAIL_SENDER')
        sender_password = os.getenv('EMAIL_PASSWORD')

        print(f"初始化邮件发送模块 (SMTP: {smtp_server}:{smtp_port})")
        return EmailSender(smtp_server, smtp_port, sender_email, sender_password)

    def run(self, top_n: int = 25, send_email: bool = True):
        """
        运行完整流程

        Args:
            top_n: 抓取的项目数量
            send_email: 是否发送邮件
        """
        print("\n" + "="*60)
        print("GitHub Trending AI 总结助手")
        print("="*60 + "\n")

        try:
            # 步骤1: 抓取GitHub Trending数据
            print("[1/3] 抓取GitHub Trending数据...")
            repos = self.crawler.get_top_n(top_n)

            if not repos:
                print("错误: 未能抓取到任何项目数据")
                return

            print(f"成功抓取 {len(repos)} 个项目\n")

            # 步骤2: AI分析
            print("[2/3] 调用DeepSeek AI进行分析...")
            report = self.analyzer.generate_summary(repos, max_repos=top_n)
            print("AI分析完成\n")

            # 保存报告到文件
            self._save_report(report)

            # 步骤3: 发送邮件
            if send_email:
                print("[3/3] 发送邮件...")
                receiver = os.getenv('EMAIL_RECEIVER')
                success = self.email_sender.send_trending_report(receiver, report)

                if success:
                    print("\n[OK] 任务完成！报告已发送到邮箱")
                else:
                    print("\n[ERROR] 邮件发送失败，但报告已保存到本地")
            else:
                print("[3/3] 跳过邮件发送")
                print("\n[OK] 任务完成！报告已保存到本地")

            # 打印报告预览
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
        """保存报告到本地文件"""
        # 创建reports目录
        os.makedirs('reports', exist_ok=True)

        # 生成文件名
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"reports/github_trending_{date_str}.md"

        # 保存文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"报告已保存: {filename}")

    def _print_report_preview(self, report: str, max_lines: int = 30):
        """打印报告预览"""
        print("\n" + "="*60)
        print("报告预览（前{}行）".format(max_lines))
        print("="*60)

        lines = report.split('\n')
        preview_lines = lines[:max_lines]

        for line in preview_lines:
            # 处理Windows控制台编码问题
            try:
                print(line)
            except UnicodeEncodeError:
                print(line.encode('gbk', errors='ignore').decode('gbk'))

        if len(lines) > max_lines:
            print(f"\n... 还有 {len(lines) - max_lines} 行 ...")

        print("="*60 + "\n")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='GitHub Trending AI 总结助手')
    parser.add_argument(
        '-n', '--top-n',
        type=int,
        default=25,
        help='抓取的项目数量 (默认: 25)'
    )
    parser.add_argument(
        '--no-email',
        action='store_true',
        help='不发送邮件，仅生成报告'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='测试模式（只抓取10个项目）'
    )

    args = parser.parse_args()

    # 测试模式
    if args.test:
        args.top_n = 10
        print("*** 测试模式 ***\n")

    # 创建并运行
    digest = TrendingDigest()
    digest.run(top_n=args.top_n, send_email=not args.no_email)


if __name__ == "__main__":
    main()
