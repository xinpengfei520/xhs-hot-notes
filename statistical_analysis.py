import pandas as pd
from collections import Counter
import re

def extract_keywords(title):
    """提取标题中的关键词"""
    # 使用正则表达式去除非字母和数字的字符
    title = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', ' ', title)
    # 分词，简单处理为按空格分隔
    keywords = title.split()
    return keywords

def analyze_titles(input_file, output_file):
    """分析笔记标题并统计关键词出现次数"""
    # 读取 Excel 文件
    df = pd.read_excel(input_file)
    
    # 获取 "笔记标题" 列的数据
    titles = df['笔记标题'].dropna().tolist()
    
    # 提取所有关键词
    all_keywords = []
    for title in titles:
        keywords = extract_keywords(title)
        all_keywords.extend(keywords)
    
    # 统计关键词出现次数
    keyword_counts = Counter(all_keywords)
    
    # 将结果转换为 DataFrame
    result_df = pd.DataFrame(keyword_counts.items(), columns=['关键词', '出现次数'])
    
    # 按出现次数倒序排列
    result_df = result_df.sort_values(by='出现次数', ascending=False)
    
    # 写入新的 Excel 文件
    result_df.to_excel(output_file, index=False)
    print(f"统计结果已保存至: {output_file}")

if __name__ == '__main__':
    input_file = 'uploads/processed_notes.xlsx'  # 输入文件路径
    output_file = 'uploads/keyword_analysis.xlsx'  # 输出文件路径
    analyze_titles(input_file, output_file) 