# -*- coding: utf-8 -*-
"""
Created on Wed May  7 14:12:17 2025

@author: huxiao
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
plt.style.use('seaborn-v0_8')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus']=False


df = pd.read_excel("C:/Users/huxiao/Desktop/TRD_Dalyr111.xlsx")
df['证券代码'] = df['证券代码'].astype(str).str.zfill(6)

# 按股票代码聚类并计算交易量总和
total_volume = df.groupby('证券代码')['日个股交易金额'].sum()

# 选出交易量最大的前20个
top_20_stocks = total_volume.nlargest(20)

# 获取前20个股票的代码
top_20_stock_codes = top_20_stocks.index

# 仅保留这20支股票的数据
df = df[df['证券代码'].isin(top_20_stock_codes)]

df['日收盘价_归一化'] = (df['日收盘价'] - df['日收盘价'].min()) / (df['日收盘价'].max() - df['日收盘价'].min())

df_cor = df[['证券代码','日收盘价_归一化','交易日期']]
reshaped_df_cor = df_cor.pivot(columns='证券代码', values='日收盘价_归一化',index='交易日期')

non_zero_values = reshaped_df_cor[reshaped_df_cor != 0].dropna(how='all')
min_value = non_zero_values.min().min()

# 将所有 0 替换为除 0 外的最小值
reshaped_df_cor = reshaped_df_cor.replace(0, min_value)
# 计算斯皮尔曼相关系数矩阵
code_to_name = {
    '300059': '东方财富',
    '300750': '宁德时代',
    '600519': '贵州茅台',
    '000063': '中兴通讯',
    '601127': '赛力斯',
    '300308': '中际旭创',
    '002594': '比亚迪电子',
    '603019': '中科曙光',
    '000977': '浪潮信息',
    '600030': '中信证券',
    '300339': '润和软件',
    '300502': '新易盛',
    '002261': '拓维信息',
    '300033': '同花顺',
    '000158': '常山北明',
    '601138': '工业富联',
    '002475': '立讯精密',
    '601318': '中国平安',
    '600839': '四川长虹',
    '601899': '紫金矿业'
}
reshaped_df_cor.columns = [code_to_name.get(col, col) for col in reshaped_df_cor.columns]
spearman_correlation_matrix = reshaped_df_cor.corr(method='spearman')
plt.figure(figsize=(10, 8))
plt.rcParams['figure.dpi'] = 300
sns.heatmap(spearman_correlation_matrix, annot=False, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('股票收益率斯皮尔曼相关性热力图')
plt.xlabel('证券代码')
plt.ylabel('证券代码')
plt.show()

reshaped_df_cor.iloc[:, :5].plot()
plt.title('归一化后的股票收盘价（示例）')
plt.show()




# 选取指定列（这里列名已经是公司名称）
selected_columns = [code_to_name.get(code, code) for code in ['300308', '000158', '002594', '300750', '600030', '000063']]
selected_df = reshaped_df_cor[selected_columns]

# 计算斯皮尔曼相关系数矩阵
spearman_correlation_matrix2 = selected_df.corr(method='spearman')

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 绘制热力图
plt.figure(figsize=(10, 2))
sns.heatmap(spearman_correlation_matrix2, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('投资组合斯皮尔曼相关性热力图')
plt.xlabel('公司名称')
plt.ylabel('公司名称') 
plt.show()

reshaped_df_cor.iloc[:, :5].plot()
plt.title('归一化后的股票收盘价（示例）')
plt.show()

'''
求夏普比率最大的资产组合
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# 计算日收益率
returns = reshaped_df_cor.pct_change().dropna()

# 计算协方差矩阵和平均收益率
cov_matrix = returns.cov()
mean_returns = returns.mean()

# 获取股票数量
num_stocks = reshaped_df_cor.shape[1]

# 定义风险无风险利率
risk_free_rate = 0.011

# 定义计算组合预期收益率、标准差和夏普比率的函数
def portfolio_stats(weights):
    portfolio_return = np.dot(weights, mean_returns) * 252
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std
    return portfolio_return, portfolio_std, sharpe_ratio

# 定义目标函数：最大化夏普比率
def negative_sharpe_ratio(weights):
    return -portfolio_stats(weights)[2]

# 约束条件：权重之和为 1
constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

# 权重范围：0 到 1
bounds = tuple((0, 1) for _ in range(num_stocks))

# 初始权重：等权重
initial_weights = np.ones(num_stocks) / num_stocks

# 优化求解
result = minimize(negative_sharpe_ratio, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

# 夏普比率最大的组合权重
optimal_weights = result.x

# 蒙特卡罗模拟生成随机组合
num_portfolios = 10000
portfolio_returns = []
portfolio_stds = []
portfolio_sharpe_ratios = []

for _ in range(num_portfolios):
    weights = np.random.random(num_stocks)
    weights /= np.sum(weights)
    ret, std, sharpe = portfolio_stats(weights)
    portfolio_returns.append(ret)
    portfolio_stds.append(std)
    portfolio_sharpe_ratios.append(sharpe)

# 绘制有效前沿
plt.figure(figsize=(12, 8))
plt.scatter(portfolio_stds, portfolio_returns, c=portfolio_sharpe_ratios, cmap='viridis')
plt.colorbar(label='夏普比率')
plt.xlabel('标准差')
plt.ylabel('预期收益率')
plt.title('有效前沿')

# 标记夏普比率最大的组合
optimal_return, optimal_std, _ = portfolio_stats(optimal_weights)
plt.scatter(optimal_std, optimal_return, marker='*', color='r', s=500, label='夏普比率最大组合')
plt.legend()

plt.show()

print("夏普比率最大的组合权重：", optimal_weights)




'''
历史模拟法
'''
def calculate_var_historical(prices, weights, confidence_level):
    # 计算每日收益率
    returns = prices.pct_change().dropna()
    # 计算组合每日收益率，考虑股票权重
    portfolio_returns = np.dot(returns, weights)
    # 排序收益率
    sorted_returns = np.sort(portfolio_returns)
    # 找到对应的百分位数
    var_index = int((1 - confidence_level) * len(sorted_returns))
    var_value = sorted_returns[var_index]
    return var_value


var_his = calculate_var_historical(reshaped_df_cor, confidence_level=0.99,weights = optimal_weights)
print("组合的在险价值（VAR）为:", var_his)
var_his2 = calculate_var_historical(reshaped_df_cor, confidence_level=0.95,weights = optimal_weights)
    
#绘制var的分布图
filtered_returns = returns[(returns >= -0.15) & (returns <= 0.15)].dropna().values.flatten()

# 绘制直方图
plt.hist(filtered_returns, bins=50, density=True, alpha=0.7)

# Plot VaR line
plt.axvline(x=var_his, color="red", linestyle="--", linewidth=2)
plt.axvline(x=var_his2, color="b", linestyle="--", linewidth=2)

# Add labels and title
plt.xlabel("Returns")
plt.ylabel("Frequency")
plt.title('历史模拟法计算VaR')
plt.show()
    
'''
方差协方差法
''' 
import numpy as np
import pandas as pd
from scipy.stats import norm

def calculate_var_covariance(reshaped_df_cor, confidence_level,weights):
    # 计算股票数量
    num_stocks = len(reshaped_df_cor.columns)
    # 计算每日收益率
    returns = reshaped_df_cor.pct_change().dropna()
    # 计算协方差矩阵
    cov_matrix = returns.cov()
    # 计算组合标准差
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    # 计算Z值
    z_value = norm.ppf(1 - confidence_level)
    # 计算VAR值
    var_value = z_value * portfolio_std
    return var_value

var_cov1 = calculate_var_covariance(reshaped_df_cor,confidence_level=0.99 ,weights = optimal_weights)
var_cov2 = calculate_var_covariance(reshaped_df_cor,confidence_level=0.95 ,weights = optimal_weights)
var_cov3 = calculate_var_covariance(reshaped_df_cor,confidence_level=0.99 ,weights = initial_weights)
var_cov4 = calculate_var_covariance(reshaped_df_cor,confidence_level=0.95 ,weights = initial_weights)


#绘制var的分布图
filtered_returns = returns[(returns >= -0.2) & (returns <= 0.2)].dropna().values.flatten()

# 绘制直方图
plt.hist(filtered_returns, bins=50, density=True, alpha=0.7)

# Plot VaR line
plt.axvline(x=var_cov1, color="red", linestyle="--", linewidth=2)
plt.axvline(x=var_cov2, color="b", linestyle="--", linewidth=2)
# Add labels and title
plt.xlabel("Returns")
plt.ylabel("Frequency")
plt.title('方差协方差法计算VaR')

# Show the plot
plt.show()

'''
蒙特卡罗模拟法
'''
def calculate_var_monte_carlo(prices, num_simulations=10000, confidence_level=0.95):
    num_stocks = len(reshaped_df_cor.columns)
    
    weights = optimal_weights

    # 计算每日收益率
    returns = prices.pct_change().dropna()
    # 计算均值和协方差矩阵
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    # 生成模拟路径
    simulated_returns = np.random.multivariate_normal(mean_returns, cov_matrix, num_simulations)
    # 计算组合模拟收益率
    portfolio_returns = np.dot(simulated_returns, weights)
    # 排序模拟收益率
    sorted_returns = np.sort(portfolio_returns)
    # 找到对应的百分位数
    var_index = int((1 - confidence_level) * len(sorted_returns))
    var_value = sorted_returns[var_index]
    return var_value

var_mon1 = calculate_var_monte_carlo(reshaped_df_cor,confidence_level=0.99)
var_mon2 = calculate_var_monte_carlo(reshaped_df_cor,confidence_level=0.95)

#绘制var的分布图
filtered_returns = returns[(returns >= -0.2) & (returns <= 0.2)].dropna().values.flatten()

# 绘制直方图
plt.hist(filtered_returns, bins=50, density=True, alpha=0.7)

# Plot VaR line
plt.axvline(x=var_mon1, color="red", linestyle="--", linewidth=2)
plt.axvline(x=var_mon2, color="b", linestyle="--", linewidth=2)
# Add labels and title
plt.xlabel("Returns")
plt.ylabel("Frequency")
plt.title('蒙特卡洛模拟法计算VaR')

# Show the plot
plt.show()


'''
与正态分布对比
'''
from scipy.stats import gaussian_kde, norm
# 绘制直方图
plt.hist(filtered_returns, bins=50, density=True, alpha=0.7)

# 拟合核密度曲线
density = gaussian_kde(filtered_returns)
xs = np.linspace(min(filtered_returns), max(filtered_returns), 200)
plt.plot(xs, density(xs), label='日收益率核密度曲线', color='green')
mean_returns = np.mean(filtered_returns)
std_returns = np.std(filtered_returns)

# 绘制正态分布曲线
plt.plot(xs, norm.pdf(xs, mean_returns, std_returns), 
         label=f'正态分布曲线', 
         color='orange', linewidth=2.5, linestyle='--', alpha=0.8)

# 添加标签和标题
plt.xlabel("Returns")
plt.ylabel("Frequency")
plt.title('日收益率与正态分布对比')
plt.legend()
plt.show()



# 回测最优权重的投资组合
def backtest_portfolio(prices, weights, initial_investment=1000000):
    # 计算每日收益率
    daily_returns = prices.pct_change().dropna()
    
    # 计算投资组合每日收益率
    portfolio_daily_returns = (daily_returns * weights).sum(axis=1)
    
    # 计算每日投资组合价值
    portfolio_value = initial_investment * (1 + portfolio_daily_returns).cumprod()
    
    # 计算累计收益率
    cumulative_return = (portfolio_value.iloc[-1] / initial_investment) - 1
    
    return portfolio_value, portfolio_daily_returns, cumulative_return

# 执行回测
initial_investment = 1000000  # 初始投资100万元
portfolio_value, portfolio_returns, cumulative_return = backtest_portfolio(
    reshaped_df_cor, optimal_weights, initial_investment
)

# 计算基准（等权重）投资组合的表现
equal_weights = np.ones(len(reshaped_df_cor.columns)) / len(reshaped_df_cor.columns)
benchmark_value, benchmark_returns, benchmark_cumulative_return = backtest_portfolio(
    reshaped_df_cor, equal_weights, initial_investment
)

# 计算最大回撤
def calculate_max_drawdown(portfolio_value):
    """计算最大回撤"""
    cumulative_returns = portfolio_value / portfolio_value.iloc[0]
    running_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns / running_max) - 1
    max_drawdown = drawdown.min()
    return drawdown, max_drawdown

drawdown, max_drawdown = calculate_max_drawdown(portfolio_value)
benchmark_drawdown, benchmark_max_drawdown = calculate_max_drawdown(benchmark_value)

# 可视化回测结果
plt.figure(figsize=(14, 10))

# 绘制投资组合价值变化
plt.subplot(2, 1, 1)
plt.plot(portfolio_value.index, portfolio_value, label='最优权重组合', color='blue')
plt.plot(benchmark_value.index, benchmark_value, label='等权重组合', color='gray', linestyle='--')
plt.title('投资组合价值变化')
plt.xlabel('日期')
plt.ylabel('资产价值 (元)')
plt.legend()
plt.grid(True)

# 添加统计数据
plt.annotate(f'最终价值: {portfolio_value.iloc[-1]:,.2f}元\n累计收益率: {cumulative_return*100:.2f}%\n最大回撤: {max_drawdown*100:.2f}%', 
             xy=(0.05, 0.95), xycoords='axes fraction',
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

plt.annotate(f'基准最终价值: {benchmark_value.iloc[-1]:,.2f}元\n基准累计收益率: {benchmark_cumulative_return*100:.2f}%\n基准最大回撤: {benchmark_max_drawdown*100:.2f}%', 
             xy=(0.05, 0.75), xycoords='axes fraction',
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

# 绘制回撤
plt.subplot(2, 1, 2)
plt.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3, label='最优权重组合回撤')
plt.fill_between(benchmark_drawdown.index, benchmark_drawdown, 0, color='gray', alpha=0.2, label='等权重组合回撤')
plt.title('投资组合回撤')
plt.xlabel('日期')
plt.ylabel('回撤比例')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# 打印回测结果统计
print("="*50)
print("投资组合回测结果统计")
print("="*50)
print(f"最优权重组合:")
print(f"  最终价值: {portfolio_value.iloc[-1]:,.2f}元")
print(f"  累计收益率: {cumulative_return*100:.2f}%")
print(f"  年化收益率: {(1+cumulative_return)**(252/len(portfolio_returns))-1:.2%}")
print(f"  夏普比率: {(portfolio_returns.mean()*252 - risk_free_rate)/(portfolio_returns.std()*np.sqrt(252)):.2f}")
print(f"  最大回撤: {max_drawdown*100:.2f}%")
print(f"  波动率: {portfolio_returns.std()*np.sqrt(252)*100:.2f}%")
print("")
print(f"等权重基准组合:")
print(f"  最终价值: {benchmark_value.iloc[-1]:,.2f}元")
print(f"  累计收益率: {benchmark_cumulative_return*100:.2f}%")
print(f"  年化收益率: {(1+benchmark_cumulative_return)**(252/len(benchmark_returns))-1:.2%}")
print(f"  夏普比率: {(benchmark_returns.mean()*252 - risk_free_rate)/(benchmark_returns.std()*np.sqrt(252)):.2f}")
print(f"  最大回撤: {benchmark_max_drawdown*100:.2f}%")
print(f"  波动率: {benchmark_returns.std()*np.sqrt(252)*100:.2f}%")















    