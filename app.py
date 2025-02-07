from flask import Flask, render_template, request, redirect, url_for, session

from config import GITLAB_API_URL, GITLAB_ACCESS_TOKEN, YEAR
from services.gitlab_service import GitLabService

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话加密

# 使用从配置中获取的用户名和密码
gitlab_service = GitLabService(GITLAB_API_URL, GITLAB_ACCESS_TOKEN, YEAR)


@app.route('/', methods=['GET', 'POST'])
def email_input():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        session['username'] = username
        session['email'] = email
        gitlab_service.username = username
        gitlab_service.mail = email  # 更新服务中的邮箱
        stats = gitlab_service.get_yearly_statistics()  # 获取统计数据
        session['stats'] = stats  # 存储统计数据
        return redirect(url_for('index'))
    return render_template('email_input.html')


@app.route('/index')
def index():
    stats = session.get('stats', {})
    return render_template('index.html', stats=stats)


@app.route('/user_info')
def user_info():
    stats = session.get('stats', {})
    return render_template('user_info.html', stats=stats)


@app.route('/summary')
def summary():
    stats = session.get('stats', {})
    return render_template('summary.html', stats=stats)


@app.route('/most_commits_day')
def most_commits_day():
    stats = session.get('stats', {})
    return render_template('most_commits_day.html', stats=stats, most_commits_day=stats.get('most_commits_day'))


@app.route('/commit_times')
def commit_times():
    stats = session.get('stats', {})
    return render_template('commit_times.html', stats=stats)


@app.route('/total_lines')
def total_lines():
    stats = session.get('stats', {})
    return render_template('total_lines.html', stats=stats, total_lines_added=stats.get('total_lines_added'),
                           total_lines_deleted=stats.get('total_lines_deleted'))


@app.route('/final')
def final():
    stats = session.get('stats', {})
    return render_template('final.html', stats=stats)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)  # 启用调试模式并修改端口
