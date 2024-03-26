

def filterTitls(tilseriesStar,relionProj,model,plot,outputFolder):
    if (model!=None):
        from src.filterTilts.filterTiltsDL import filterTiltsDL
        lables,probs,titlspath=filterTiltsDL(tilseriesStar,relionProj,model,'binary')
        plotFilterTiltsResults(lables,probs,titlspath,outputFolder)


def plotFilterTiltsResults(pred_lables,pred_probs,titlspath,outputFolder):

    from src.deepLearning.predictTilts_Binary import mrcFilesToPilImageStackParallel
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
    
    


        
#main function
def main():      
    #tilseriesStar = '/fs/pool/pool-plitzko3/Michael/01-Data/relion/231117_Ribo_Vfischeri_Oda/CtfFind/job007/tilt_series_ctf.star'
    tilseriesStar = 'data/tilts/tilt_series_ctf.star'
    relionProj='./'
    model="data/models/model.pkl"
    filterTitls(tilseriesStar,relionProj,model,1,1)

if __name__ == '__main__':
    main()
            
        
        


# # %%load dataset for trainin


# pathTrainDat="/fs/pool/pool-plitzko3/fbeck/cElegans/full1kTomosAreAlg/relion5/testSquid/sort1/003_IniSortVB/TrainDsN/balanced/1/"
# print("loading Dataset 1 for training",pathTrainDat)

# dls = ImageDataLoaders.from_folder(pathTrainDat, valid='val', 
#     batch_tfms=Normalize.from_stats(*imagenet_stats))
# dls.show_batch()


# # %%load dataset for trainin
# learn = vision_learner(dls,xresnet18,metrics=[accuracy,error_rate])
# #learn.fit_one_cycle(10)
# learn.fine_tune(15)
# learn.export('/fs/pool/pool-fbeck/projects/4TomoPipe/rel5Pipe/src/protoTypes/model.pkl')



# # %%load other model 

# learn =load_learner('/fs/pool/pool-fbeck/projects/4TomoPipe/rel5Pipe/src/protoTypes/model.pkl')
# learn.model.eval()


# # %% predict files from folder
# folder_path='/fs/pool/pool-plitzko3/fbeck/cElegans/full1kTomosAreAlg/relion5/testSquid/sort1/003_IniSortVB/TrainDsN/balanced/1/val/good/'
# #folder_path='/fs/pool/pool-chlamy/users/fbeck/relion5/full/manSort2/sort1/002_reSortCl/TrainDsN/balanced/1/val/good/'
# image_files = get_image_files(folder_path)
# #folder_path2='/fs/pool/pool-chlamy/users/fbeck/relion5/full/manSort2/sort1/002_reSortCl/TrainDsN/balanced/1/val/bad/'
# folder_path2='/fs/pool/pool-plitzko3/fbeck/cElegans/full1kTomosAreAlg/relion5/testSquid/sort1/003_IniSortVB/TrainDsN/balanced/1/val/bad/'
# image_files2 = get_image_files(folder_path2)

# image_files=image_files+image_files2





# # %% generate stack from mrc


# import mrcfile
# from PIL import Image
# from pathlib import Path
# from starfile import read as starread


# # Example usage
# starFilePath = '/fs/pool/pool-plitzko3/Michael/01-Data/relion/231117_Ribo_Vfischeri_Oda/CtfFind/job007/tilt_series_ctf.star'
# relionProj='/fs/pool/pool-plitzko3/Michael/01-Data/relion/231117_Ribo_Vfischeri_Oda'
# pil_images = get_pil_images_from_starFile(starFilePath,relionProj)




# # %% predict files from folder

# # Assuming 'learn' is your learner and 'image_files' is a list of image file paths
# #image_files = list(Path(folder_path).glob('*.png'))  # Example path and pattern

# # Step 1: Create a list of PILImage objects
# #images = [PILImage.create(image_file) for image_file in image_files]

# # Step 2: Convert list of images to a DataLoader
# test_dl = learn.dls.test_dl(pil_images, with_labels=False,batch_tfms=Normalize.from_stats(*imagenet_stats))

# #test_dl.after_batch.add(Normalize.from_stats(*imagenet_stats))

# # Step 3: Predict on the DataLoader
# preds, _ = learn.get_preds(dl=test_dl)

# # Decoding the predictions to get the class indices
# decoded_preds = preds.argmax(dim=-1)

# # Step 4: Convert decoded predictions to labels
# pred_labels = [learn.dls.vocab[pred] for pred in decoded_preds]

# # Simplified extraction of the highest probability for each prediction
# pred_probs = [max(pred).item() for pred in preds]

# # Step 5: Extract actual labels from folder names
# #actual_labels = [image_file.parent.name for image_file in image_files]

# # Verification: Ensure lengths match to avoid 'list index out of range' errors
# #assert len(pred_labels) == len(pred_probs) == len(actual_labels) == len(images), "Mismatch in lengths of outputs."


# # %% evaluate prediction
# cm = confusion_matrix(actual_labels,pred_labels)
# print(cm)

# # print prediction on
# le = LabelEncoder()
# actLabN=le.fit_transform(actual_labels)
# predLabN=le.fit_transform(pred_labels)
# ac=round(accuracy_score(actLabN,predLabN),2)
# ps=round(precision_score(actLabN,predLabN),2)
# rc=round(recall_score(actLabN,predLabN),2)
# f1=round(f1_score(actLabN,predLabN),2)

# print("accuracy:",ac,"precision:",ps,"recall",rc,"F1:",f1) 


# # %% plot images
# print("potting random selection of images")
# maxRows=15
# num_images = len(pred_labels)
# num_cols = 3  # Number of columns in the matrix
# num_rows = -(-num_images // num_cols)  # Calculate number of rows needed
# if (num_rows>maxRows):
#     num_rows=maxRows

# fig, axs = plt.subplots(num_rows, num_cols, figsize=(15, 5*num_rows))
# perm = np.random.permutation(num_images)
# for i, ax in enumerate(axs.flat):
#     if i < num_images:
#         ind=perm[i]
#         #img = PILImage.create(image_files[ind])
#         img = pil_images[ind]
#         ax.imshow(img,cmap='gray')
#         ax.set_title(f'Pred: {pred_labels[ind]}, Prob: {pred_probs[ind]:.2f}')
#         img_size = img.shape[-2:]  # Get the height and width of the image
#         rect_width = img_size[1] * 0.98  # Increase width by 10%
#         rect_height = img_size[0] * 0.98# Increase height by 10%
#         rect_x = (img_size[1] - rect_width) / 2  # Center the rectangle horizontally
#         rect_y = (img_size[0] - rect_height) / 2  # Center the rectangle vertically
        
#         """ if pred_labels[ind] == actual_labels[ind]:
#             color = 'g'  # Green for correct prediction
#         else:
#             color = 'r'  # Red for incorrect prediction """
#         #rect = plt.Rectangle((rect_x, rect_y), rect_width, rect_height, linewidth=4, edgecolor=color, facecolor='none')
#         #ax.add_patch(rect)
#         ax.axis('off')

#     else:
#         ax.axis('off')  # Hide empty subplots
# plt.tight_layout()
# plt.show()   
# # %%
# def getTiltImagePathFromTiltStar(pathToStarFile,pathToRelionProj):
#     st=starread(pathToStarFile)
#     tilts=pd.Series([])
#     for ts in st['rlnTomoTiltSeriesStarFile']:
#         stts=starread(pathToRelionProj+"/"+ts)
#         tmp=pathToRelionProj + "/" + stts['rlnMicrographName']
#         tilts=pd.concat([tilts, tmp])
    
#     #tilts=tilts.tail(20)
#     return tilts,len(st)
    