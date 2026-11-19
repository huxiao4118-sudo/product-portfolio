# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 19:35:33 2025

@author: huxiao
"""

#%%AI指数全球分布情况
import pandas as pd

# 读取文件
excel_file = pd.ExcelFile(r'C:\Users\huxiao\Desktop\AI_index_db.xlsx')
# 获取指定工作表中的数据
df = excel_file.parse('AI_index_db')

# 查看数据的基本信息
print('数据基本信息：')
df.info()



##全球AI指数
import geopandas as gpd
import matplotlib.pyplot as plt
from zipfile import ZipFile
import tempfile
import os

# 读取本地的 ZIP 文件
# 请根据实际上传文件名和路径修改，代码运行环境里一般是 /mnt/ 开头
zip_file_path = "D:/python经济/ne_110m_admin_0_countries.zip"
# 创建临时目录
with tempfile.TemporaryDirectory() as tmpdirname:
    with ZipFile(zip_file_path, 'r') as zip_file:
        # 将 ZIP 文件解压到临时目录
        zip_file.extractall(tmpdirname)
        # 找到解压后的.shp 文件
        for root, dirs, files in os.walk(tmpdirname):
            for file in files:
                if file.endswith('.shp'):
                    shapefile_path = os.path.join(root, file)
                    world = gpd.read_file(shapefile_path)

# 合并地图数据和 AI 指数数据
merged = world.merge(df, left_on='NAME', right_on='Country', how='left')

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
fig.patch.set_facecolor('white')  # 设置图形背景为白色
ax.set_facecolor('white') 
# 绘制地图，使用蓝色系配色
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
merged.plot(column='Total score',
            ax=ax,
            cmap='Blues',
            legend=True,
            missing_kwds={
                "color": "lightgrey",
                "label": "无数据",
            },
            legend_kwds={
                "label": "AI 指数总得分",
                "orientation": "horizontal",
                "shrink": 0.6
            })

# 设置标题
ax.set_title('全球 AI 指数总得分分布')

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.show()


#不同类别国家AI指数的各个维度对比

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, colors
import matplotlib.ticker as ticker

# 确保中文显示正常
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams['axes.unicode_minus'] = False

# 提取需要展示的指标列
features = ['Talent', 'Infrastructure', 'Operating Environment', 
            'Research', 'Development', 'Government Strategy', 'Commercial']

# 获取不同 Cluster 的均值 (假设df已正确加载)
cluster_mean = df.groupby('Cluster')[features].mean()

# 设置标签和角度
labels = features
num_labels = len(labels)
angles = np.linspace(0, 2*np.pi, num_labels, endpoint=False).tolist()
angles += angles[:1]  # 闭合角度

# 设置画布大小和清晰度 (调整宽度以适应一行展示)
plt.figure(figsize=(18, 5), dpi=300)  # 增加宽度，高度减小
plt.subplots_adjust(wspace=0.25, hspace=0.1)  # 调整子图间距

# 使用更专业的配色方案
colors_list = ['#0080FF', '#0080FF', '#0080FF', '#0080FF', '#0080FF', '#0080FF']

# 绘制雷达图
for i, cluster in enumerate(cluster_mean.index):
    values = cluster_mean.loc[cluster].values.tolist()
    values += values[:1]  # 闭合数值
    
    # 创建子图 (调整为一行多列)
    ax = plt.subplot(1, len(cluster_mean.index), i+1, polar=True)  # 改为1行布局
    
    # 绘制雷达图线条和填充
    ax.plot(angles, values, linewidth=2.5, color=colors_list[i % len(colors_list)], 
            label=cluster, alpha=0.8)
    ax.fill(angles, values, color=colors_list[i % len(colors_list)], alpha=0.2)
    
    # 设置网格和标签
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=9)  # 适当减小字体
    ax.set_rlabel_position(180/num_labels)  # 调整径向标签位置
    
    # 设置坐标轴范围和样式
    ax.set_ylim(0, 100)
    ax.set_title(f'集群 {cluster}', fontsize=11, fontweight='bold', pad=10)
    
    # 美化坐标轴
    ax.spines['polar'].set_color('#cccccc')
    ax.tick_params(axis='both', which='major', pad=8)
    
    # 设置径向刻度
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d%%'))

# 设置总图标题
plt.suptitle('不同类别国家AI指数的各个维度对比', fontsize=16, fontweight='bold', y=1.05)

# 调整布局
plt.tight_layout()
plt.show()



# 设置总图标题
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False

# 定义统一的蓝色系颜色列表
blue_colors = ['#E0FFFF', '#B0E0E6', '#87CEFA', '#4682B4', '#00008B']

# 假设已有数据：df, region_ct, income_ct, political_ct
# （此处省略数据读取和计算过程，需确保已有这三个交叉表）
region_ct = pd.crosstab(df['Cluster'], df['Region'])
income_ct = pd.crosstab(df['Cluster'], df['Income group'])
political_ct = pd.crosstab(df['Cluster'], df['Political regime'])
# 创建大图
fig, axes = plt.subplots(3, 1, figsize=(15, 12), sharey=True, sharex=True)
fig.suptitle('不同类别国家的地区、收入群体、政治体制分布分析', fontsize=18, fontweight='bold', y=0.95)

# 1. 绘制地区分布（带右下角图例）
region_ct.plot(kind='barh', stacked=True, ax=axes[0], color=blue_colors, legend=True)
axes[0].set_title('地区分布', fontsize=14)
axes[0].set_xlabel('')  # 隐藏X轴标签
axes[0].set_ylabel('Cluster类别', fontsize=12)
axes[0].legend(
    title='地区分类',
    loc='lower right',               # 右下角位置
    fontsize=10, 
    title_fontsize=12,
    frameon=True,
    borderpad=1
)

# 2. 绘制收入群体分布（带右下角图例）
income_ct.plot(kind='barh', stacked=True, ax=axes[1], color=blue_colors, legend=True)
axes[1].set_title('收入群体分布', fontsize=14)
axes[1].set_xlabel('')  # 隐藏X轴标签
axes[1].set_ylabel('')
axes[1].legend(
    title='收入分类',
    loc='lower right',
    fontsize=10, 
    title_fontsize=12,
    frameon=True,
    borderpad=1
)

# 3. 绘制政治体制分布（带右下角图例）
political_ct.plot(kind='barh', stacked=True, ax=axes[2], color=blue_colors, legend=True)
axes[2].set_title('政治体制分布', fontsize=14)
axes[2].set_xlabel('国家数量', fontsize=12)
axes[2].set_ylabel('')
axes[2].legend(
    title='政治体制分类',
    loc='lower right',
    fontsize=10, 
    title_fontsize=12,
    frameon=True,
    borderpad=1
)

# 优化布局（右侧留出空间）
plt.tight_layout()
plt.subplots_adjust(top=0.9, right=0.85)  # 调整右侧边距
plt.show()

#%%




#%%数据看板

import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Map, Page
from pyecharts.globals import ThemeType

# 读取数据
df = pd.read_csv('D:/python经济/ai_job_dataset.csv')

# 计算每个国家的平均薪资
country_stats = df.groupby('company_location')['salary_usd'].mean().reset_index()

# 国家名称中英文映射字典（使用 pyecharts 支持的标准名称）
country_name_map = {
    'China': 'China',
    'Canada': 'Canada',
    'Switzerland': 'Switzerland',
    'India': 'India',
    'France': 'France',
    'United States': 'United States',
    'United Kingdom': 'United Kingdom',
    'Germany': 'Germany',
    'Japan': 'Japan',
    'Australia': 'Australia',
    'South Korea': 'South Korea',
    'Netherlands': 'Netherlands',
    'Sweden': 'Sweden',
    'Denmark': 'Denmark',
    'Norway': 'Norway',
    'Finland': 'Finland',
    'Belgium': 'Belgium',
    'Austria': 'Austria',
    'Italy': 'Italy',
    'Spain': 'Spain'
}

# 准备世界地图数据
map_data = []
for index, row in country_stats.iterrows():
    country = row['company_location']
    if country in country_name_map:
        map_data.append([country_name_map[country], row['salary_usd']])

# 创建世界地图
world_map = (
    Map(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width='1200px', height='800px'))
    .add(
        series_name="平均薪资",
        data_pair=map_data,
        maptype="world",
        label_opts=opts.LabelOpts(is_show=False),
        itemstyle_opts=opts.ItemStyleOpts(color="#323c48", border_color="#111")
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="不同国家AI岗位平均薪资分布"),
        visualmap_opts=opts.VisualMapOpts(
            min_=country_stats['salary_usd'].min(),
            max_=country_stats['salary_usd'].max(),
            range_color=["#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027", "#a50026"]
        ),
        toolbox_opts=opts.ToolboxOpts(is_show=True)
    )
)

# 创建页面来组合图表
page = Page()
page.add(world_map)

# 保存为 HTML 文件
page.render("D:/python经济/ai_job_world_avg_salary_dashboard.html")


#%%


#%%
'''
描述性分析
'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

# 设置中文字体支持（确保中文正常显示）
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 读取数据
df = pd.read_csv('D:/python经济/ai_job_dataset.csv')

# 检查数据结构
print("数据列名:", df.columns.tolist())

# 计算每个职位的数量
if 'job_title' in df.columns:
    value_counts = df['job_title'].value_counts().reset_index()
    value_counts.columns = ['job_title', 'Count']
else:
    print("错误：数据中没有找到'Job_Title'列，请检查列名")
    exit()

# 按照数量排序（可选，使图表更美观）
value_counts = value_counts.sort_values('Count', ascending=True)

# 创建画布和子图
fig, ax = plt.subplots(figsize=(12, 7))

# 生成渐变色（使用viridis色彩映射）
norm = plt.Normalize(value_counts['Count'].min(), value_counts['Count'].max())
colors = cm.viridis(norm(value_counts['Count'].values))

# 绘制柱状图
bars = ax.barh(value_counts['job_title'], value_counts['Count'], color=colors)

# 添加标题和标签
ax.set_title('各职位数量统计', fontsize=16, pad=15)
ax.set_xlabel('数量', fontsize=12, labelpad=10)
ax.set_ylabel('职位名称', fontsize=12, labelpad=10)

# 添加数值标签
for bar in bars:
    width = bar.get_width()
    ax.text(width + 1, bar.get_y() + bar.get_height()/2,
            f'{int(width)}', ha='left', va='center', fontsize=10)

# 添加颜色条（显示颜色与数值的对应关系）
sm = cm.ScalarMappable(cmap='viridis', norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label('职位数量', rotation=270, labelpad=20)

# 调整布局
plt.tight_layout()

# 显示图形
plt.show()


# 计算每个行业的数量，假设行业列名为'Industry'，可根据实际调整
value_counts = df['industry'].value_counts().reset_index()
value_counts.columns = ['industry', 'Count']

# 按照数量排序（可选，让图表更美观，与目标图排序一致可调整 ascending 参数）
value_counts = value_counts.sort_values('Count', ascending=True)

# 创建画布和子图
fig, ax = plt.subplots(figsize=(10, 6))

# 生成渐变色（使用 Plasma 色彩映射）
norm = plt.Normalize(value_counts['Count'].min(), value_counts['Count'].max())
colors = cm.plasma(norm(value_counts['Count'].values))

# 绘制纵向（垂直）柱状图
bars = ax.bar(
    value_counts['industry'], 
    value_counts['Count'], 
    color=colors
)

# 添加标题和标签，与目标图标题风格匹配
ax.set_title('各行业数量统计', fontsize=16, pad=15)
ax.set_xlabel('行业', fontsize=12, labelpad=10)
ax.set_ylabel('数量', fontsize=12, labelpad=10)

# 设置 x 轴刻度标签旋转角度，避免重叠
plt.xticks(rotation=45, ha='right')

# 添加数值标签
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2., 
        height + 1, 
        f'{int(height)}', 
        ha='center', 
        va='bottom', 
        fontsize=10
    )

# 添加颜色条（显示颜色与数值的对应关系）
sm = cm.ScalarMappable(cmap='plasma', norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
cbar.set_label('Count', rotation=270, labelpad=20)

# 调整布局
plt.tight_layout()

# 显示图形
plt.show()


skills = df['required_skills'].str.split(', ')
unique_skills = set()
for skill_list in skills:
    unique_skills.update(skill_list)
skill_to_index = {skill: index for index, skill in enumerate(unique_skills)}

skill_matrix = np.zeros((len(df), len(unique_skills)))
for i, skill_list in enumerate(skills):
    for skill in skill_list:
        if skill in skill_to_index:
            skill_matrix[i, skill_to_index[skill]] = 1

# 将技能矩阵与原数据合并
skill_df = pd.DataFrame(skill_matrix, columns=list(unique_skills))
# 统计每个技能的占比（计算每列的和，再除以总样本数得到占比）
skill_counts = skill_matrix.sum(axis=0)
total_jobs = len(df)
skill_ratios = skill_counts / total_jobs

# 将占比转换为可排序的格式并取前十
skill_ratio_dict = {skill: ratio for skill, ratio in zip(unique_skills, skill_ratios)}
# 按占比降序排序，取前十
sorted_skills = sorted(skill_ratio_dict.items(), key=lambda x: x[1], reverse=True)[:10]
labels = [skill for skill, _ in sorted_skills]
sizes = [ratio for _, ratio in sorted_skills]

# 绘制饼状图，尝试还原目标配色风格（手动映射颜色，可根据实际微调）
# 这里手动定义与目标图风格接近的颜色，可根据需要调整
norm = plt.Normalize(min(sizes), max(sizes))
colors = cm.plasma(norm(sizes))
fig, ax = plt.subplots(figsize=(8, 6))
wedges, texts, autotexts = ax.pie(
    sizes, 
    labels=labels, 
    autopct='%1.1f%%',  # 显示百分比，保留1位小数
    startangle=140,  # 饼图起始角度，接近目标图
    colors=colors
)
# 设置百分比标签字体为白色
for text in autotexts:
    text.set_color('white')
    text.set_fontweight('bold')  # 可选：加粗字体增强可读性
# 设置标题，与目标图标题一致
ax.set_title("技能需求分布", fontsize=16, pad=20)

# 调整图例位置（避免与饼图重叠），与目标图图例位置类似
ax.legend(wedges, labels, title="Skills", loc="center left", bbox_to_anchor=(1, 0.5))

# 优化布局
plt.tight_layout()

# 显示图形
plt.show()


#%%



#%%
'''
随机森林
'''
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.tree import export_graphviz
import graphviz
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import time  # 添加时间模块

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 设置Graphviz路径（根据你的实际安装路径修改）
graphviz_path = r'C:\Program Files\Graphviz\bin'  # 典型的Windows安装路径
import os
os.environ["PATH"] += os.pathsep + graphviz_path

# 1. 读取并预处理数据
df = pd.read_csv(r"D:\python经济\ai_job_dataset.csv")

# 特征与目标变量
X = df[['experience_level', 'employment_type', 'company_location',
        'company_size', 'employee_residence', 'remote_ratio',
        'required_skills', 'education_required', 'years_experience',
        'industry', 'job_description_length', 'benefits_score']]
y = df['salary_usd']

# 编码类别特征
categorical_cols = X.select_dtypes(include=['object']).columns
for col in categorical_cols:
    X[col] = LabelEncoder().fit_transform(X[col])

# 2. 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 记录训练开始时间
start_time = time.time()

# 3. 训练随机森林
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# 记录训练结束时间并计算耗时
end_time = time.time()
training_time = end_time - start_time

# 4. 预测测试集
y_pred = rf.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100  # 平均绝对百分比误差
accuracy = 100 - mape  # 预测准确率

# 打印评估指标和训练时间
print(f"均方误差 (MSE): {mse:.2f}")
print(f"决定系数 (R²): {r2:.2f}")
print(f"平均绝对误差 (MAE): {mae:.2f}")
print(f"预测准确率: {accuracy:.2f}%")
print(f"模型训练时间: {training_time:.2f} 秒")

# 4. 获取特征重要性并排序
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
import networkx as nx

feature_importance = rf.feature_importances_
importance_df = pd.DataFrame({
    '特征': X.columns,
    '重要性': feature_importance
}).sort_values(by='重要性', ascending=False)

print("特征重要性排名:")
print(importance_df)


# 预测结果与真实值差异分析（绘制散点图）
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=2)
plt.title('随机森林预测结果与真实值差异分析')
plt.xlabel('真实值')
plt.ylabel('预测值')
plt.show()


#%%



#%%
#随机森林优化一
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.tree import export_graphviz
import graphviz
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 设置Graphviz路径（根据你的实际安装路径修改）
graphviz_path = r'C:\Program Files\Graphviz\bin'  # 典型的Windows安装路径
import os
os.environ["PATH"] += os.pathsep + graphviz_path

# 1. 读取并预处理数据
df = pd.read_csv(r"D:\python经济\ai_job_dataset.csv")

skills = df['required_skills'].str.split(', ')
unique_skills = set()
for skill_list in skills:
    unique_skills.update(skill_list)
skill_to_index = {skill: index for index, skill in enumerate(unique_skills)}

skill_matrix = np.zeros((len(df), len(unique_skills)))
for i, skill_list in enumerate(skills):
    for skill in skill_list:
        if skill in skill_to_index:
            skill_matrix[i, skill_to_index[skill]] = 1

# 将技能矩阵与原数据合并
skill_df = pd.DataFrame(skill_matrix, columns=list(unique_skills))

# 特征与目标变量
X = df[['experience_level', 'employment_type', 'company_location',
        'company_size', 'employee_residence', 'remote_ratio',
        'required_skills', 'education_required', 'years_experience',
        'industry', 'job_description_length', 'benefits_score']]

X = pd.concat([X, skill_df], axis=1)  
y = df['salary_usd']

# 编码类别特征
categorical_cols = X.select_dtypes(include=['object']).columns
for col in categorical_cols:
    X[col] = LabelEncoder().fit_transform(X[col])

# 2. 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. 训练随机森林
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# 4. 预测测试集
y_pred = rf.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100  # 平均绝对百分比误差
accuracy = 100 - mape  # 预测准确率


# 打印评估指标
print(f"均方误差 (MSE): {mse:.2f}")
print(f"决定系数 (R²): {r2:.2f}")
print(f"平均绝对误差 (MAE): {mae:.2f}")
print(f"预测准确率: {accuracy:.2f}%")



#%%
#随机森林优化二
# 读取文件
import pandas as pd

# 直接读取 CSV 文件为 DataFrame
df1 = pd.read_csv('D:/python经济/ai_job_dataset.csv')

# 读取 Excel 文件
excel_file2 = pd.ExcelFile('D:/python经济/AI_index_db.xlsx')
df2 = excel_file2.parse('AI_index_db')

# 将 df2 的列名 Country 修改为 company_location，以便进行合并
df2.rename(columns={'Country': 'company_location'}, inplace=True)

# 合并数据，这里使用左连接，以 df1 为主，保留 df1 的所有行
merged_df = pd.merge(df1, df2, on='company_location', how='left')

# 将结果保存为 Excel 文件
merged_df.to_excel('D:/python经济/ai_job_dataset_merged.xlsx', index=False)


import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# 读取数据
df = pd.read_excel('D:/python经济/ai_job_dataset_merged.xlsx')

# 确定特征和目标变量
X = df.drop(['salary_usd', 'job_id', 'posting_date', 'application_deadline', 'salary_currency'], axis=1)
y = df['salary_usd']

# 划分数值型和分类变量列
numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns
categorical_cols = X.select_dtypes(include=['object']).columns

# 对数值型列进行缺失值填充，对分类变量进行顺序编码
preprocessor = ColumnTransformer(
    transformers=[
        ('num', SimpleImputer(strategy='mean'), numeric_cols),
        ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), categorical_cols)
    ])

# 创建包含预处理和随机森林回归的管道
rf_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                              ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))])

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 训练模型
rf_pipeline.fit(X_train, y_train)

# 在测试集上进行预测
y_pred = rf_pipeline.predict(X_test)

# 计算评估指标
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100  # 平均绝对百分比误差
accuracy = 100 - mape  # 预测准确率

# 打印评估指标
print(f"均方误差 (MSE): {mse:.2f}")
print(f"决定系数 (R²): {r2:.2f}")
print(f"平均绝对误差 (MAE): {mae:.2f}")
print(f"预测准确率: {accuracy:.2f}%")

# 获取随机森林模型
rf_model = rf_pipeline.named_steps['regressor']  # 添加这一行，正确获取模型

# 获取特征重要性
feature_names = rf_pipeline[:-1].get_feature_names_out()
importances = rf_model.feature_importances_
indices = np.argsort(importances)[::-1]  # 降序排列

# 验证特征数量是否匹配
print(f"特征名称数量: {len(feature_names)}")
print(f"特征重要性数量: {len(importances)}")

# 显示特征重要性排序结果（只显示有效索引）
print("\n随机森林特征重要性排名：")
for f in range(min(12, len(indices))):  # 显示前10个特征
    index = indices[f]
    if index < len(feature_names):
        feature_name = feature_names[index]
        importance = importances[index]
        print(f"{f+1}. {feature_name}: {importance:.4f}")
    else:
        print(f"警告：索引 {index} 超出特征名称范围")
        

#%%



#%%
'''
XGBOOST
'''
#pip install shap

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import shap
import matplotlib.pyplot as plt
import time  # 添加时间模块

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 读取数据
df = pd.read_csv(r"D:\python经济\ai_job_dataset.csv")

# 提取特征和目标变量
X = df[['experience_level', 'employment_type', 'company_location', 'company_size', 'employee_residence',
        'remote_ratio', 'required_skills', 'education_required', 'years_experience', 'industry',
        'job_description_length', 'benefits_score']]

y = df['salary_usd']

# 对类别型特征进行编码
categorical_cols = X.select_dtypes(include=['object']).columns
for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 记录训练开始时间
train_start_time = time.time()

# 创建基准XGBoost回归模型并训练
base_model = xgb.XGBRegressor(objective='reg:squarederror', random_state=42)
base_model.fit(X_train, y_train)

# 记录训练结束时间并计算训练耗时
train_end_time = time.time()
train_time = train_end_time - train_start_time

# 预测并评估基准模型
y_pred_base = base_model.predict(X_test)

# 计算完整评估指标
mse_base = mean_squared_error(y_test, y_pred_base)
r2_base = r2_score(y_test, y_pred_base)
mae_base = mean_absolute_error(y_test, y_pred_base)
mape_base = np.mean(np.abs((y_test - y_pred_base) / y_test)) * 100
accuracy_base = 100 - mape_base

# 打印评估指标和训练时间
print("基准模型性能:")
print(f"均方误差 (MSE): {mse_base:.2f}")
print(f"决定系数 (R²): {r2_base:.2f}")
print(f"平均绝对误差 (MAE): {mae_base:.2f}")
print(f"预测准确率: {accuracy_base:.2f}%")
print(f"模型训练时间: {train_time:.2f} 秒")


#XGBOOST优化
# 设置K折交叉验证
kfold = KFold(n_splits=5, shuffle=True, random_state=42)

# 定义要优化的参数网格
param_grid = {
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0],
    'n_estimators': [100, 200]
}

# 创建XGBoost回归模型
xgb_reg = xgb.XGBRegressor(objective='reg:squarederror', random_state=42)

# 执行网格搜索
grid_search = GridSearchCV(
    estimator=xgb_reg,
    param_grid=param_grid,
    cv=kfold,
    scoring='neg_mean_squared_error',
    verbose=1,
    n_jobs=-1
)

# 拟合训练数据
grid_search.fit(X_train, y_train)

# 输出最优参数
print("\n最优参数组合:")
for param, value in grid_search.best_params_.items():
    print(f"{param}: {value}")

# 使用最优参数的模型进行预测
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)

# 计算均方误差和 R² 得分
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# 计算预测准确率（误差在10%以内的样本比例）
accuracy = np.mean(np.abs(y_pred - y_test) / y_test < 0.1) * 100

print("\n优化后模型性能:")
print(f'均方误差(MSE)：{mse:.2f}')
print(f'R² 得分：{r2:.2f}')
print(f'预测准确率(误差在10%以内)：{accuracy:.2f}%')


# 可视化预测结果与实际值的对比
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.7)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
plt.xlabel('实际薪资 (USD)')
plt.ylabel('预测薪资 (USD)')
plt.title('XGBOOST预测结果与真实值差异')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# SHAP分析
explainer = shap.TreeExplainer(best_model)
shap_values = explainer.shap_values(X_test)


# 绘制每个单个特征散点图，表现特征值与 shap 值的关系
# 获取特征数量
num_features = len(X_test.columns)


# 2.1 绘制 shap 值的 summary plot，显示每个特征的小提琴图
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_test, plot_type='violin', show=False)
plt.title('SHAP值的summary plot（小提琴图）')
plt.tight_layout()
plt.savefig("shap_violin_plot.pdf", format='pdf', bbox_inches='tight', dpi=300)
plt.show()


#每个特征值的散点图
# 计算子图的行数和列数
num_cols = 4  # 可以根据需要调整每行的子图数量
num_rows = 3

# 创建一个包含多个子图的画布
fig, axes = plt.subplots(num_rows, num_cols, figsize=(25, 5 * num_rows))
axes = axes.flatten()  # 将二维的 axes 数组展平为一维

for i, col in enumerate(X_test.columns):
    ax = axes[i]
    shap.dependence_plot(col, shap_values, X_test, ax=ax, show=False)
    ax.set_title(f'{col} 特征值与 SHAP 值的关系')

# 隐藏多余的子图（如果有）
for j in range(i + 1, len(axes)):
    axes[j].axis('off')

plt.tight_layout()
plt.savefig("shap_all_features_dependence.pdf", format='pdf', bbox_inches='tight', dpi=300)
plt.show()


# 3. 新增：Force Plot（力图） - 解释单个样本的预测
# 选择一个样本进行解释（例如，预测薪资最高的样本）
sample_idx = np.argmax(y_pred)  # 或手动选择样本索引，如 sample_idx = 0

# 创建力图
sample_idx = np.argmax(y_pred)
plt.figure(figsize=(15, 5))
shap.force_plot(
    explainer.expected_value,  # 基础值（全局平均预测）
    shap_values[sample_idx],   # 该样本的SHAP值
    X_test.iloc[sample_idx],   # 该样本的特征值
    feature_names=X_test.columns,
    matplotlib=True,
    show=False
)
plt.title(f'样本 {sample_idx} 的预测解释（薪资: {y_pred[sample_idx]:.2f} 美元）')
plt.tight_layout()
plt.savefig(f"shap_force_plot_sample_{sample_idx}.pdf", format='pdf', bbox_inches='tight', dpi=300)
plt.show()





# 绝对贡献堆叠图
model = xgb.XGBRegressor(objective='reg:squarederror', random_state=42)
model.fit(X_train, y_train)

# SHAP 分析
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)  
feature_names = X_test.columns.tolist()

# 构建 SHAP 分析所需的 DataFrame
df_shap = pd.DataFrame(shap_values, columns=feature_names)
df_shap['salary_usd'] = y_test.reset_index(drop=True)  
df_shap = df_shap.sort_values('salary_usd').reset_index(drop=True)

# 绘制绝对贡献堆叠图（取绝对值）
plt.figure(figsize=(15, 8))
# 对 SHAP 值取绝对值
df_shap_abs = df_shap.drop('salary_usd', axis=1).abs()  
# 按列累加生成堆叠效果
stacked_data = df_shap_abs.cumsum(axis=1)  

# 自定义渐变色配色（可根据喜好调整）
import matplotlib.colors as mcolors  
cmap = mcolors.LinearSegmentedColormap.from_list(
    'custom_cmap', 
    ['#4B0082', '#800080', '#483D8B', '#1E3A99', '#4682B4', 
     '#48D1CC', '#40E0D0', '#32CD32', '#98FB98', '#FFFF00', '#FFD700'],
    N=len(feature_names)
)

# 绘制每个特征的堆叠区域
for i, feat in enumerate(feature_names):
    if i == 0:
        plt.fill_between(
            df_shap.index, 
            0, 
            stacked_data[feat], 
            label=feat, 
            alpha=0.7,
            edgecolor='black',  
            linewidth=0.5,
            color=cmap(i)  
        )
    else:
        plt.fill_between(
            df_shap.index, 
            stacked_data.iloc[:, i-1], 
            stacked_data[feat], 
            label=feat, 
            alpha=0.7,
            edgecolor='black',  
            linewidth=0.5,
            color=cmap(i)  
        )

# 坐标轴与标题设置
plt.xlabel('样本索引（按薪资升序排列）', fontsize=12, fontweight='bold')
plt.ylabel('SHAP 值绝对值之和', fontsize=12, fontweight='bold')
plt.title('所有样本的特征SHAP贡献绝对堆叠图（按薪资排序）', fontsize=14, fontweight='bold')

# 图例设置
plt.legend(
    title='特征', 
    title_fontsize=12, 
    fontsize=10, 
    bbox_to_anchor=(1.05, 1),  
    loc='upper left', 
    frameon=True,  
    borderpad=1,  
    labelspacing=0.8  
)

plt.tight_layout()  
plt.savefig('shap_stack_absolute_all_samples.pdf', format='pdf', bbox_inches='tight')
plt.show()


# 绘制相对贡献堆叠图（百分比）
# 计算每个样本的总 SHAP 绝对值（行求和）
total_shap_abs = df_shap_abs.sum(axis=1)  
df_shap_rel = df_shap_abs.div(total_shap_abs, axis=0) * 100  
# 计算每个特征的相对贡献（百分比）
df_shap_rel = df_shap_abs.div(total_shap_abs, axis=0) * 100  

# 按列累加生成堆叠效果
stacked_data_rel = df_shap_rel.cumsum(axis=1)  

# ---------------------------
# 绘制相对贡献堆叠图
# ---------------------------
plt.figure(figsize=(15, 8))

# 自定义渐变色配色
cmap = mcolors.LinearSegmentedColormap.from_list(
    'custom_cmap', 
    ['#4B0082', '#800080', '#483D8B', '#1E3A99', '#4682B4', 
     '#48D1CC', '#40E0D0', '#32CD32', '#98FB98', '#FFFF00', '#FFD700'],
    N=len(feature_names)
)

# 绘制每个特征的堆叠区域
for i, feat in enumerate(feature_names):
    if i == 0:
        plt.fill_between(
            df_shap.index, 
            0, 
            stacked_data_rel[feat], 
            label=feat, 
            alpha=0.7,
            edgecolor='black',  
            linewidth=0.5,
            color=cmap(i)  
        )
    else:
        plt.fill_between(
            df_shap.index, 
            stacked_data_rel.iloc[:, i-1], 
            stacked_data_rel[feat], 
            label=feat, 
            alpha=0.7,
            edgecolor='black',  
            linewidth=0.5,
            color=cmap(i)  
        )

# 坐标轴与标题设置
plt.xlabel('样本索引（按薪资升序排列）', fontsize=12, fontweight='bold')
plt.ylabel('SHAP 贡献占比（%）', fontsize=12, fontweight='bold')
plt.title('所有样本的特征SHAP贡献相对堆叠图（按薪资排序）', fontsize=14, fontweight='bold')

# 图例设置
plt.legend(
    title='特征', 
    title_fontsize=12, 
    fontsize=10, 
    bbox_to_anchor=(1.05, 1),  
    loc='upper left', 
    frameon=True,  
    borderpad=1,  
    labelspacing=0.8  
)

plt.tight_layout()
plt.savefig('shap_stack_relative_all_samples.pdf', format='pdf', bbox_inches='tight')
plt.show()


#%%



#%%

'''
文本分析
'''
#pip install wordcloud
#pip install jieba
from collections import Counter
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import jieba
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import numpy as np

# 读取新的停用词文件
with open('D:/python经济/Python期末/stopwords.txt', 'r', encoding='utf-8') as file:
    new_stopwords = [line.strip() for line in file.readlines()]

# 读取原始的中文停用词文件
with open("D:/python经济/Python期末/cn_stopwords.txt", 'r', encoding='utf-8') as file:
    stopwords = [line.strip() for line in file.readlines()]

# 合并停用词
all_stopwords = set(stopwords + new_stopwords)

# 读取文本数据
try:
    excel_file = pd.ExcelFile("D:/python经济/Python期末/MAIMAIAI.xlsx")
    # 获取所有工作表名
    sheet_names = excel_file.sheet_names

    # 假设数据在第一个工作表，提取文本内容
    df = excel_file.parse(sheet_names[0])

    # 根据实际情况选择文本所在列（示例：合并所有字符串列）
    text_columns = df.select_dtypes(include='object')  # 选择文本列
    text = ' '.join(text_columns.astype(str).values.flatten())  # 合并所有文本
except Exception as e:
    print(f"读取 Excel 失败: {e}")
    text = ""  # 读取失败时设为空

# 文本预处理：去除特殊字符和数字
text = re.sub(r'[^\u4e00-\u9fa5]', ' ', text)

# 使用 jieba 进行分词
words = jieba.cut(text)

# 过滤停用词
filtered_words = [word for word in words if word not in all_stopwords and len(word) > 1]

# 统计词频
word_freq = Counter(filtered_words)
word_freq_df = pd.DataFrame(word_freq.items(), columns=['Word', 'Frequency'])

# 按照频率降序排序
word_freq_df = word_freq_df.sort_values(by='Frequency', ascending=False)

# 保存为 Excel 文件
excel_path = r'D:/python经济/Python期末/word_frequency.xlsx'
word_freq_df.to_excel(excel_path, index=False)
print(f"词频统计结果已保存至: {excel_path}")

# 获取前 100 个高频词
top_100_words = word_freq.most_common(100)
print("前100个高频词：", top_100_words)

# 输出前100个高频词
print("前50个高频词及其词频：")
for word, freq in top_100_words:
    print(f"{word}: {freq}")

# 生成词云图
wordcloud = WordCloud(font_path = r"‪C:\Windows\Fonts\simhei.ttf", width=800, height=400, background_color='white').generate_from_frequencies(dict(top_100_words))

# 显示词云图
plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('词云图')
plt.show()

#%%