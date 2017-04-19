import matplotlib.pyplot as plt
import numpy as np
#import seaborn as sns

def drawLine(x,y,labels,xLabel,yLabel,title):
    f, ax = plt.subplots(1, 1, figsize=(10, 6), sharex=True)

    #f.tight_layout()
    #sns.set(style="darkgrid")

    palette = ['blue','orange','red','green','purple','pink']
    # for i in range(len(ax)):
    #     x1 = range(0, len(x))
        #ax.set_xlim(min(x1)-0.2,max(x1)+0.2)
        # mini = 10000;max = -10000
        # for label in labels:
        #     if mini>min(y[i][label]):
        #         mini = min(y[i][label])
        #     if max<max(y[i][label]):
        #         max = max(y[i][label])
        # ax[i].set_ylim(mini-0.25*(max-mini),max+0.25*(max-mini))
        # for j,label in enumerate(labels):
        #     if j%2==1:
        #         ax[i].plot(x1, y[i][label], color=palette[j/2], marker='.', label=label, markersize=12)
        #     else:
        #         ax[i].plot(x1, y[i][label], color=palette[j/2], marker='.', label=label,markersize=12,linestyle='--')
        # ax[0].set_ylabel(yLabel,fontsize=20)

    for xdata,ydata,lab,c in zip(x,y,labels,palette):
        ax.plot(xdata,ydata,color = c,label=lab)
    ind = np.arange(0,60,10)
    ax.set_xticks(ind)
    #ax.set_xticklabels(x)
    ax.set_xlabel(xLabel, fontsize=20)
    ax.set_ylabel(yLabel, fontsize=20)
    ax.tick_params(labelsize=16)
    #ax.tick_params(axs='y', labelsize=20)

    ax.set_title(title,fontsize=24)
    plt.grid(True)
    handles, labels1 = ax.get_legend_handles_labels()

    #ax[i].legend(handles, labels1, loc=2, fontsize=20)
    # ax.legend(loc=2,
    #        ncol=6,  borderaxespad=0.,fontsize=20)
    #ax[2].legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.,fontsize=20)
    ax.legend(loc='upper right',fontsize=20,shadow=True)
    plt.show()
    plt.close()

paths = ['SVD.txt','PMF.txt','EE.txt','RDML.txt']
files = ['EE['+str(i)+'] iteration.txt' for i in range(2,9)]
x = []
y = []

data = []
def normalize():
    for file in files:
        xdata = []
        with open(file) as f:
            for line in f:
                items = line.strip().split()
                rmse = items[2].split(':')[1]
                xdata.append(float(rmse))
        data.append(xdata)
    average = []
    for i in range(len(data[0])):
        total = 0
        for k in range(len(data)):
            total += data[k][i]
        average.append(str(i+1)+':'+str(float(total)/len(data))+'\n')
    with open('EE.txt','w') as f:
        f.writelines(average)



def readData():
    for file in paths:
        xdata = []
        ydata = []
        with open(file) as f:
            for line in f:
                items = line.strip().split(':')
                xdata.append(int(items[0]))
                rmse = float(items[1])
                ydata.append(float(rmse))
        x.append(xdata)
        y.append(ydata)




# x = [[1,2,3],[1,2,3]]
# y = [[1,2,3],[4,5,6]]
#normalize()
readData()
labels = ['SVD','PMF','EE','RDML',]
xlabel = 'Iteration'
ylabel = 'RMSE'

drawLine(x,y,labels,xlabel,ylabel,'')