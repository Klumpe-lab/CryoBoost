from src.rw.librw import tiltSeriesMeta
import os

def filterTitls(tilseriesStar,relionProj='',pramRuleFilter=None,model=None,plot=None,outputFolder=None,probThr=0.1,probAction="assingToGood",threads=24):
    ts=tiltSeriesMeta(tilseriesStar,relionProj)
    if os.path.exists(outputFolder+"tiltseries_filtered.star"):
         tsExist=tiltSeriesMeta(outputFolder+"tiltseries_filtered.star")
         ts.reduceToNonOverlab(tsExist)
         if len(ts.tilt_series_df)==0:
             print("nothing to do")
             return
         print(ts.tilt_series_df.rlnTomoName)
        
    #plotTiltStat(ts,outputFolder)
    threads=int(threads)
    if (pramRuleFilter!=None):
        from src.filterTilts.filterTiltsRule import filterTiltsRule
        ts=filterTiltsRule(ts,pramRuleFilter,plot)

    if (model!=None):
        from src.filterTilts.filterTiltsDL import filterTiltsDL
        ts=filterTiltsDL(ts,model,'binary',outputFolder,plot,probThr,probAction,threads)
    
    if os.path.exists(outputFolder+"tiltseries_filtered.star"):
        tsExist.mergeTiltSeries(ts)
        ts=tsExist
    
    ts.writeTiltSeries(outputFolder+"tiltseries_filtered.star")
    
def plotTiltStat(ts,outputFolder,plot=None):
    import matplotlib.pyplot as plt
    import os
    if (plot==None):
        return
    #dummy plot replaced by michael's code
    ts.all_tilts_df.reset_index().plot(kind='scatter', x='rlnTomoNominalStageTiltAngle', y='rlnCtfMaxResolution', title='Scatter Plot using Pandas')
    plt.savefig(outputFolder+ os.path.sep +'tiltseriesStatistic.pdf')
    pass
    
    
def plotFilterTiltsResults(ts,outputFolder,classLabelName=None,predScoreLabelName=None,titlNameLabel=None,plot=False):
    if (plot==False):
        return
    
    from src.deepLearning.predictTilts_Binary import mrcFilesToPilImageStackParallel   
    #from src.deepLearning.predictTilts_Binary import mrcFilesToPilImageS  
    
    pred_lables=ts.all_tilts_df[classLabelName]
    if (predScoreLabelName is not None):
        pred_probs=ts.all_tilts_df.cryoBoostDlProbability
    
    
    if (titlNameLabel is not None):
        pred_Name=ts.all_tilts_df[titlNameLabel]    
    
    titlspath=ts.getMicrographMovieNameFull()
   
    from matplotlib import pyplot as plt
    import numpy as np
    maxRows=150
    num_images = len(pred_lables)
    num_cols = 3  # Number of columns in the matrix
    num_rows = (num_images // num_cols)  # Calculate number of rows needed
    if (num_rows>maxRows):
        num_rows=maxRows
    
    pil_images=mrcFilesToPilImageStackParallel(titlspath,384)
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(15, 5*num_rows))
    perm = np.random.permutation(num_images)
    for i, ax in enumerate(axs.flat):
        if i < num_images:
            ind=i ##ind=perm[i]
            img = pil_images[ind]
            ax.imshow(img,cmap='gray')
            if (predScoreLabelName is not None and  titlNameLabel is not None):
                axTitleStr=f'{pred_Name[ind]}, Pred: {pred_lables[ind]}, Prob: {pred_probs[ind]:.2f}'
            if (predScoreLabelName is not None and titlNameLabel is None):
                axTitleStr=f'Pred: {pred_lables[ind]}, Prob: {pred_probs[ind]:.2f}'
            if (predScoreLabelName is None and titlNameLabel is None):
                axTitleStr=f'Pred: {pred_lables[ind]}'    
            
            ax.set_title(axTitleStr) 
            
            img_size = img.shape[-2:]  
            rect_width = img_size[1] * 0.98  
            rect_height = img_size[0] * 0.98
            rect_x = (img_size[1] - rect_width) / 2  
            rect_y = (img_size[0] - rect_height) / 2 
            
            if pred_lables[ind] == 'good':
                color = 'g'  # Green for correct prediction
            else:
                color = 'r'  # Red for incorrect prediction """
            rect = plt.Rectangle((rect_x, rect_y), rect_width, rect_height, linewidth=4, edgecolor=color, facecolor='none')
            ax.add_patch(rect)
            ax.axis('off')

        else:
            ax.axis('off')  # Hide empty subplots
    plt.tight_layout()
    fig.savefig(f'{outputFolder}/logfile.pdf')
    #plt.show()   
    


