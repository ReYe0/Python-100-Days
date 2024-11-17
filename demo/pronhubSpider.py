import os
import requests
import subprocess

if __name__ == '__main__':

    # M3U8 文件的 URL
    m3u8_url = 'https://ev-h.phncdn.com/hls/videos/202403/02/448962971/1080P_4000K_448962971.mp4/master.m3u8?validfrom=1729859241&validto=1729866441&ipa=146.56.174.194&hdl=-1&hash=1d8tRHUJ0Hb%2FeFokYoxVEKr4AM0%3D'

    # 下载 M3U8 文件
    response = requests.get(m3u8_url)
    m3u8_content = response.text

    # 解析 M3U8 文件，提取 .ts 文件的 URL
    ts_urls = []
    base_url = m3u8_url.rsplit('/', 1)[0]  # 获取基础 URL，用于拼接完整的 .ts URL

    for line in m3u8_content.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):  # 跳过注释行
            ts_url = f'{base_url}/{line}'
            ts_urls.append(ts_url)

    ts_urls_test = []
    test = requests.get(ts_url).text
    for line in test.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):  # 跳过注释行
            ts_url = f'{base_url}/{line}'
            ts_urls_test.append(ts_url)

    # 下载所有的 .ts 文件
    for i, ts_url in enumerate(ts_urls_test):
        ts_response = requests.get(ts_url)
        ts_filename = f'video_part_{i}.ts'
        with open(ts_filename, 'wb') as ts_file:
            ts_file.write(ts_response.content)
        print(f'Downloaded {i + 1}/{len(ts_urls_test)}: {ts_filename}')

    # 检查 .ts 文件是否存在
    ts_files = [f'video_part_{i}.ts' for i in range(len(ts_urls_test))]
    for file in ts_files:
        if not os.path.isfile(file):
            print(f'{file} does not exist.')
            exit()

    # 创建 ts_list.txt 文件，用于 ffmpeg 合并
    with open('ts_list.txt', 'w') as f:
        for file in ts_files:
            f.write(f"file '{file}'\n")

    # 使用 ffmpeg 合并视频片段
    try:
        subprocess.run(
            ['D:\\dev\\ffmpeg-7.0.2-full_build\\bin\\ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'ts_list.txt', '-c',
             'copy', 'output.mp4'], check=True)
        print('Video merging completed: output.mp4, 开始删除ts文件')
        with open('ts_list.txt', 'r') as f:
            for file in f:
                path = file.replace("file", "")
                path = path.strip().replace('\'', "")
                if os.path.exists(path):
                    os.remove(path)
        if os.path.exists('ts_list.txt'):
            os.remove('ts_list.txt')
        print("completed")
    except subprocess.CalledProcessError as e:
        print(f'Error during merging: {e}')
