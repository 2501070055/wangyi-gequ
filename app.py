import os

from flask import Flask, render_template, url_for, request as req
from bs4 import BeautifulSoup
from urllib import request
import re

from werkzeug.utils import secure_filename, redirect

app = Flask(__name__)


class Music(object):
    def __init__(self, baseurl):
        head = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"  # 用户请求头
        }
        self.baseurl = baseurl  # 初始化请求地址
        self.headers = head  # 初始化header头

    def main(self):
        html = self.html()
        bs4 = self.analysis(html)
        name1 = self.matching(bs4)
        self.save(name1)

    def html(self):
        req = request.Request(url=self.baseurl, headers=self.headers)
        response = request.urlopen(req)
        html_page = response.read().decode("utf-8")
        return html_page

    def analysis(self, html):
        soup = BeautifulSoup(html, "html.parser")  # 把网页解析为BeautifulSoup对象
        bs4 = soup.find_all("textarea", {"id": "song-list-pre-data"})
        bs4 = str(bs4)
        return bs4

    def matching(self, bs4):
        rule0 = re.compile(r'"name":"(.*?)","tns":[],"alias":[]')
        name0 = re.findall(rule0, bs4)
        # print(name0)
        str = ""
        for i in name0:
            str = str + "," + i
        str = str.replace("\xa0", "")
        rule1 = re.compile(r'jpg,(.*?),(.*?)","id":(\d*)')
        name1 = re.findall(rule1, str)
        return name1

    def save(self, name1):
        for j in name1:
            print("正在写入：" + j[1] + " - " + j[0] + "...")
            # song_str = "http://music.163.com/song/media/outer/url?id=" + j[2] + ','
            song_str = j[2] + '+'
            music_str = j[1] + '+'
            author_str = j[0] + '+'
            # time.sleep(0.1)
            with open('song.txt', "a+", encoding='utf-8') as f:
                list_file = str(song_str)
                f.write(list_file)
            f.close()
            with open('music.txt', "a+", encoding='utf-8') as f:
                list_file = str(music_str)
                f.write(list_file)
            f.close()
            with open('author.txt', "a+", encoding='utf-8') as f:
                list_file = str(author_str)
                f.write(list_file)
            f.close()
        return


@app.route('/')
def hello_world():
    base_url = "https://music.163.com/discover/toplist?id=3778678"  # 要爬取的热歌榜链接
    if os.path.exists('author.txt' and 'song.txt' and 'music.txt'):
        try:
            os.remove("author.txt")
            os.remove("song.txt")
            os.remove("music.txt")
        except Exception as e:
            return f"Error in deleting files: {e}"
    Music(base_url).main()
    with open('song.txt', "r", encoding='utf-8') as f:
        list_str = f.read()
    f.close()
    list_song = list_str.split('+')
    with open('author.txt', "r", encoding='utf-8') as f:
        list_str = f.read()
    f.close()
    list_author = list_str.split('+')
    with open('music.txt', "r", encoding='utf-8') as f:
        list_str = f.read()
    f.close()
    list_music = list_str.split('+')
    # print(list_music)
    print(len(list_song))
    form_list = []
    for i in range(len(list_song)-1):
        form_list.append({
            "song": list_song[i],
            "author": list_author[i],
            "music": list_music[i]
        })
    print(form_list)
    return render_template('index.html', form_list=form_list)


@app.route('/music')
def music():
    file_url = req.args.get("file_url")
    return render_template('music.html', file_url=file_url)


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if req.method == 'POST':
        f = req.files['file']
        file_url = secure_filename(f.filename)
        base_path = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(base_path, 'static/uploads', secure_filename(f.filename))
        f.save(upload_path)
        return redirect(url_for('music', file_url=file_url))
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
