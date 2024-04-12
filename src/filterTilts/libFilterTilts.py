from src.rw.librw import tiltSeriesMeta

def filterTitls(tilseriesStar,relionProj='',pramRuleFilter=None,model=None,plot=None,outputFolder=None):
    ts=tiltSeriesMeta(tilseriesStar,relionProj)
    
    if (pramRuleFilter!=None):
        from src.filterTilts.filterTiltsRule import filterTiltsRule
        ts=filterTiltsRule(ts,pramRuleFilter,plot)

    if (model!=None):
        from src.filterTilts.filterTiltsDL import filterTiltsDL
        ts=filterTiltsDL(ts,model,'binary',plot)
   
    ts.writeTiltSeries(outputFolder+"tiltseries_filtered.star")
    
    
    
def plotFilterTiltsResults(ts,outputFolder,plot):
    if (plot==None):
        return
    
    from src.deepLearning.predictTilts_Binary import mrcFilesToPilImageStackParallel
    
    pred_lables=ts.all_tilts_df.cryoBoostDlLabel
    pred_probs=ts.all_tilts_df.cryoBoostDlProbability
    titlspath=ts.getMicrographMovieNameFull
    pil_images=mrcFilesToPilImageStackParallel(titlspath,384)
    
    from matplotlib import pyplot as plt
    import numpy as np
    print("potting random selection of images")
    maxRows=30
    num_images = len(pred_lables)
    num_cols = 3  # Number of columns in the matrix
    num_rows = -(-num_images // num_cols)  # Calculate number of rows needed
    if (num_rows>maxRows):
        num_rows=maxRows

    fig, axs = plt.subplots(num_rows, num_cols, figsize=(15, 5*num_rows))
    perm = np.random.permutation(num_images)
    for i, ax in enumerate(axs.flat):
        if i < num_images:
            ind=i ##ind=perm[i]
            #img = PILImage.create(image_files[ind])
            img = pil_images[ind]
            ax.imshow(img,cmap='gray')
            ax.set_title(f'Pred: {pred_lables[ind]}, Prob: {pred_probs[ind]:.2f}') 
            #FileName: {titlspath[ind]}')
            #ax.set_title(f'F: {titlspath[ind]}')
            print(pred_lables[ind],'Prob:',pred_probs[ind],'F:'+titlspath[ind])
            img_size = img.shape[-2:]  # Get the height and width of the image
            rect_width = img_size[1] * 0.98  # Increase width by 10%
            rect_height = img_size[0] * 0.98# Increase height by 10%
            rect_x = (img_size[1] - rect_width) / 2  # Center the rectangle horizontally
            rect_y = (img_size[0] - rect_height) / 2  # Center the rectangle vertically
            
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
    fig.savefig(f'{outputFolder}/plot_results.pdf')
    #plt.show()   
    
