# -*- coding: utf-8 -*-
"""
胡潇
2022141010246
"""

#%%数据预处理
####综合得分法（3年148）（有周期性，2022暴跌）
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams['figure.facecolor'] = 'white'  # 设置背景为白色
plt.rcParams['axes.facecolor'] = 'white'   # 设置绘图区域背景为白色
plt.rcParams['axes.edgecolor'] = 'black'   # 设置边框颜色为黑色
plt.rcParams['axes.linewidth'] = 1         # 设置边框宽度
plt.rcParams['grid.color'] = 'none'        # 关闭网格
plt.rcParams['grid.linestyle'] = ''        # 确保网格不显示
plt.rcParams['text.color'] = 'black'       # 设置字体颜色为黑色

#处理数据
file_path = r'D:\python经济\final_project\all_data_raw.pickle'
data = pd.read_pickle(file_path)
data.info()
missing_values = data.isnull().sum() #检查每列的缺失值

#用每列的平均数填补缺失值
# 计算每列的平均值（仅针对数值类型列）
numeric_columns = data.select_dtypes(include=['number']).columns
column_means = data[numeric_columns].mean()

# 使用对应列的平均值填充缺失值
data.fillna(column_means, inplace=True)

# 验证填充结果
missing_summary = data.isnull().sum()

# 转换交易日期为日期类型
data['交易日期'] = pd.to_datetime(data['交易日期'])
# 增加一列"星期"，标记交易日期对应周几（1=周一，2=周二，..., 7=周日）
data['星期'] = data['交易日期'].dt.isocalendar().day

all_data = data
# 删去重复代码对应行
all_data = all_data.drop_duplicates(subset=['交易日期', '代码'], keep='first')
trading_dates = sorted(all_data['交易日期'].unique())
# 创建一个空的 DataFrame 用于存储所有重复的行
all_duplicates = pd.DataFrame()

# 检查每一天的交易数据
for date in trading_dates:
    current_data = all_data[all_data['交易日期'] == date]
    
    # 找出有重复代码的行
    is_duplicated = current_data['代码'].duplicated(keep=False)  # keep=False 标记所有重复项
    duplicated_rows = current_data[is_duplicated]
    
    # 如果有重复项，添加到结果 DataFrame 中
    if not duplicated_rows.empty:
        all_duplicates = pd.concat([all_duplicates, duplicated_rows])

# 重置索引，方便查看
all_duplicates = all_duplicates.reset_index(drop=True)

# 打印结果
if not all_duplicates.empty:
    print(f"共发现 {len(all_duplicates)} 条重复记录")
    print(all_duplicates)
else:
    print("没有发现重复的代码")

numeric_cols = ['收盘价', '转股溢价率(%)', '纯债到期收益率(%)', '剩余期限(年)', '成交金额(万元)']
for col in numeric_cols:
    all_data[col].fillna(all_data[col].mean(), inplace=True)
    

#可转债市场扩张
monthly_stats = all_data.groupby(pd.Grouper(key='交易日期', freq='M')).agg(
    转债数量=('代码', pd.Series.nunique),
    债券余额_万元=('债券余额(万元)', 'sum')  # 保持原始单位（万元）
).reset_index()

if monthly_stats.isnull().any().any():
    monthly_stats = monthly_stats.dropna()
fig, ax1 = plt.subplots(figsize=(12, 6), facecolor='white')

# 左轴：债券余额（万元）- 柱状图（数据保持原始单位）
bars = ax1.bar(
    monthly_stats['交易日期'], 
    monthly_stats['债券余额_万元'], 
    color='#A9A9A9',
    width=20, 
    label='转债余额(万元)'
)

# 定义格式化函数：将万元转换为亿元显示
def ten_thousand_to_billion(x, pos):
    return f'{x/10000:.0f}'  # 除以10000并保留整数

# 应用格式化函数到y轴
ax1.yaxis.set_major_formatter(FuncFormatter(ten_thousand_to_billion))
ax1.set_ylabel('转债余额(万元)', fontsize=12, color='#5A5A5A')
ax1.tick_params(axis='y', labelcolor='#5A5A5A')

# 右轴：可转债数量 - 折线图（保持不变）
ax2 = ax1.twinx()
ax2.plot(
    monthly_stats['交易日期'], 
    monthly_stats['转债数量'], 
    color='#E63946',
    linewidth=2, 
    marker='o', 
    markersize=5, 
    label='转债数量(右轴)'
)
ax2.set_ylabel('转债数量', fontsize=12)
ax2.tick_params(axis='y')

# 设置标题和图例
plt.title('可转债数量与债券余额', fontsize=14, fontweight='bold')
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', fontsize=10)

# 优化x轴日期显示
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
ax1.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()



# 构造双低值
all_data['双低值'] = all_data['收盘价'] + all_data['转股溢价率(%)']

# 计算收盘价与双低值在不同窗口下的相关系数
target = '收盘价'
factor = '双低值'
windows = [5, 10, 20]  # 窗口天数
stats = ['平均值', '中位值', '最大值']  # 统计量

# 存储各统计量在不同窗口下的相关系数
corr_data = {stat: [] for stat in stats}

for window in windows:
    # 按代码分组计算滚动相关系数
    rolling_corr = all_data.groupby('代码').apply(
        lambda x: x[[target, factor]].rolling(window=window).corr().iloc[1::2, 0]
    ).reset_index(level=2, drop=True).dropna()
    
    # 计算并存储各统计量
    corr_data['平均值'].append(rolling_corr.mean())
    corr_data['中位值'].append(rolling_corr.median())
    corr_data['最大值'].append(rolling_corr.max())
 

# 红灰配色方案（可根据需要调整）
colors = ['#8B0000', '#A9A9A9', '#D3D3D3']  # 深红、深灰、浅灰，对应 5、10、20 日窗口

# 绘制合并图
x = np.arange(len(stats))  # x 轴位置（对应 4 个统计量）
bar_width = 0.25  # 每个窗口的柱子宽度

fig, ax = plt.subplots(figsize=(8, 6))

for i, window in enumerate(windows):
    offset = i * bar_width
    ax.bar(x + offset, 
           [corr_data[stat][i] for stat in stats],
           width=bar_width, 
           color=colors[i], 
           label=f'{window}日窗口')

# 设置 x 轴标签
ax.set_xticks(x + bar_width * (len(windows) - 1) / 2)
ax.set_xticklabels(stats)

# 设置坐标轴与标题
ax.set_ylabel('相关系数')
ax.set_title('收盘价与双低值不同窗口相关系数统计')
ax.legend()

# 在柱子上标注数值
for i in range(len(stats)):
    for j in range(len(windows)):
        value = corr_data[stats[i]][j]
        ax.text(i + j * bar_width, value + 0.02, f'{value:.2f}', 
                ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()


 #%%   
#绘制成交额筛选结果
clean_data1 = all_data
# 1. 按周计算四分位数和每周样本量
# 1. 按周计算四分位数
weekly_quantiles = clean_data1.groupby(pd.Grouper(key='交易日期', freq='W'))['成交金额(万元)'].quantile([0.25, 0.5, 0.75])
weekly_quantiles = weekly_quantiles.reset_index().rename(columns={'level_1': '四分位', '成交金额(万元)': '金额'})

# 2. 计算合并后的总体四分位数
overall_quantiles = weekly_quantiles['金额'].quantile([0.25, 0.5, 0.75])
print("所有周四分位数合并后的总体四分位数：")
print(overall_quantiles)

# 转换交易日期为日期类型
clean_data1['交易日期'] = pd.to_datetime(clean_data1['交易日期'])

# 按月度分组，格式化为 YYYY-M 形式
clean_data1['月度区间'] = clean_data1['交易日期'].dt.to_period('M').astype(str).str.replace('-0', '-')

# 计算每月的总样本数量
monthly_total = clean_data1.groupby('月度区间').size().reset_index(name='月度总样本数')

# 假设剔除条件是成交金额(万元) <= 1000
filtered_out = clean_data1[clean_data1['成交金额(万元)'] <= 1000]
# 计算每月因条件被剔除的样本数量
monthly_filtered_count = filtered_out.groupby('月度区间').size().reset_index(name='被剔除样本数量')

# 合并数据，填充缺失值
monthly_stats = pd.merge(monthly_total, monthly_filtered_count, on='月度区间', how='left')
monthly_stats['被剔除样本数量'].fillna(0, inplace=True)

# 计算占比
monthly_stats['被剔除占比(%)'] = (monthly_stats['被剔除样本数量'] / monthly_stats['月度总样本数']) * 100

# 准备绘图数据
x_labels = monthly_stats['月度区间'].astype(str)
y1 = monthly_stats['被剔除占比(%)']
y2 = monthly_stats['被剔除样本数量']

# 绘图设置
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.grid(False)  # 关闭左轴网格

# 绘制左轴：被剔除样本占比（浅灰色填充）
ax1.set_ylabel('被剔除样本占比 (%)', fontsize=12, color='black')
ax1.fill_between(x_labels, y1, color='lightgray', alpha=0.7, label='被剔除样本占比 (%)')
ax1.tick_params(axis='y', labelcolor='black')

# 仅创建一次右轴：被剔除样本数量（深红色折线）
ax2 = ax1.twinx()  # 关键：只创建一次右轴
ax2.grid(False)  # 关闭右轴网格
ax2.set_ylabel('被剔除样本数量 (只)', fontsize=12, color='black')
ax2.plot(x_labels, y2, color='#C20000', linewidth=2, label='被剔除样本数量 (只)')
ax2.tick_params(axis='y', labelcolor='black')

# 优化坐标轴显示
for spine in ax1.spines.values():
    spine.set_visible(True)
for spine in ax2.spines.values():
    spine.set_visible(True)

# 优化横轴标签（每隔3个显示一个）
step = 3
plt.xticks(range(0, len(x_labels), step), x_labels[::step], rotation=45, color='black')

# 添加图例
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', 
           fontsize=10, facecolor='white', edgecolor='black')

# 设置标题
plt.title('月度因成交金额条件剔除样本的数量及占比', fontsize=14, color='black')
plt.tight_layout()
plt.show()
#%%


##绘制转股溢价率筛选结果
clean_data2 = all_data
# 转换交易日期为日期类型
weekly_quantiles = clean_data2.groupby(pd.Grouper(key='交易日期', freq='W'))['转股溢价率(%)'].quantile([0.25, 0.5, 0.75])
weekly_quantiles = weekly_quantiles.reset_index().rename(columns={'level_1': '四分位', '转股溢价率(%)': '金额'})

# 2. 计算合并后的总体四分位数
overall_quantiles = weekly_quantiles['金额'].quantile([0.25, 0.5, 0.75])
print("所有周四分位数合并后的总体四分位数：")
print(overall_quantiles)

clean_data2['交易日期'] = pd.to_datetime(clean_data2['交易日期'])

# 按月度分组，格式化为 YYYY-M 形式
clean_data2['月度区间'] = clean_data2['交易日期'].dt.to_period('M').astype(str).str.replace('-0', '-')

# 计算每月的总样本数量
monthly_total = clean_data2.groupby('月度区间').size().reset_index(name='月度总样本数')


filtered_out = clean_data2[clean_data2['转股溢价率(%)'] >= 30]
# 计算每月因条件被剔除的样本数量
monthly_filtered_count = filtered_out.groupby('月度区间').size().reset_index(name='被剔除样本数量')

# 合并数据，填充缺失值
monthly_stats = pd.merge(monthly_total, monthly_filtered_count, on='月度区间', how='left')
monthly_stats['被剔除样本数量'].fillna(0, inplace=True)

# 计算占比
monthly_stats['被剔除占比(%)'] = (monthly_stats['被剔除样本数量'] / monthly_stats['月度总样本数']) * 100

# 准备绘图数据
x_labels = monthly_stats['月度区间'].astype(str)
y1 = monthly_stats['被剔除占比(%)']
y2 = monthly_stats['被剔除样本数量']

# 绘图设置
fig, ax1 = plt.subplots(figsize=(12, 6))

# 绘制占比（左轴，浅灰色填充）
ax1.set_ylabel('被剔除样本占比 (%)', fontsize=12, color='black')  # 设置左纵轴标签字体颜色为黑色
ax1.fill_between(x_labels, y1, color='lightgray', alpha=0.7, label='被剔除样本占比 (%)')
ax1.tick_params(axis='y', labelcolor='black')  # 设置左纵轴刻度字体颜色为黑色

# 创建右轴绘制数量（深红色折线）
ax2 = ax1.twinx()
ax2.set_ylabel('被剔除样本数量 (只)', fontsize=12, color='black')  # 设置右纵轴标签字体颜色为黑色
ax2.plot(x_labels, y2, color='#C20000', linewidth=2, label='被剔除样本数量 (只)')
ax2.tick_params(axis='y', labelcolor='black')  # 设置右纵轴刻度字体颜色为黑色

# 优化横轴显示：每隔一定数量的标签显示，避免拥挤
step = 3  # 可根据实际情况调整间隔
plt.xticks(range(0, len(x_labels), step), x_labels[::step], rotation=45, color='black')  # 设置横轴刻度字体颜色为黑色

plt.tight_layout()

# 添加图例
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', fontsize=10, facecolor='white', edgecolor='black')

plt.title('月度因转股溢价率条件剔除样本的数量及占比', fontsize=14, color='black')  # 设置标题字体颜色为黑色
plt.show()


#%%

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from matplotlib.ticker import FuncFormatter
import pandas as pd


# --------------------------- 工具函数定义 ---------------------------
 #时序标准化算子
def time_series_standardize(df, factor_col, window=60):
        mean = df[factor_col].rolling(window).mean()
        std = df[factor_col].rolling(window).std()
        return (df[factor_col] - mean) / std
    
def prepare_selected_data(all_data):

    selected_data = all_data.copy()

    
    # 计算双低值和调整双低值
    selected_data['双低值'] = selected_data['收盘价'] + selected_data['转股溢价率(%)']
    selected_data['调整双低值'] = time_series_standardize(selected_data, '双低值')
    
    # 标准化其他因子

    selected_data['纯债到期收益率(%)_std'] = time_series_standardize(
       selected_data, '纯债到期收益率(%)'
    )
    selected_data['剩余期限(年)_std'] = time_series_standardize(
       selected_data,'剩余期限(年)'
    )
    selected_data['成交金额(万元)_std'] = time_series_standardize(
       selected_data,'成交金额(万元)'
    )
    
    # 定义需要处理的数值型列
    numeric_cols = [
        '收盘价', '转股溢价率(%)', '纯债到期收益率(%)_std', 
        '剩余期限(年)_std', '成交金额(万元)_std', '调整双低值', '双低值'
    ]
    
    # 填充缺失值
    for col in numeric_cols:
        if col in selected_data.columns:
            selected_data[col].fillna(selected_data[col].mean(), inplace=True)
    
    # 数据筛选
    selected_data = selected_data[
        (selected_data['成交金额(万元)'] > 1000) & 
        (selected_data['转股溢价率(%)'] < 30)
    ]
    
    return selected_data


def calculate_rank_ic(df, factor_col):
    """计算每周因子与下期收益率的RankIC"""
    rank_corr = spearmanr(df[factor_col], df['下期收益率'])[0]
    return pd.Series({'RankIC': rank_corr})

def calculate_long_short_returns(df, factor_col, top_n=50, bottom_n=50):
    """计算多空收益：按因子排序，取首尾组合收益"""
    sorted_df = df.sort_values(factor_col)
    long_returns = sorted_df.head(top_n)['下期收益率'].mean()
    short_returns = sorted_df.tail(bottom_n)['下期收益率'].mean()
    return pd.Series({
        '多头收益率': long_returns,
        '空头收益率': short_returns,
        '多空收益率': long_returns - short_returns
    })

def plot_factor_analysis(weekly_ic, weekly_returns, factor_name, ylim_ic=None):
    """绘制因子IC表现 + 多空收益净值图"""
    # 图表1：IC表现

    plt.figure(figsize=(14, 7))  # 调整画布大小
    
    # 左侧Y轴：RankIC（柱状图）和IC均值（折线图）
    ax1 = plt.gca()  # 获取当前坐标轴
    bars = ax1.bar(weekly_ic['交易日期'], weekly_ic['RankIC'], width=5, 
                  color='red', alpha=0.6, label='周度RankIC')
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)  # 添加水平零线
    ax1.set_title(f'{factor_name}因子IC表现')
    ax1.set_ylabel('RankIC/IC均值')
    
    # 绘制IC均值曲线（与RankIC共用左轴）
    ax1.plot(weekly_ic['交易日期'], weekly_ic['IC均值'], 
            color='gray', linestyle='--', label='IC均值(滚动52周)')
    
    # 右侧Y轴：累积IC
    ax2 = ax1.twinx()
    ax2.plot(weekly_ic['交易日期'], weekly_ic['累积IC'], 
            color='brown', label='累积IC')
    ax2.set_ylabel('累积IC', color='k')
    ax2.tick_params(axis='y', labelcolor='k')
    
    # 合并左右两侧的图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    plt.tight_layout()

    # 图表2：多空收益
    plt.figure(figsize=(12, 6))
    plt.plot(weekly_returns['交易日期'], weekly_returns['多头净值'], 
             color='red', label='多头净值(因子值低)')
    plt.plot(weekly_returns['交易日期'], weekly_returns['空头净值'], 
             color='gray', label='空头净值(因子值高)')
    plt.plot(weekly_returns['交易日期'], weekly_returns['多空净值'], 
             color='orange', linewidth=2, label='多空净值(低-高)')
    plt.axhline(y=1, color='black', linestyle='-', alpha=0.3)
    plt.title(f'{factor_name}因子多空收益')
    plt.ylabel('累积净值')
    plt.legend(loc='upper left')
    
    # 净值轴百分比格式化
    def percent_formatter(x, pos):
        return f'{x:.0%}'
    plt.gca().yaxis.set_major_formatter(FuncFormatter(percent_formatter))
    
    plt.tight_layout()
    plt.show()

def run_factor_analysis(data, factor_col, factor_name, 
                        filter_cond=None, top_n=50, bottom_n=50):
    """完整因子分析流程：数据预处理→周度计算→IC+收益→绘图"""
    # 数据预处理
    df = data.copy()
    df['交易日期'] = pd.to_datetime(df['交易日期'])
    df = df.sort_values(['交易日期', '代码'])

    
    # 周度数据处理（取每周最后一个交易日）
    weekly_data = df.groupby(['代码', pd.Grouper(key='交易日期', freq='W-FRI')]).last().reset_index()
    
    # 计算下期收益率
    weekly_data['下期收益率'] = weekly_data.groupby('代码')['收盘价'].pct_change(1).shift(-1)
    weekly_data = weekly_data.dropna(subset=['下期收益率'])
    
    # 计算周度IC
    weekly_ic = weekly_data.groupby('交易日期').apply(
        calculate_rank_ic, factor_col=factor_col
    ).reset_index()
    weekly_ic['累积IC'] = weekly_ic['RankIC'].cumsum()
    weekly_ic['IC均值'] = weekly_ic['RankIC'].rolling(window=52).mean()
    
    # 计算多空收益
    weekly_returns = weekly_data.groupby('交易日期').apply(
        calculate_long_short_returns, factor_col=factor_col, 
        top_n=top_n, bottom_n=bottom_n
    ).reset_index()
    
    # 计算累积净值
    weekly_returns['多头净值'] = (1 + weekly_returns['多头收益率']).cumprod()
    weekly_returns['空头净值'] = (1 + weekly_returns['空头收益率']).cumprod()
    weekly_returns['多空净值'] = (1 + weekly_returns['多空收益率']).cumprod()
    
    # 绘图
    plot_factor_analysis(weekly_ic, weekly_returns, factor_name)
    return weekly_ic, weekly_returns


   
# --------------------------- 主流程：调用函数执行分析 ---------------------------

if __name__ == "__main__":

    selected_data = prepare_selected_data(all_data)

  # 1. 转股溢价率因子（筛选池：成交>600万、溢价率<30%）
    weekly_ic1, weekly_returns1 = run_factor_analysis(
        selected_data, 
        factor_col='转股溢价率(%)', 
        factor_name='转股溢价率(筛选池)', 
    
    )
    
    # 2. 转股溢价率因子（不筛选池）
    weekly_ic2, weekly_returns2 = run_factor_analysis(
        all_data, 
        factor_col='转股溢价率(%)', 
        factor_name='转股溢价率(不筛选池)'
    )
    
    # 3. 双低因子
    weekly_ic3, weekly_returns3 = run_factor_analysis(
        selected_data, 
        factor_col='双低值', 
        factor_name='双低因子', 
    )
    
    # 4.收盘价大小不同的股票对比分析
    price_below = selected_data[selected_data['收盘价'] < 130]
    weekly_ic4, weekly_returns4 = run_factor_analysis(
        price_below, 
        factor_col='双低值', 
        factor_name='双低因子（收盘价<130）', 
    
    )
    
    price_above = selected_data[selected_data['收盘价'] > 130]
    weekly_ic9, weekly_returns = run_factor_analysis(
        price_above, 
        factor_col='双低值', 
        factor_name='双低因子（收盘价>130)', 
    
    )
    
    
    #5.调整纯债到期收益率(%) 正向
    weekly_ic5, weekly_returns5 = run_factor_analysis(
        selected_data, 
        factor_col='纯债到期收益率(%)_std', 
        factor_name='调整纯债到期收益率(%)'
    )
    
    #6.调整剩余期限(年) 正向
    weekly_ic6, weekly_returns6 = run_factor_analysis(
        selected_data, 
        factor_col='剩余期限(年)_std', 
        factor_name='调整剩余期限(年)'
    )
    
    #7.调整成交金额(万元)  负向
    weekly_ic7, weekly_returns7 = run_factor_analysis(
        selected_data, 
        factor_col='成交金额(万元)_std', 
        factor_name='调整成交金额(万元)'
    )
    
    #8.调整双低值  负向
    weekly_ic8, weekly_returns8 = run_factor_analysis(
        selected_data, 
        factor_col='调整双低值', 
        factor_name='调整双低值'
    )


#4个调整因子之间的相关性
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 定义需要计算相关性的因子列
factor_columns = [
    '纯债到期收益率(%)_std', 
    '剩余期限(年)_std', 
    '成交金额(万元)_std', 
    '调整双低值'
]

# 从selected_data中提取因子数据
factor_data = selected_data[factor_columns].copy()

# 计算相关系数矩阵（默认使用Pearson相关系数）
correlation_matrix = factor_data.corr()

# 打印相关系数矩阵（保留两位小数）
print("因子相关性矩阵：")
print(correlation_matrix.round(2))

plt.figure(figsize=(10, 8))
cmap = sns.diverging_palette(250, 10, as_cmap=True)  # 红灰配色

# 绘制热力图
sns.heatmap(correlation_matrix, annot=True, cmap=cmap, 
            square=True, linewidths=0.5, annot_kws={'size': 10},
            vmin=-1, vmax=1, center=0)  # 确保颜色以0为中心对称

plt.title('因子相关性热力图（红灰配色）')
plt.tight_layout()
plt.show()

correlation = selected_data['双低值'].corr(selected_data['转股溢价率(%)'])
print(f"双低值与转股溢价率的相关系数: {correlation:.4f}")

#%% 仅双低
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr
plt.style.use('seaborn-v0_8')
plt.rcParams["font.family"] = ["SimHei"]
# 解决负号显示问题
plt.rcParams["axes.unicode_minus"] = False


# 处理数据
file_path = r'D:\python经济\final_project\all_data_raw.pickle'
data = pd.read_pickle(file_path)
data.info()
missing_values = data.isnull().sum()  # 检查每列的缺失值

# 用每列的平均数填补缺失值
# 计算每列的平均值（仅针对数值类型列）
numeric_columns = data.select_dtypes(include=['number']).columns
column_means = data[numeric_columns].mean()

# 使用对应列的平均值填充缺失值
data.fillna(column_means, inplace=True)

# 验证填充结果
missing_summary = data.isnull().sum()

# 转换交易日期为日期类型
data['交易日期'] = pd.to_datetime(data['交易日期'])
# 增加一列"星期"，标记交易日期对应周几（1=周一，2=周二，..., 7=周日）
data['星期'] = data['交易日期'].dt.isocalendar().day

all_data = data
# 删去重复代码对应行
all_data = all_data.drop_duplicates(subset=['交易日期', '代码'], keep='first')
trading_dates = sorted(all_data['交易日期'].unique())
# 创建一个空的 DataFrame 用于存储所有重复的行
all_duplicates = pd.DataFrame()

# 检查每一天的交易数据
for date in trading_dates:
    current_data = all_data[all_data['交易日期'] == date]
    
    # 找出有重复代码的行
    is_duplicated = current_data['代码'].duplicated(keep=False)  # keep=False 标记所有重复项
    duplicated_rows = current_data[is_duplicated]
    
    # 如果有重复项，添加到结果 DataFrame 中
    if not duplicated_rows.empty:
        all_duplicates = pd.concat([all_duplicates, duplicated_rows])

# 重置索引，方便查看
all_duplicates = all_duplicates.reset_index(drop=True)

# 打印结果
if not all_duplicates.empty:
    print(f"共发现 {len(all_duplicates)} 条重复记录")
    print(all_duplicates)
else:
    print("没有发现重复的代码")

numeric_cols = ['收盘价', '转股溢价率(%)', '纯债到期收益率(%)', '剩余期限(年)', '成交金额(万元)']
for col in numeric_cols:
    all_data[col].fillna(all_data[col].mean(), inplace=True)


def select_and_filter_data(data):
    selected_data = data[data['星期'] == 2]
    selected_data = selected_data.drop_duplicates(subset=['交易日期', '代码'], keep='first')
    
    def time_series_standardize(df, factor_col, window=40):
        mean = df[factor_col].rolling(window).mean()
        std = df[factor_col].rolling(window).std()
        return (df[factor_col] - mean) / std

    selected_data['双低值'] = selected_data['收盘价'] + selected_data['转股溢价率(%)']
    selected_data['调整双低值'] = time_series_standardize(selected_data, '双低值')

    # 补充其他因子并标准化
    selected_data['纯债到期收益率(%)_std'] = StandardScaler().fit_transform(
        selected_data[['纯债到期收益率(%)']]
    )
    selected_data['剩余期限(年)_std'] = StandardScaler().fit_transform(
        selected_data[['剩余期限(年)']]
    )
    selected_data['成交金额(万元)_std'] = StandardScaler().fit_transform(
        selected_data[['成交金额(万元)']]
    )

    numeric_cols = ['收盘价', '转股溢价率(%)', '纯债到期收益率(%)_std', '剩余期限(年)_std', '成交金额(万元)_std', '调整双低值']
    for col in numeric_cols:
        selected_data[col].fillna(selected_data[col].mean(), inplace=True)
    
    # 筛选成交金额和转股溢价率
    selected_data = selected_data[(selected_data['成交金额(万元)'] > 1000) & (selected_data['转股溢价率(%)'] < 30)]
    return selected_data


def calculate_scores(selected_data):
    """直接选择调整双低值最小的15支可转债"""
    # 按交易日期分组，每组按调整双低值升序排序，取前15支
    selected_bond = selected_data.groupby('交易日期').apply(lambda x: x.nsmallest(15, '调整双低值')).reset_index(drop=True)
    
    # 计算每个日期实际筛选出的数量
    daily_counts = selected_data.groupby('交易日期').apply(lambda x: min(len(x), 15)).reset_index(name='实际数量')
    
    # 找出不足15支的日期
    insufficient_dates = daily_counts[daily_counts['实际数量'] < 15]
    
    return selected_bond, insufficient_dates


def backtest(selected_bond, selected_data, initial_investment):
    investment_record = []
    trading_dates = sorted(selected_bond['交易日期'].unique())
    
    for i, date in enumerate(trading_dates):
        current_data = selected_bond[selected_bond['交易日期'] == date]
        
        if i == 0:
            per_bond_investment = min(initial_investment / len(current_data), initial_investment * 0.1)
            current_data['投资金额'] = per_bond_investment
            current_data['买入数量'] = current_data['投资金额'] / current_data['开盘价']
            investment_record.append(current_data)
        else:
            prev_data = investment_record[-1]
            current_prices = selected_data[selected_data['交易日期'] == date].set_index('代码')['前收盘价']
            prev_data['卖出价格'] = prev_data['代码'].map(current_prices).fillna(prev_data['收盘价'])
            prev_data['卖出金额'] = prev_data['卖出价格'] * prev_data['买入数量']
            prev_data['买入交易成本'] = prev_data['投资金额'] * 0.0001
            prev_data['卖出交易成本'] = prev_data['卖出金额'] * 0.0001
            
            total_return = prev_data['卖出金额'].sum() - prev_data['卖出交易成本'].sum() - prev_data['买入交易成本'].sum()
            total_investment = total_return
            
            per_bond_investment = min(total_investment / len(current_data), total_investment * 0.1)
            current_data['投资金额'] = per_bond_investment
            current_data['买入数量'] = current_data['投资金额'] / current_data['开盘价']
            investment_record.append(current_data)
    
    return investment_record



def calculate_performance(investment_record, initial_investment):
    investment_df = pd.concat(investment_record, ignore_index=True)
    all_dates = sorted(investment_df['交易日期'].unique())
    
    portfolio_values = []
    dates = []
    
    for i, date in enumerate(all_dates):
        if i == 0:
            portfolio_values.append(initial_investment)
            dates.append(date)
        else:
            prev_date = all_dates[i - 1]
            prev_data = investment_df[investment_df['交易日期'] == prev_date]
            
            if '卖出金额' in prev_data.columns:
                total_value = prev_data['卖出金额'].sum() - prev_data['卖出交易成本'].sum() - prev_data['买入交易成本'].sum()
                portfolio_values.append(total_value)
                dates.append(date)
    
    # 计算总收益率
    total_return_percent = (portfolio_values[-1] - initial_investment) / initial_investment * 100
    
    # 基于交易周数计算年化收益率（每周交易一次）
    trading_weeks = len(dates) - 1  # 交易周数 = 日期数 - 1
    years = trading_weeks / 52      # 一年约52周
    annual_return_percent = ((1 + total_return_percent / 100) ** (1 / years) - 1) * 100
        
    return portfolio_values, dates, total_return_percent, annual_return_percent


def plot_portfolio_value(dates, portfolio_values):
    plt.figure(figsize=(12, 6))
    plt.rcParams['figure.facecolor'] = 'white'  # 设置背景为白色
    plt.rcParams['axes.facecolor'] = 'white'   # 设置绘图区域背景为白色
    plt.rcParams['axes.edgecolor'] = 'black'   # 设置边框颜色为黑色
    plt.rcParams['axes.linewidth'] = 1         # 设置边框宽度
    plt.rcParams['grid.color'] = 'none'        # 关闭网格
    plt.rcParams['grid.linestyle'] = ''        # 确保网格不显示
    plt.rcParams['text.color'] = 'black'       # 设置字体颜色为黑色
    plt.figure(figsize=(12, 6))
    plt.plot(dates, portfolio_values, label='总资产曲线', color='#C20000', linewidth=2.5)  # 深红色，线宽2.5
    plt.legend(loc='upper left', fontsize=10)
    plt.title('单因子模型——调整后的双低因子总资产曲线')
    plt.ylabel('总资产 (元)')
    plt.grid(True)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()


def calculate_sharpe_ratio(portfolio_values, risk_free_rate=0.000286):
    returns = np.diff(portfolio_values) / portfolio_values[:-1]
    avg_return = np.mean(returns)
    std_return = np.std(returns)
    if std_return == 0:
        return 0
    sharpe_ratio = (avg_return - risk_free_rate) / std_return * (52 ** 0.5)
        
    return sharpe_ratio


def calculate_max_drawdown(portfolio_values):
    """计算投资组合的最大回撤"""
    max_value = float('-inf')
    max_drawdown = 0.0
    
    for value in portfolio_values:
        max_value = max(max_value, value)
        drawdown = (max_value - value) / max_value
        max_drawdown = max(max_drawdown, drawdown)
    
    return max_drawdown

def calculate_annual_performance(portfolio_values, dates, risk_free_rate=0.000286):
    """按年份计算收益率、夏普比率和最大回撤"""
    if len(portfolio_values) < 2:
        return pd.DataFrame()
    
    # 创建包含日期和资产值的DataFrame
    performance_df = pd.DataFrame({
        'date': dates,
        'portfolio_value': portfolio_values
    })
    
    # 添加年份列
    performance_df['year'] = performance_df['date'].dt.year
    
    # 按年份分组计算年度指标
    annual_performance = []
    
    for year, group in performance_df.groupby('year'):
        if len(group) < 2:
            continue
            
        # 计算年度收益率
        start_value = group.iloc[0]['portfolio_value']
        end_value = group.iloc[-1]['portfolio_value']
        annual_return = (end_value - start_value) / start_value * 100
        
        # 计算年度夏普比率
        annual_returns = np.diff(group['portfolio_value']) / group['portfolio_value'].values[:-1]
        avg_annual_return = np.mean(annual_returns)
        std_annual_return = np.std(annual_returns)
        
        if std_annual_return == 0:
            sharpe = 0
        else:
            sharpe = (avg_annual_return - risk_free_rate) / std_annual_return * (len(annual_returns) ** 0.5)
        
        # 计算年度最大回撤
        max_dd = calculate_max_drawdown(group['portfolio_value'].tolist())
        
        annual_performance.append({
            '年份': year,
            '年度收益率(%)': annual_return,
            '夏普比率': sharpe,
            '最大回撤(%)': max_dd * 100
        })
    
    return pd.DataFrame(annual_performance)


# 主程序
file_path = r'D:\python经济\final_project\all_data_raw.pickle'
initial_investment = 1500000

# 选择和过滤数据
selected_data = select_and_filter_data(all_data)

# 计算得分并选择转债（直接使用调整双低值）
selected_bond, insufficient_dates = calculate_scores(selected_data)

# 输出不足15支的日期
print("\n===== 筛选不足15支的交易日 =====")
if not insufficient_dates.empty:
    print(insufficient_dates)
else:
    print("所有交易日均筛选出15支可转债。")

# 回测
investment_record = backtest(selected_bond, selected_data, initial_investment)

# 计算性能
portfolio_values, dates, total_return_percent, annual_return_percent = calculate_performance(investment_record, initial_investment)

# 绘制总资产曲线
plot_portfolio_value(dates, portfolio_values)

print(f"初始投资: {initial_investment} 元")
print(f"最终资产: {portfolio_values[-1]:.2f} 元")
print(f"总收益率: {total_return_percent:.2f}%")
print(f"年化收益率: {annual_return_percent:.2f}%")
print(f"回测周期: {len(dates)} 个交易周")

# 计算 IC
features = ['调整双低值', '纯债到期收益率(%)_std', '成交金额(万元)_std', '剩余期限(年)_std']
target = '收盘价'

# 计算夏普比率
sharpe_ratio = calculate_sharpe_ratio(portfolio_values)
print(f"夏普比率: {sharpe_ratio:.4f}")

# 计算最大回撤
max_drawdown = calculate_max_drawdown(portfolio_values)
print(f"最大回撤: {max_drawdown:.4f} ({max_drawdown*100:.2f}%)")

# 按年计算绩效指标
annual_performance = calculate_annual_performance(portfolio_values, dates)
if not annual_performance.empty:
    print("\n===== 各年度绩效指标 =====")
    print(annual_performance.to_string(index=False))
else:
    print("\n无法计算年度绩效指标（数据不足）")
    
    
#%%随机森林
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr
plt.style.use('seaborn-v0_8')
plt.rcParams["font.family"] = ["SimHei"]
# 解决负号显示问题
plt.rcParams["axes.unicode_minus"] = False


# 处理数据
file_path = r'D:\python经济\final_project\all_data_raw.pickle'
data = pd.read_pickle(file_path)
data.info()
missing_values = data.isnull().sum()  # 检查每列的缺失值

# 用每列的平均数填补缺失值
# 计算每列的平均值（仅针对数值类型列）
numeric_columns = data.select_dtypes(include=['number']).columns
column_means = data[numeric_columns].mean()

# 使用对应列的平均值填充缺失值
data.fillna(column_means, inplace=True)

# 验证填充结果
missing_summary = data.isnull().sum()

# 转换交易日期为日期类型
data['交易日期'] = pd.to_datetime(data['交易日期'])
# 增加一列"星期"，标记交易日期对应周几（1=周一，2=周二，..., 7=周日）
data['星期'] = data['交易日期'].dt.isocalendar().day

all_data = data
# 删去重复代码对应行
all_data = all_data.drop_duplicates(subset=['交易日期', '代码'], keep='first')
trading_dates = sorted(all_data['交易日期'].unique())
# 创建一个空的 DataFrame 用于存储所有重复的行
all_duplicates = pd.DataFrame()

# 检查每一天的交易数据
for date in trading_dates:
    current_data = all_data[all_data['交易日期'] == date]
    
    # 找出有重复代码的行
    is_duplicated = current_data['代码'].duplicated(keep=False)  # keep=False 标记所有重复项
    duplicated_rows = current_data[is_duplicated]
    
    # 如果有重复项，添加到结果 DataFrame 中
    if not duplicated_rows.empty:
        all_duplicates = pd.concat([all_duplicates, duplicated_rows])

# 重置索引，方便查看
all_duplicates = all_duplicates.reset_index(drop=True)

# 打印结果
if not all_duplicates.empty:
    print(f"共发现 {len(all_duplicates)} 条重复记录")
    print(all_duplicates)
else:
    print("没有发现重复的代码")

numeric_cols = ['收盘价', '转股溢价率(%)', '纯债到期收益率(%)', '剩余期限(年)', '成交金额(万元)']
for col in numeric_cols:
    all_data[col].fillna(all_data[col].mean(), inplace=True)

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr
plt.style.use('seaborn-v0_8')
plt.rcParams['font.sans-serif'] = ['SimHei']


def select_and_filter_data(data):
    selected_data = data[data['星期'] == 2]
    selected_data = selected_data.drop_duplicates(subset=['交易日期', '代码'], keep='first')
    
    def time_series_standardize(df, factor_col, window=60):
        mean = df[factor_col].rolling(window).mean()
        std = df[factor_col].rolling(window).std()
        return (df[factor_col] - mean) / std

    selected_data['双低值'] = selected_data['收盘价'] + selected_data['转股溢价率(%)']
    selected_data['调整双低值'] = time_series_standardize(selected_data, '双低值')

    # 补充其他因子并标准化
    selected_data['纯债到期收益率(%)_std'] = StandardScaler().fit_transform(
        selected_data[['纯债到期收益率(%)']]
    )
    selected_data['剩余期限(年)_std'] = StandardScaler().fit_transform(
        selected_data[['剩余期限(年)']]
    )
    selected_data['成交金额(万元)_std'] = StandardScaler().fit_transform(
        selected_data[['成交金额(万元)']]
    )

    numeric_cols = ['收盘价', '转股溢价率(%)', '纯债到期收益率(%)_std', '剩余期限(年)_std', '成交金额(万元)_std', '调整双低值']
    for col in numeric_cols:
        selected_data[col].fillna(selected_data[col].mean(), inplace=True)
    selected_data = selected_data[(selected_data['成交金额(万元)'] > 1000) & (selected_data['转股溢价率(%)'] < 30)]
    return selected_data
   


def train_random_forest(selected_data):
    features = ['调整双低值', '纯债到期收益率(%)_std', '成交金额(万元)_std', '剩余期限(年)_std']
    target = '收盘价'
    X = selected_data[features]
    y = selected_data[target]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model, scaler, features


def calculate_scores(selected_data, model, scaler, features):
    X = selected_data[features]
    X_scaled = scaler.transform(X)
    predicted_prices = model.predict(X_scaled)
    selected_data['预测差异得分'] = (predicted_prices - selected_data['收盘价']) / selected_data['收盘价']
    selected_bond = selected_data.groupby('交易日期').apply(lambda x: x.nlargest(15, '预测差异得分')).reset_index(drop=True)
    return selected_bond


def backtest(selected_bond, selected_data, initial_investment):
    investment_record = []
    trading_dates = sorted(selected_bond['交易日期'].unique())
    for i, date in enumerate(trading_dates):
        current_data = selected_bond[selected_bond['交易日期'] == date]
        if i == 0:
            per_bond_investment = min(initial_investment / len(current_data), initial_investment * 0.1)
            current_data['投资金额'] = per_bond_investment
            current_data['买入数量'] = current_data['投资金额'] / current_data['开盘价']
            investment_record.append(current_data)
        else:
            prev_data = investment_record[-1]
            current_prices = selected_data[selected_data['交易日期'] == date].set_index('代码')['前收盘价']
            prev_data['卖出价格'] = prev_data['代码'].map(current_prices).fillna(prev_data['收盘价'])
            prev_data['卖出金额'] = prev_data['卖出价格'] * prev_data['买入数量']
            prev_data['买入交易成本'] = prev_data['投资金额'] * 0.0001
            prev_data['卖出交易成本'] = prev_data['卖出金额'] * 0.0001
            total_return = prev_data['卖出金额'].sum() - prev_data['卖出交易成本'].sum() - prev_data['买入交易成本'].sum()
            total_investment = total_return
            per_bond_investment = min(total_investment / len(current_data), total_investment * 0.1)
            current_data['投资金额'] = per_bond_investment
            current_data['买入数量'] = current_data['投资金额'] / current_data['开盘价']
            investment_record.append(current_data)
    return investment_record


def calculate_performance(investment_record, initial_investment):
    investment_df = pd.concat(investment_record, ignore_index=True)
    all_dates = sorted(investment_df['交易日期'].unique())
    penultimate_date = all_dates[-2]
    final_value = investment_df[investment_df['交易日期'] == penultimate_date]['卖出金额'].sum()
    total_return = final_value - initial_investment
    annual_return = (total_return / initial_investment) / ((len(all_dates) - 1) / 52)
    portfolio_values = []
    dates = []
    for i, date in enumerate(all_dates):
        if i == 0:
            portfolio_values.append(initial_investment)
            dates.append(date)
        else:
            prev_date = all_dates[i - 1]
            prev_data = investment_df[investment_df['交易日期'] == prev_date]
            if '卖出金额' in prev_data.columns:
                total_value = prev_data['卖出金额'].sum()
                portfolio_values.append(total_value)
                dates.append(date)
    total_return_percent = (portfolio_values[-2] - initial_investment) / initial_investment * 100
    trading_weeks = len(dates) - 1  # 交易周数 = 日期数 - 1
    years = trading_weeks / 52      # 一年约52周
    annual_return_percent = ((1 + total_return_percent / 100) ** (1 / years) - 1) * 100
    return portfolio_values, dates, total_return_percent, annual_return_percent


def plot_portfolio_value(dates, portfolio_values):
    plt.figure(figsize=(12, 6))
    plt.rcParams['figure.facecolor'] = 'white'  # 设置背景为白色
    plt.rcParams['axes.facecolor'] = 'white'   # 设置绘图区域背景为白色
    plt.rcParams['axes.edgecolor'] = 'black'   # 设置边框颜色为黑色
    plt.rcParams['axes.linewidth'] = 1         # 设置边框宽度
    plt.rcParams['grid.color'] = 'none'        # 关闭网格
    plt.rcParams['grid.linestyle'] = ''        # 确保网格不显示
    plt.rcParams['text.color'] = 'black'       # 设置字体颜色为黑色
    plt.figure(figsize=(12, 6))
    plt.plot(dates, portfolio_values, label='总资产曲线', color='#C20000', linewidth=2.5)  # 深红色，线宽2.5
    plt.legend(loc='upper left', fontsize=10)
    plt.title('多因子模型——随机森林总资产曲线')
    plt.ylabel('总资产 (元)')
    plt.grid(True)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()


def calculate_ic(selected_data, features, target):
    ic_values = {}
    for feature in features:
        ic, _ = spearmanr(selected_data[feature], selected_data[target])
        ic_values[feature] = ic
    return ic_values


def calculate_sharpe_ratio(portfolio_values, risk_free_rate=0.000286):
    returns = np.diff(portfolio_values) / portfolio_values[:-1]
    avg_return = np.mean(returns)
    std_return = np.std(returns)
    if std_return == 0:
        return 0
    sharpe_ratio = (avg_return - risk_free_rate) / std_return * (52 ** 0.5)
    return sharpe_ratio


def calculate_max_drawdown(portfolio_values):
    """计算投资组合的最大回撤"""
    max_value = float('-inf')
    max_drawdown = 0.0
    
    for value in portfolio_values:
        max_value = max(max_value, value)
        drawdown = (max_value - value) / max_value
        max_drawdown = max(max_drawdown, drawdown)
    
    return max_drawdown

def calculate_annual_performance(portfolio_values, dates, risk_free_rate=0.000286):
    """按年份计算年度收益率、夏普比率和最大回撤"""
    if len(portfolio_values) < 2:
        return pd.DataFrame()
    
    # 创建包含日期和资产值的DataFrame
    performance_df = pd.DataFrame({
        'date': dates,
        'portfolio_value': portfolio_values
    })
    
    # 添加年份列
    performance_df['year'] = performance_df['date'].dt.year
    
    # 按年份分组计算年度指标
    annual_performance = []
    
    for year, group in performance_df.groupby('year'):
        if len(group) < 2:
            continue
            
        # 计算年度收益率
        start_value = group.iloc[0]['portfolio_value']
        end_value = group.iloc[-1]['portfolio_value']
        annual_return = (end_value - start_value) / start_value * 100
        
        # 计算年度夏普比率
        annual_returns = np.diff(group['portfolio_value']) / group['portfolio_value'].values[:-1]
        avg_annual_return = np.mean(annual_returns)
        std_annual_return = np.std(annual_returns)
        
        if std_annual_return == 0:
            sharpe = 0
        else:
            sharpe = (avg_annual_return - risk_free_rate) / std_annual_return * (len(annual_returns) ** 0.5)
        
        # 计算年度最大回撤
        max_dd = calculate_max_drawdown(group['portfolio_value'].tolist())
        
        annual_performance.append({
            '年份': year,
            '年度收益率(%)': annual_return,
            '夏普比率': sharpe,
            '最大回撤(%)': max_dd * 100
        })
    
    return pd.DataFrame(annual_performance)


# 主程序
file_path = r'D:\python经济\final_project\all_data_raw.pickle'
initial_investment = 1500000

# 选择和过滤数据
selected_data = select_and_filter_data(all_data)

# 训练随机森林模型
model, scaler, features = train_random_forest(selected_data)

# 计算得分并选择转债
selected_bond = calculate_scores(selected_data, model, scaler, features)

# 回测
investment_record = backtest(selected_bond, selected_data, initial_investment)

# 计算性能
portfolio_values, dates, total_return_percent, annual_return_percent = calculate_performance(investment_record, initial_investment)

# 绘制总资产曲线
plot_portfolio_value(dates, portfolio_values)

print(f"初始投资: {initial_investment} 元")
print(f"最终资产: {portfolio_values[-2]:.2f} 元")
print(f"总收益率: {total_return_percent:.2f}%")
print(f"年化收益率: {annual_return_percent:.2f}%")
print(f"回测周期: {len(dates)} 个交易日")

# 计算 IC
target = '收盘价'
ic_values = calculate_ic(selected_data, features, target)
print("各因子与收盘价的 IC：")
for factor, ic in ic_values.items():
    print(f"{factor}: {ic:.4f}")

# 计算夏普比率
sharpe_ratio = calculate_sharpe_ratio(portfolio_values)
print(f"夏普比率: {sharpe_ratio:.4f}")

# 计算最大回撤
max_drawdown = calculate_max_drawdown(portfolio_values)
print(f"最大回撤: {max_drawdown:.4f}")

# 按年计算绩效指标
annual_performance = calculate_annual_performance(portfolio_values, dates)
if not annual_performance.empty:
    print("\n===== 各年度绩效指标 =====")
    print(annual_performance.to_string(index=False))
else:
    print("\n无法计算年度绩效指标（数据不足）")
    
#%%GRU
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
plt.rcParams["font.family"] = ["SimHei"]
# 解决负号显示问题
plt.rcParams["axes.unicode_minus"] = False


#处理数据
file_path = r'D:\python经济\final_project\all_data_raw.pickle'
data = pd.read_pickle(file_path)
data.info()
missing_values = data.isnull().sum() #检查每列的缺失值

#用每列的平均数填补缺失值
# 计算每列的平均值（仅针对数值类型列）
numeric_columns = data.select_dtypes(include=['number']).columns
column_means = data[numeric_columns].mean()

# 使用对应列的平均值填充缺失值
data.fillna(column_means, inplace=True)

# 验证填充结果
missing_summary = data.isnull().sum()

# 转换交易日期为日期类型
data['交易日期'] = pd.to_datetime(data['交易日期'])
# 增加一列"星期"，标记交易日期对应周几（1=周一，2=周二，..., 7=周日）
data['星期'] = data['交易日期'].dt.isocalendar().day

all_data = data
# 简化版：如果只有收盘价和成交量数据
# 按交易日期和代码分组计算 VWAP
# 按交易日期和代码分组计算 VWAP
def calculate_daily_vwap(group):

    # 计算典型价格 (TP) - 日内平均价格的近似
    typical_price = (group['开盘价'] + group['最高价'] + group['最低价'] + group['收盘价']) / 4
    
    # 计算成交量加权的价格总和
    vwap_numerator = typical_price * group['成交金额(万元)']
    
    # 计算总成交量
    total_volume = group['成交金额(万元)'].sum()
    
    # 避免除零错误
    if total_volume == 0:
        return 0
    
    # 计算 VWAP
    return vwap_numerator.sum() / total_volume

# 按交易日期和代码分组计算 VWAP
all_data['VWAP'] = all_data.groupby(['交易日期', '代码']).apply(calculate_daily_vwap).reset_index(level=[0,1], drop=True)

# 计算 VWAP 与收盘价的偏离度 (VWAP 指标常用作交易信号)
all_data['VWAP_偏离度'] = (all_data['收盘价'] - all_data['VWAP']) / all_data['VWAP']

print("VWAP 指标计算完成，已添加到 all_data 中")
# 删去重复代码对应行
all_data = all_data.drop_duplicates(subset=['交易日期', '代码'], keep='first')
trading_dates = sorted(all_data['交易日期'].unique())
# 创建一个空的 DataFrame 用于存储所有重复的行
all_duplicates = pd.DataFrame()

# 检查每一天的交易数据
for date in trading_dates:
    current_data = all_data[all_data['交易日期'] == date]
    
    # 找出有重复代码的行
    is_duplicated = current_data['代码'].duplicated(keep=False)  # keep=False 标记所有重复项
    duplicated_rows = current_data[is_duplicated]
    
    # 如果有重复项，添加到结果 DataFrame 中
    if not duplicated_rows.empty:
        all_duplicates = pd.concat([all_duplicates, duplicated_rows])

# 重置索引，方便查看
all_duplicates = all_duplicates.reset_index(drop=True)

# 打印结果
if not all_duplicates.empty:
    print(f"共发现 {len(all_duplicates)} 条重复记录")
    print(all_duplicates)
else:
    print("没有发现重复的代码")

numeric_cols = ['收盘价', '转股溢价率(%)', '纯债到期收益率(%)', '剩余期限(年)', '成交金额(万元)']
for col in numeric_cols:
    all_data[col].fillna(all_data[col].mean(), inplace=True)
    
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from scipy.stats import spearmanr
plt.style.use('seaborn-v0_8')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams["axes.unicode_minus"] = False

# 设置随机种子以确保结果可复现
torch.manual_seed(42)
np.random.seed(42)

# GRU模型定义
class GRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(GRUModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # GRU层
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        
        # 全连接层，将GRU的输出转换为预测值
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        # 初始化隐藏状态
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # 前向传播GRU
        out, _ = self.gru(x, h0)
        
        # 只取最后一个时间步的输出
        out = self.fc(out[:, -1, :])
        return out

# 准备序列数据
def create_sequences(data, seq_length, target_col_index=None):
    """
    将数据转换为序列格式，适合RNN/LSTM/GRU模型
    data: numpy数组，形状为 (样本数, 特征数)
    seq_length: 序列长度
    target_col_index: 目标变量在特征中的索引位置，如果为None则不返回y
    """
    X = []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length, :])
    
    if target_col_index is not None:
        y = data[seq_length:, target_col_index]
        return np.array(X), np.array(y)
    else:
        return np.array(X)

# 处理数据函数
def select_and_filter_data(data):
    selected_data = data[data['星期'] == 2]
    selected_data = selected_data.drop_duplicates(subset=['交易日期', '代码'], keep='first')
    
    def time_series_standardize(df, factor_col, window=60):
        mean = df[factor_col].rolling(window).mean()
        std = df[factor_col].rolling(window).std()
        return (df[factor_col] - mean) / std

    selected_data['双低值'] = selected_data['收盘价'] + selected_data['转股溢价率(%)']
    selected_data['调整双低值'] = time_series_standardize(selected_data, '双低值')

    # 补充其他因子并标准化
    selected_data['纯债到期收益率(%)_std'] = StandardScaler().fit_transform(
        selected_data[['纯债到期收益率(%)']]
    )
    selected_data['剩余期限(年)_std'] = StandardScaler().fit_transform(
        selected_data[['剩余期限(年)']]
    )
    selected_data['成交金额(万元)_std'] = StandardScaler().fit_transform(
        selected_data[['成交金额(万元)']]
    )

    numeric_cols = ['收盘价', '转股溢价率(%)', '纯债到期收益率(%)_std', '剩余期限(年)_std', '成交金额(万元)_std', '调整双低值']
    for col in numeric_cols:
        selected_data[col].fillna(selected_data[col].mean(), inplace=True)
    
    # 筛选条件
    selected_data = selected_data[(selected_data['成交金额(万元)'] > 1000) & (selected_data['转股溢价率(%)'] < 30)]
    return selected_data

# 训练GRU模型
def train_gru_model(selected_data, features, target, seq_length=20):
    # 提取特征和目标变量
    X = selected_data[features].values
    y = selected_data[target].values
    
    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 为目标变量创建一个索引
    target_col_index = features.index(target)
    
    # 创建序列数据
    X_seq, y_seq = create_sequences(X_scaled, seq_length, target_col_index)
    
    # 转换为PyTorch张量
    X_tensor = torch.FloatTensor(X_seq)
    y_tensor = torch.FloatTensor(y_seq)
    
    # 划分训练集和测试集
    train_size = int(0.8 * len(X_tensor))
    X_train, X_test = X_tensor[:train_size], X_tensor[train_size:]
    y_train, y_test = y_tensor[:train_size], y_tensor[train_size:]
    
    # 创建数据加载器
    batch_size = 64
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    # 初始化模型
    input_size = len(features)
    hidden_size = 64
    num_layers = 2
    output_size = 1
    
    model = GRUModel(input_size, hidden_size, num_layers, output_size)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # 训练模型
    num_epochs = 50
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch.view(-1, 1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        if (epoch+1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss/len(train_loader):.4f}')
    
    # 在测试集上评估模型
    model.eval()
    with torch.no_grad():
        test_outputs = model(X_test)
        test_loss = criterion(test_outputs, y_test.view(-1, 1))
        print(f'Test Loss: {test_loss.item():.4f}')
    
    return model, scaler, features, seq_length

# 计算预测得分
def calculate_scores(selected_data, model, scaler, features, seq_length):
    # 提取特征
    X = selected_data[features].values
    
    # 标准化
    X_scaled = scaler.transform(X)
    
    # 创建序列数据
    X_seq = create_sequences(X_scaled, seq_length)
    
    # 转换为PyTorch张量
    X_tensor = torch.FloatTensor(X_seq)
    
    # 预测
    model.eval()
    with torch.no_grad():
        predicted_prices = model(X_tensor).numpy().flatten()
    
    # 由于序列处理会减少样本数，我们需要调整预测结果的长度以匹配原始数据
    # 这里我们只保留有预测值的部分
    selected_data = selected_data.iloc[seq_length:]
    selected_data = selected_data.reset_index(drop=True)
    
    # 计算预测差异得分
    selected_data['预测差异得分'] = (predicted_prices - selected_data['收盘价']) / selected_data['收盘价']
    
    # 选择得分最高的15只可转债
    selected_bond = selected_data.groupby('交易日期').apply(lambda x: x.nlargest(15, '预测差异得分')).reset_index(drop=True)
    
    return selected_bond

# 回测函数保持不变
def backtest(selected_bond, selected_data, initial_investment):
    investment_record = []
    trading_dates = sorted(selected_bond['交易日期'].unique())
    for i, date in enumerate(trading_dates):
        current_data = selected_bond[selected_bond['交易日期'] == date]
        if i == 0:
            per_bond_investment = min(initial_investment / len(current_data), initial_investment * 0.1)
            current_data['投资金额'] = per_bond_investment
            current_data['买入数量'] = current_data['投资金额'] / current_data['开盘价']
            investment_record.append(current_data)
        else:
            prev_data = investment_record[-1]
            current_prices = selected_data[selected_data['交易日期'] == date].set_index('代码')['前收盘价']
            prev_data['卖出价格'] = prev_data['代码'].map(current_prices).fillna(prev_data['收盘价'])
            prev_data['卖出金额'] = prev_data['卖出价格'] * prev_data['买入数量']
            prev_data['买入交易成本'] = prev_data['投资金额'] * 0.0001
            prev_data['卖出交易成本'] = prev_data['卖出金额'] * 0.0001
            total_return = prev_data['卖出金额'].sum() - prev_data['卖出交易成本'].sum() - prev_data['买入交易成本'].sum()
            total_investment = total_return
            per_bond_investment = min(total_investment / len(current_data), total_investment * 0.1)
            current_data['投资金额'] = per_bond_investment
            current_data['买入数量'] = current_data['投资金额'] / current_data['开盘价']
            investment_record.append(current_data)
    return investment_record

# 计算性能函数保持不变
def calculate_performance(investment_record, initial_investment):
    investment_df = pd.concat(investment_record, ignore_index=True)
    all_dates = sorted(investment_df['交易日期'].unique())
    penultimate_date = all_dates[-2]
    final_value = investment_df[investment_df['交易日期'] == penultimate_date]['卖出金额'].sum()
    total_return = final_value - initial_investment
    annual_return = (total_return / initial_investment) / ((len(all_dates) - 1) / 52)
    portfolio_values = []
    dates = []
    for i, date in enumerate(all_dates):
        if i == 0:
            portfolio_values.append(initial_investment)
            dates.append(date)
        else:
            prev_date = all_dates[i - 1]
            prev_data = investment_df[investment_df['交易日期'] == prev_date]
            if '卖出金额' in prev_data.columns:
                total_value = prev_data['卖出金额'].sum()
                portfolio_values.append(total_value)
                dates.append(date)
    total_return_percent = (portfolio_values[-2] - initial_investment) / initial_investment * 100
    trading_weeks = len(dates) - 1  # 交易周数 = 日期数 - 1
    years = trading_weeks / 52      # 一年约52周
    annual_return_percent = ((1 + total_return_percent / 100) ** (1 / years) - 1) * 100
    return portfolio_values, dates, total_return_percent, annual_return_percent

# 绘制资产曲线函数保持不变
def plot_portfolio_value(dates, portfolio_values):
    plt.figure(figsize=(12, 6))
    plt.rcParams['figure.facecolor'] = 'white'  # 设置背景为白色
    plt.rcParams['axes.facecolor'] = 'white'   # 设置绘图区域背景为白色
    plt.rcParams['axes.edgecolor'] = 'black'   # 设置边框颜色为黑色
    plt.rcParams['axes.linewidth'] = 1         # 设置边框宽度
    plt.rcParams['grid.color'] = 'none'        # 关闭网格
    plt.rcParams['grid.linestyle'] = ''        # 确保网格不显示
    plt.rcParams['text.color'] = 'black'       # 设置字体颜色为黑色
    plt.figure(figsize=(12, 6))
    plt.plot(dates, portfolio_values, label='总资产曲线', color='#C20000', linewidth=2.5)  # 深红色，线宽2.5
    plt.legend(loc='upper left', fontsize=10)
    plt.title('多因子模型——GRU总资产曲线')
    plt.ylabel('总资产 (元)')
    plt.grid(True)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()


# 计算IC函数保持不变
def calculate_ic(selected_data, features, target):
    ic_values = {}
    for feature in features:
        ic, _ = spearmanr(selected_data[feature], selected_data[target])
        ic_values[feature] = ic
    return ic_values

# 计算夏普比率函数保持不变
def calculate_sharpe_ratio(portfolio_values, risk_free_rate=0.000286):
    returns = np.diff(portfolio_values) / portfolio_values[:-1]
    avg_return = np.mean(returns)
    std_return = np.std(returns)
    if std_return == 0:
        return 0
    sharpe_ratio = (avg_return - risk_free_rate) / std_return * (52 ** 0.5)
    return sharpe_ratio

# 计算最大回撤函数保持不变
def calculate_max_drawdown(portfolio_values):
    """计算投资组合的最大回撤"""
    max_value = float('-inf')
    max_drawdown = 0.0
    
    for value in portfolio_values:
        max_value = max(max_value, value)
        drawdown = (max_value - value) / max_value
        max_drawdown = max(max_drawdown, drawdown)
    
    return max_drawdown
def calculate_annual_performance(portfolio_values, dates, risk_free_rate=0.000286):
    """按年份计算收益率、夏普比率和最大回撤"""
    if len(portfolio_values) < 2:
        return pd.DataFrame()
    
    # 创建包含日期和资产值的DataFrame
    performance_df = pd.DataFrame({
        'date': dates,
        'portfolio_value': portfolio_values
    })
    
    # 添加年份列
    performance_df['year'] = performance_df['date'].dt.year
    
    # 按年份分组计算年度指标
    annual_performance = []
    
    for year, group in performance_df.groupby('year'):
        if len(group) < 2:
            continue
            
        # 计算年度收益率
        start_value = group.iloc[0]['portfolio_value']
        end_value = group.iloc[-1]['portfolio_value']
        annual_return = (end_value - start_value) / start_value * 100
        
        # 计算年度夏普比率
        annual_returns = np.diff(group['portfolio_value']) / group['portfolio_value'].values[:-1]
        avg_annual_return = np.mean(annual_returns)
        std_annual_return = np.std(annual_returns)
        
        if std_annual_return == 0:
            sharpe = 0
        else:
            sharpe = (avg_annual_return - risk_free_rate) / std_annual_return * (len(annual_returns) ** 0.5)
        
        # 计算年度最大回撤
        max_dd = calculate_max_drawdown(group['portfolio_value'].tolist())
        
        annual_performance.append({
            '年份': year,
            '年度收益率(%)': annual_return,
            '夏普比率': sharpe,
            '最大回撤(%)': max_dd * 100
        })
    
    return pd.DataFrame(annual_performance)

# 主程序
if __name__ == "__main__":
    # 假设已经加载了数据
    # file_path = r'D:\python经济\final_project\all_data_raw.pickle'
    # all_data = pd.read_pickle(file_path)
    
    initial_investment = 1500000
    
    # 选择和过滤数据
    selected_data = select_and_filter_data(all_data)
    
    # 定义特征和目标
    features = ['调整双低值',  '收盘价','最高价','最低价','开盘价','VWAP']
    target = '收盘价'
    
    # 训练GRU模型
    model, scaler, features, seq_length = train_gru_model(selected_data, features, target)
    
    # 计算得分并选择转债
    selected_bond = calculate_scores(selected_data, model, scaler, features, seq_length)
    
    # 回测
    investment_record = backtest(selected_bond, selected_data, initial_investment)
    
    # 计算性能
    portfolio_values, dates, total_return_percent, annual_return_percent = calculate_performance(investment_record, initial_investment)
    
    # 绘制总资产曲线
    plot_portfolio_value(dates, portfolio_values)
    
    print(f"初始投资: {initial_investment} 元")
    print(f"最终资产: {portfolio_values[-2]:.2f} 元")
    print(f"总收益率: {total_return_percent:.2f}%")
    print(f"年化收益率: {annual_return_percent:.2f}%")
    print(f"回测周期: {len(dates)} 个交易日")
    
    # 计算 IC
    target = '收盘价'
    ic_values = calculate_ic(selected_data, features, target)
    print("各因子与收盘价的 IC：")
    for factor, ic in ic_values.items():
        print(f"{factor}: {ic:.4f}")
    
    # 计算夏普比率
    sharpe_ratio = calculate_sharpe_ratio(portfolio_values)
    print(f"夏普比率: {sharpe_ratio:.4f}")
    
    # 计算最大回撤
    max_drawdown = calculate_max_drawdown(portfolio_values)
    print(f"最大回撤: {max_drawdown:.4f}")
    
    # 按年计算绩效指标
    annual_performance = calculate_annual_performance(portfolio_values, dates)
    if not annual_performance.empty:
        print("\n===== 各年度绩效指标 =====")
        print(annual_performance.to_string(index=False))
    else:
        print("\n无法计算年度绩效指标（数据不足）")


