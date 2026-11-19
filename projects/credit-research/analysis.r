library("fUnitRoots")
library(readxl)
x <- read_excel("D:/金融计量MATLAB/EX1/lunwenshuju.xlsx")
xt1 <- ts(x$RealGDP,start = c(2010,01))
xt2 <- ts(x$同业拆借利率,start = c(2010,01))
xt3 <- ts(x$`固定资产投资额累计增长(%)`,start = c(2010,01))
xt4 <- ts(x$`社会消费品零售总额当期值(亿元)`,start = c(2010,01))
#ADF检验
adfTest(xt1,lag=1,type = "c")
adfTest(xt2,lag=1,type = "c")
adfTest(xt3,lag=1,type = "c")
adfTest(xt4,lag=1,type = "c")
xt3 <- diff(log(xt3))
xt4 <- diff(log(xt4))

#协整检验
moni <- lm(xt1~xt3+xt4)
moni
adfTest(moni$residuals,lag = 1,type = "c")

