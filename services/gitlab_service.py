from collections import defaultdict
from datetime import datetime, time

import requests
from dateutil import parser


class GitLabService:
    def __init__(self, api_url, access_token, year):
        self.api_url = api_url
        self.headers = {
            "Private-Token": access_token
        }
        self.year = year
        self.username = None  # 初始化时不设置用户名
        self.mail = None  # 初始化时不设置邮箱
        self.user_info = None

    def get_user_info(self):
        # 通过用户名获取用户 ID
        response = requests.get(f"{self.api_url}/users?username={self.username}", headers=self.headers)
        users = response.json()
        if users:
            return users[0]
        else:
            raise ValueError("User not found")

    def get_projects_by_time(self):
        # 获取指定时间范围内的项目
        projects = []
        page = 1
        while True:
            response = requests.get(
                f"{self.api_url}/projects?created_after={self.year}-01-01T00:00:00Z&created_before={self.year}-12-31T23:59:59Z&page={page}",
                headers=self.headers)
            page_projects = response.json()
            if not page_projects:
                break
            projects.extend(page_projects)
            page += 1
        return projects

    def get_project_commits(self, project_id):
        response = requests.get(f"{self.api_url}/projects/{project_id}/repository/commits", headers=self.headers)
        commits = response.json()
        if not commits:
            return []
        # 使用 dateutil.parser 解析日期时间
        return [commit for commit in commits if parser.isoparse(commit['created_at']).year == self.year]

    def get_project_commits_min_max(self, project_id):
        commits = self.get_project_commits(project_id)
        if not commits:
            return None, None, 0

        earliest_commit = min(commits, key=lambda x: x['created_at'])
        latest_commit = max(commits, key=lambda x: x['created_at'])
        return earliest_commit['created_at'], latest_commit['created_at'], len(commits)

    def get_commit_changes(self, project_id, commit):
        response = requests.get(f"{self.api_url}/projects/{project_id}/repository/commits/{commit['id']}",
                                headers=self.headers)
        commit_details = response.json()

        lines_added = commit_details['stats']['additions']
        lines_deleted = commit_details['stats']['deletions']

        return lines_added, lines_deleted

    def get_yearly_statistics(self):
        self.user_info = self.get_user_info()

        created_at = parser.isoparse(self.user_info['created_at'])
        today = datetime.now()
        total_days = (today - created_at.replace(tzinfo=None)).days
        total_years = total_days // 365
        user_register_time = created_at.strftime('%Y年%m月%d日')

        projects = self.get_projects_by_time()
        this_year_projects = 0
        total_commits = 0
        total_lines_added = 0
        total_lines_deleted = 0
        commit_days = defaultdict(int)
        earliest_commit_time = None
        closest_to_midnight = None  # 最接近24点的时间
        latest_commit_time = None
        earliest_commit_date = None
        latest_commit_date = None
        closest_to_midnight_date = None
        most_commits_day_lines = 0

        for project in projects:
            flag = False
            commits = self.get_project_commits(project['id'])
            for commit in commits:
                if commit['author_email'] == self.mail:
                    flag = True
                    commit_date = parser.isoparse(commit['created_at']).date()
                    commit_days[commit_date] += 1
                    total_commits += 1
                    lines_added, lines_deleted = self.get_commit_changes(project['id'], commit)
                    total_lines_added += lines_added
                    total_lines_deleted += lines_deleted
                    if lines_added > most_commits_day_lines:
                        most_commits_day_lines = lines_added
                        most_commits_day = commit_date

                    commit_time = parser.isoparse(commit['created_at']).time()

                    # 定义凌晨五点的时间
                    cutoff_time = time(5, 0, 0)

                    # 处理最接近凌晨5点之前的时间
                    if commit_time < cutoff_time:
                        if latest_commit_time is None or commit_time > latest_commit_time:
                            latest_commit_time = commit_time
                            latest_commit_date = commit_date

                    # 处理最接近凌晨5点之后的时间
                    if commit_time >= cutoff_time:
                        if earliest_commit_time is None or commit_time < earliest_commit_time:
                            earliest_commit_time = commit_time
                            earliest_commit_date = commit_date

                    # 同时更新最接近午夜的时间
                    if closest_to_midnight is None or commit_time > closest_to_midnight:
                        closest_to_midnight = commit_time
                        closest_to_midnight_date = commit_date

            if flag:
                this_year_projects += 1

        # 如果没有找到凌晨5点之前的时间，使用最接近午夜的时间
        if latest_commit_time is None:
            latest_commit_time = closest_to_midnight
            latest_commit_date = closest_to_midnight_date

        most_commits_day = most_commits_day.strftime('%m月%d日')
        earliest_commit_time = earliest_commit_time.strftime('%H:%M:%S')
        latest_commit_time = latest_commit_time.strftime('%H:%M:%S')
        earliest_commit_date = earliest_commit_date.strftime('%m月%d日')
        latest_commit_date = latest_commit_date.strftime('%m月%d日')

        keywords = {
            5:{
                "keyword": "小小贡献者",    
                "description": "你在过去一年中为团队增添的点滴，像是代码的星星，闪烁着你的努力和热情。"
            },
            10:{
                "keyword": "成长树",
                "description": "你像一棵茁壮成长的树，吸收了新知识和技能的养分，枝繁叶茂，迎接未来的阳光。"
            },
            20:{
                "keyword": "挑战勇士",
                "description": "面对工作中的各种挑战，你像勇士一样迎战，战胜了困难，收获了宝贵的经验和智慧。"
            },
            40:{
                "keyword": "协作小蜜蜂",
                "description": "在团队中，你像小蜜蜂一样忙碌，与大家一起合作，酿造出甜蜜的成果，分享快乐与成就。"
            },
            50:{
                "keyword": "目标小火箭",
                "description": "你设定的目标就像小火箭，冲向星空，努力实现每一个梦想，飞向更高的地方。"
            },
            60:{
                "keyword": "创意小魔法",
                "description": "在工作中，你施展创意的小魔法，提出新点子和解决方案，让任务变得更加有趣和高效。"
            },
            70:{
                "keyword": "未来小探险家",
                "description": "你对未来充满期待，像小探险家一样，准备探索新的领域，迎接未知的挑战和机遇。"
            },
            90:{
                "keyword": "梦想小画家",
                "description": "你像小画家一样，用代码绘制梦想的蓝图，每一行代码都是你心中的色彩。"
            }
        }

        
        keyword = None
        keyword_description = None

        for key in sorted(keywords.keys(), reverse=True):
            if total_commits >= key:
                item = keywords[key]
                keyword = item['keyword']
                keyword_description = item['description']
                break

        return {
            'year': self.year,
            'user': self.user_info,
            'total_days': total_days,
            'total_years': total_years,
            'user_register_time': user_register_time,
            'total_projects': len(projects),
            'this_year_projects': this_year_projects,
            'total_commits': total_commits,
            'total_lines_added': total_lines_added,
            'total_lines_deleted': total_lines_deleted,
            'most_commits_day': most_commits_day,
            'most_commits_day_lines': most_commits_day_lines,
            'earliest_commit_time': earliest_commit_time,
            'latest_commit_time': latest_commit_time,
            'earliest_commit_date': earliest_commit_date,
            'latest_commit_date': latest_commit_date,
            'keyword': keyword,
            'keyword_description': keyword_description
        }
