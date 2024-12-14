import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_headers(cookie):
    """设置请求头"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Cookie': cookie
    }
    return headers

def get_note_content(url, headers):
    """获取笔记内容和话题标签"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        detail = soup.find(id='detail-desc')
        detail_text = detail.text.strip() if detail else ''
        
        hash_tags = soup.find(id='hash-tag')
        tags = []
        if hash_tags:
            tags = [tag.text.strip() for tag in hash_tags.find_all('a')]
        tags_text = ','.join(tags) if tags else ''
        
        return detail_text, tags_text
    
    except Exception as e:
        logging.error(f"处理URL时出错: {url}, 错误信息: {str(e)}")
        return '', ''

def process_notes(input_file, cookie):
    """处理小红书笔记主函数"""
    try:
        logging.info(f"正在处理文件: {input_file}")
        
        # 读取Excel文件
        df = pd.read_excel(input_file)
        
        # 获取请求头
        headers = setup_headers(cookie)
        
        # 新建存储结果的列
        df['笔记详情'] = ''
        df['话题标签'] = ''
        
        # 处理每一行数据
        for index, row in df.iterrows():
            url = row[0]  # 第一列是笔记地址
            logging.info(f"正在处理第 {index + 1} 条笔记: {url}")
            
            detail, tags = get_note_content(url, headers)
            
            df.at[index, '笔记详情'] = detail
            df.at[index, '话题标签'] = tags
        
        # 生成输出文件名
        output_dir = os.path.dirname(input_file)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'processed_notes_{timestamp}.xlsx')
        
        # 保存结果
        df.to_excel(output_file, index=False)
        logging.info(f"处理完成，结果已保存至: {output_file}")
        
        return output_file
        
    except Exception as e:
        logging.error(f"处理过程中出错: {str(e)}")
        raise 