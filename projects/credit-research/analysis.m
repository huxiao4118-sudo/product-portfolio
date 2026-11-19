clc
clear
tic
%% 加载工具箱
addpath('D:\金融计量MATLAB\EX1\VAR_Toolbox_2.0\VAR')
addpath('D:\金融计量MATLAB\EX1\VAR_Toolbox_2.0\Utils')
addpath('D:\金融计量MATLAB\EX1\VAR_Toolbox_2.0\Stats')
addpath('D:\金融计量MATLAB\EX1\VAR_Toolbox_2.0\Auxiliary')

%% 读取数据
load data.txt
load b.txt
% 同业拆借利率、CPI、信贷、GDP、M2 
% 信贷、CPI、GDP
%% 简化式VAR模型估计
nlag = 4;
const = 1;
[VAR, VARopt] = VARmodel(data,nlag,const); 

%% 短期零约束
VARopt.nsteps = 20; 
VARopt.ident = 'oir'; 
[IRF, VAR] = VARir(VAR,VARopt);

VARopt.ndraws = 1000; %设置抽样次数
VARopt.pctg = 90;%置信区间大小
[INF,SUP,MED,BAR] = VARirband(VAR,VARopt);

%% 脉冲响应
figure
for ii = 1:5 %变量序号
    for jj = 2:5 %冲击序号
    subplot(5,4,4*(ii-1)+jj-1)
        plot(1:20,MED(:,ii,jj),"Color",'k','LineWidth',1,'LineStyle','-')
        hold on
        plot(1:20,INF(:,ii,jj),"Color",'k','LineWidth',1,'LineStyle','--')
        hold on
        plot(1:20,SUP(:,ii,jj),"Color",'k','LineWidth',1,'LineStyle','--')
        hold on
        plot(1:20,zeros(20,1),"Color",'k','LineWidth',1,'LineStyle',':')

        if ii == 1  
            ylabel('同业拆借利率%')
        elseif ii == 2
            ylabel('通胀率%')
        elseif ii == 3
            ylabel('信贷增长率%')
        elseif ii == 4
            ylabel('产出增长率%')
        else
            ylabel('货币增长率%')
        end

       if jj == 2  
            title('总需求冲击')
        elseif jj == 3
            title('信贷供给冲击')
        elseif jj == 4
            title('总供给冲击')
        else
            title('货币政策冲击')
        end
        axis tight
        set(gca,'FontSize',10,'Color','none')
        grid on

    end
    end

%% 预测误差方差分解
[FEVD, VAR] = VARfevd(VAR,VARopt);
VARopt.ndraws = 1000; %设置抽样次数
VARopt.pctg = 90;%置信区间大小
[INF,SUP,MED,BAR] = VARfevdband(VAR,VARopt);

figure
for ii = 1:5 %变量序号
    for jj = 2:5 %冲击序号
    subplot(5,4,4*(ii-1)+jj-1)
        plot(1:20,MED(:,ii,jj),"Color",'k','LineWidth',1,'LineStyle','-')
        hold on
        plot(1:20,INF(:,ii,jj),"Color",'k','LineWidth',1,'LineStyle','--')
        hold on
        plot(1:20,SUP(:,ii,jj),"Color",'k','LineWidth',1,'LineStyle','--')
        hold on
        plot(1:20,zeros(20,1),"Color",'k','LineWidth',1,'LineStyle',':')

        if ii == 1  
            ylabel('同业拆借利率%')
        elseif ii == 2
            ylabel('通胀率%')
        elseif ii == 3
            ylabel('信贷增长率%')
        elseif ii == 4
            ylabel('产出增长率%')
        else
            ylabel('货币增长率%')
        end

       if jj == 2  
            title('总需求冲击')
        elseif jj == 3
            title('信贷供给冲击')
        elseif jj == 4
            title('总供给冲击')
        else
            title('货币政策冲击')
        end
        axis tight
        set(gca,'FontSize',10,'Color','none')
        grid on

    end
end

%% 符号约束
nlag = 4;
const = 1;
[VAR, VARopt] = VARmodel(b,nlag,const); 

% 信贷供给冲击
%              from        to          sign
   R(:,:,1) = [ 1           4            1          % 信贷
                1           4            1          % CPI
                0           0            0];        % GDP
                


VARopt.nsteps = 20;
VARopt.ndraws = 1000;  

SRout = SR(VAR,R,VARopt);

%% 脉冲响应
figure
for ii = 1:3 %变量序号
    for jj = 1:3 %冲击序号
    subplot(3,3,3*(ii-1)+jj)
        plot(1:20,SRout.IRFmed(:,ii,jj),"Color",'k','LineWidth',1,'LineStyle','-')
        hold on
        plot(1:20,SRout.IRFinf(:,ii,jj),"Color",'k','LineWidth',1,'LineStyle','--')
        hold on
        plot(1:20,SRout.IRFsup(:,ii,jj),"Color",'k','LineWidth',1,'LineStyle','--')
        hold on
        plot(1:20,zeros(20,1),"Color",'k','LineWidth',1,'LineStyle',':')

        if ii == 1  
            ylabel('信贷增长率%')
        elseif ii == 2
            ylabel('通胀率%')
        else ii == 3
            ylabel('产出增长率%')
       
        end

       if jj == 1  
            title('信贷供给冲击')
       elseif jj == 2
            title('总需求冲击')
       else jj == 3
            title('总供给冲击')
            
        end
        axis tight
        set(gca,'FontSize',10,'Color','none')
        grid on

    end
    end

%% 预测误差方差分解
[FEVD, VAR] = VARfevd(VAR,VARopt);
VARopt.ndraws = 1000; %设置抽样次数
VARopt.pctg = 90;%置信区间大小
[INF,SUP,MED,BAR] = VARfevdband(VAR,VARopt);

figure
for ii = 1:3 %变量序号
    for jj = 1:3 %冲击序号
    subplot(3,3,3*(ii-1)+jj)
        plot(1:20,SRout.FEVDmed(:,ii,jj),"Color",'k','LineWidth',1,'LineStyle','-')
        hold on
        plot(1:20,SRout.FEVDinf(:,ii,jj),"Color",'k','LineWidth',1,'LineStyle','--')
        hold on
        plot(1:20,SRout.FEVDsup(:,ii,jj),"Color",'k','LineWidth',1,'LineStyle','--')
        hold on
        plot(1:20,zeros(20,1),"Color",'k','LineWidth',1,'LineStyle',':')

        if ii == 1  
            ylabel('信贷增长率%')
        elseif ii == 2
            ylabel('通胀率%')
        else ii == 3
            ylabel('产出增长率%')
       
        end

       if jj == 1  
            title('信贷供给冲击')
       elseif jj == 2
            title('总需求冲击')
       else jj == 3
            title('总供给冲击')
            
        end
        axis tight
        set(gca,'FontSize',10,'Color','none')
        grid on

    end
end


%%符号约束下的BVAR
%脉冲响应
clc
clear
tic

load datac.txt
%信贷、消费、投资

addpath ('D:/金融计量MATLAB/EX1/BVAR_-master/cmintools')
addpath ('D:/金融计量MATLAB/EX1/BVAR_-master/bvartools')

xd=datac(:,1);
c=datac(:,2);
tz=datac(:,3);
y=[xd c tz];
lags        = 12;
options.hor = 24;
options.signs{1} = 'y(3,1:3,1)>0';
options.signs{2} = 'y(2,1:3,1)>0';
options.K        = 1000;
 
% run the BVAR
bvar1       = bvar_(datac,lags,options);
indx_sho              = 1;   
indx_var              = [2,3];
irfs_to_plot           = bvar1.ir_draws(indx_var,:,indx_sho,:);
options.varnames      = {'社会消费品零售总额增长率',"固定资产投资额增长率"}; 
options.shocksnames   = {'信贷冲击'};
options.conf_sig_1    = 0.9;   
plot_irfs_(irfs_to_plot,options)
pause;


%%长期约束下的历史分解
clc
clear
tic

addpath('D:\金融计量MATLAB\EX1\VAR_Toolbox_2.0\VAR')
addpath('D:\金融计量MATLAB\EX1\VAR_Toolbox_2.0\Utils')
addpath('D:\金融计量MATLAB\EX1\VAR_Toolbox_2.0\Stats')
addpath('D:\金融计量MATLAB\EX1\VAR_Toolbox_2.0\Auxiliary')
load datab.txt

nlag = 1;
const = 1;
[VAR, VARopt] = VARmodel(datab,nlag,const);
VARopt.nsteps = 20; %设置影响期数，脉冲的
VARopt.ident = 'bq'; %使用短期零约束
VARopt.ndraws = 1000; %设置抽样次数，运用自举法（boostrap）
VARopt.pctg = 90; 
[INF,SUP,MED,BAR] = VARirband(VAR,VARopt);

%历史分解
tim = 1:1:173; 
[IRF, VAR] = VARir(VAR,VARopt);
HD = VARhd(VAR);
GDP_hd = HD.shock(:,:,3);
datab_demean = datab-mean(datab) %剔除均值
figure
bar(tim,GDP_hd,'stacked') %堆叠
hold on
plot(tim,dataa_demean(:,1),"Color",'k','LineWidth',2,'LineStyle','-')
legend('消费冲击','投资冲击','总供给冲击')
legend("boxoff")
