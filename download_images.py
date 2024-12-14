import pandas as pd
import requests
import os

def download_image(url, save_path):
    """下载图片并保存到指定路径"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"下载成功: {save_path}")
    except Exception as e:
        print(f"下载失败: {url}, 错误信息: {str(e)}")

def filter_and_download_images(input_file, output_dir):
    """筛选数据并下载封面图片"""
    # 读取 Excel 文件
    df = pd.read_excel(input_file)
    
    # 筛选粉丝数小于 1000 且互动量大于 100 的数据
    filtered_df = df[(df['粉丝数'] < 1000) & (df['互动量'] > 100)]
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 下载封面图片
    for index, row in filtered_df.iterrows():
        image_url = row['封面地址']
        if pd.notna(image_url):  # 确保 URL 不为空
            # 生成保存路径
            image_name = f"cover_image_{index + 1}.jpg"  # 可以根据需要修改��名规则
            save_path = os.path.join(output_dir, image_name)
            download_image(image_url, save_path)

if __name__ == '__main__':
    input_file = 'uploads/processed_notes.xlsx'  # 输入文件路径
    output_dir = 'downloads'  # 输出目录
    filter_and_download_images(input_file, output_dir) 