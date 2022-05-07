library(shiny)
library(FuzzyR)
fis = newfis('medical', fisType = 'tsk', andMethod = "prod");

fis <- addvar(fis, 'input', 'temperature', c(30, 45), "singleton.fuzzification");
fis <- addvar(fis, 'input', 'headache', c(0,10),  "singleton.fuzzification");
fis <- addvar(fis, 'output', 'Urgency', c(0,100));


fis <- addmf(fis, 'input', 1, 'very_low', 'trapmf', c(26, 29, 33, 35));
fis <- addmf(fis, 'input', 1, 'low', 'trimf', c(33, 35, 36.5));
fis <- addmf(fis, 'input', 1, 'normal', 'trimf', c(35.5, 36.5, 37.5));
fis <- addmf(fis, 'input', 1, 'high', 'trimf', c(36.5, 38, 40));
fis <- addmf(fis, 'input', 1, 'very_high', 'trapmf', c(38.5, 40, 46, 48));


fis <- addmf(fis, 'input', 2, 'normal', 'gaussmf', c(1.5, 0));
fis <- addmf(fis, 'input', 2, 'mild', 'gaussmf', c(1.5, 5));
fis <- addmf(fis, 'input', 2, 'severe', 'gaussmf', c(1.5, 10));

fis <- addmf(fis, 'output', 1, 'slight', 'linearmf', c(0,0,0.2));
fis <- addmf(fis, 'output', 1, 'medium', 'linearmf', c(45, 0,0.2));
fis <- addmf(fis, 'output', 1, 'emergency', 'linearmf', c(80, 0, 2));

rulelist = rbind(c(1,3,3,1,1),c(5,3,3,1,1),c(2,2,2,1,1),c(4,2,2,1,1), c(3,1,1,1,1))
fis <- addrule(fis,rulelist)
data = read.table("data.csv",header=T)
urgency = evalfis(data$A,fis)[1]

#par(mfrow = c(3,1))
#plotmf(fis, 'input', 1, main = 'service')
#plotmf(fis, 'input', 2, main = 'food')
#plotmf(fis, 'output', 1, main = 'tip')
#gensurf(fis)
