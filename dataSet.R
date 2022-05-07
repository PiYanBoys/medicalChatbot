t = seq(30,45,1);
h = seq(0,10,1);
a = c();
for (i in t){
	for (j in h){
		a = rbind(a,c(i,j));
	}
}
result = evalfis(a,fis);

dataset = read.table("dataset",header=T)

error = result - dataset$C
se = error ^ 2
mse = sum(se) / 176
rmse = mse ^ 0.5

print("MSE=")
print(mse)
print("RMSE=")
print(rmse)