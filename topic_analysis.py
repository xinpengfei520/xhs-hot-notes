import pandas as pd
from collections import Counter

def analyze_topics(input_file, output_file):
    """分析话题标签并统计出现次数"""
    # 读取 Excel 文件
    df = pd.read_excel(input_file)
    
    # 获取 "话题标签" 列的数据
    topics = df['话题标签'].dropna().tolist()
    
    # 打印读取到的话题标签，便于调试
    print("读取到的话题标签:", topics)
    
    # 拆分话题并统计出现次数
    all_topics = []
    for topic_str in topics:
        # 拆分并去除空格，保留 # 符号
        individual_topics = [topic.strip() for topic in topic_str.split(',')]
        all_topics.extend(individual_topics)
    
    # 统计话题出现次数
    topic_counts = Counter(all_topics)
    
    # 获取出现次数最多的 50 个话题
    most_common_topics = topic_counts.most_common(50)
    
    # 写入 TXT 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for topic, count in most_common_topics:
            f.write(f"{topic}: {count}\n")
    
    print(f"话题统计结果已保存至: {output_file}")

if __name__ == '__main__':
    input_file = 'uploads/processed_notes.xlsx'  # 输入文件路径
    output_file = 'uploads/topic_analysis.txt'  # 输出文件路径
    analyze_topics(input_file, output_file) 