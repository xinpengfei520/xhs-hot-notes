import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_headers():
    """设置请求头"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Cookie': 'timestamp2=1730275859061380742226e6915e83f2d943afe8b94483cd4c48b2635260ead; timestamp2.sig=9Bc8MwYAW9EjyF9QQ93s_RTk7QgOSsN5PU-3Y3YOKI0; acw_tc=0a00d80e17341452190184503edfb132f46b0b31cacdc181da465755135fd3; abRequestId=2ae711a0-8081-59cc-8327-48e83602b9b6; webBuild=4.47.1; a1=193c31c1bb1jxc452lwomp1w55gols45isma5chzu30000204390; webId=84da6b10e99219102f67540364f4f285; websectiga=2a3d3ea002e7d92b5c9743590ebd24010cf3710ff3af8029153751e41a6af4a3; sec_poison_id=924338d1-4cf2-4d5f-bf08-9f0d7c829eb2; gid=yjqSqySJj43qyjqSqySyDMSxDyVCS42J1El66u7UyE22k0q8l1M422888J84qj88D4qdjKjd; web_session=040069736d4af9cd18fbb1bc69354b8e225f4d; unread={%22ub%22:%22675690400000000007009efe%22%2C%22ue%22:%22673d9e910000000002019d9b%22%2C%22uc%22:29}; xsecappid=ranchi'  # 替换为你的实际 cookie
    }
    return headers

def get_note_content(url, headers):
    """获取笔记内容和话题标签"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 获取笔记详情
        detail = soup.find(id='detail-desc')
        detail_text = detail.text.strip() if detail else ''
        
        # 获取话题标签
        hash_tags = soup.find(id='hash-tag')
        tags = []
        if hash_tags:
            tags = [tag.text.strip() for tag in hash_tags.find_all('a')]
        tags_text = ','.join(tags) if tags else ''
        
        return detail_text, tags_text
    
    except Exception as e:
        logging.error(f"处理URL时出错: {url}, 错误信息: {str(e)}")
        return '', ''

def process_notes():
    """处理小红书笔记主函数"""
    try:
        # 设置文件路径
        input_path = '/Users/vancexin/Desktop/'
        
        # 获取目录下的所有xlsx文件
        xlsx_files = [f for f in os.listdir(input_path) if f.endswith('.xlsx')]
        
        if not xlsx_files:
            logging.error("未找到xlsx文件")
            return
            
        input_file = os.path.join(input_path, xlsx_files[0])
        logging.info(f"正在处理文件: {input_file}")
        
        # 读取Excel文件
        df = pd.read_excel(input_file)
        
        # 获取请求头
        headers = setup_headers()
        
        # 新建存储结果的列
        df['笔记详情'] = ''
        df['话题标签'] = ''
        
        # 处理每一行数据
        for index, row in df.iterrows():
            url = row[0]  # 第一列是笔记地址
            logging.info(f"正在处理第 {index + 1} 条笔记: {url}")
            
            # 获取笔记内容和标签
            detail, tags = get_note_content(url, headers)
            
            # 更新数据框
            df.at[index, '笔记详情'] = detail
            df.at[index, '话题标签'] = tags
        
        # 生成输出文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(input_path, f'processed_notes_{timestamp}.xlsx')
        
        # 保存结果
        df.to_excel(output_file, index=False)
        logging.info(f"处理完成，结果已保存至: {output_file}")
        
    except Exception as e:
        logging.error(f"处理过程中出错: {str(e)}")

if __name__ == '__main__':
    process_notes() 