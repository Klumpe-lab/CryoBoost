

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
    
# functions for the exclude tilts rules file
import os
import sys
import pandas as pd


def col_of_df_to_series(star_df, param):
    """
    looks into the ctf.star (already as df) and writes a list of the tilt_series star files containing the parameters.

    Args:
        star_df (pd.Dataframe): df of the contents of the tilt-series_ctf.star, containing the paths to the
        .star files of the individual tilts under "rlnTomoTiltSeriesStarFile".
        param (str): column label of df.
    
    Returns:
        series_of_param_values (pd.Series): pd.Series of the entries of star_df under param.
    
    Example:
    tilt_series_ctf_star_df = pd.DataFrame(
        {"rlnTomoName": [
            "Position_1", 
            "Position_2", 
            "Position_10",
            ], 
        "rlnTomoTiltSeriesStarFile": [
            "CtfFind/job003/tilt_series/Position_1.star",
            "CtfFind/job003/tilt_series/Position_2.star",
            "CtfFind/job003/tilt_series/Position_10.star",
            ],
            )
    
    The function will return: [
            "CtfFind/job003/tilt_series/Position_1.star",
            "CtfFind/job003/tilt_series/Position_2.star",
            "CtfFind/job003/tilt_series/Position_10.star",
            ]
    """
    series_of_param_values = pd.Series(star_df[param])
    return series_of_param_values


def series_higher_lower(series_of_values, range:tuple):
    """
    run through the entries of the given pd.Series and write a new vector of the same length. For this new
    vector, write 1 if the value is within the range, otherwise write 0.

    Args:
        series_of_values (pd.Series): series of values that should be tested.
        range (tubple): range as a cut-off where range[0] is the lower cut-off and range[1] the higher cut-off.
    
    Returns:
        higher_lower_series (pd.Series): series of 0s and 1s (0 = value was outside of range, 1 = value was inside).

    Example:
        series_of_values = pd.Series([1, 2, 3, 4, 5])
        range_ = (2, 4)

        The function will create a new pd.Series with the length 5, populated by 0. Then, it will iterate through the
        entries of the series_of_values and test whether it is true that they are >= 2 and <= 4 also ensures that the 
        entries are floats). If yes, True is saved, if not, False. Lastly, the newly created series will be set to 1 
        everywhere where the boolean is True and returned. 
    """
    higher_lower_series = pd.Series(0, index = series_of_values.index)
    mask_of_booleans = (series_of_values.astype(float) >= range[0]) & (series_of_values.astype(float) <= range[1])
    higher_lower_series[mask_of_booleans] = 1
    return higher_lower_series


def combine_vectors(df_0_1):
    """
    take a df of all pd.Series together created in series_higher_lower (one for each pparam) and find the indices
    where all vectors are 1.

    Args:
        df_0_1 (pd.Dataframe): a dataframe containing series of 0s and 1s, where 0s mean that a value at that index
        should be removed in future steps.

    Returns:
        indices_true (pd.Index): index object containing all indices where all series in the df are 1.

    Example:
        df_0_1 = pd.DataFrame({"a": vector_a, "b":vector_b, "c": vector_c})
        (with: 
        vector_a = pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1])
        vector_b = pd.Series([1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1])
        vector_c = pd.Series([1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1])
        )

        The function will create a pd.Series containing True where all rows (axis = 1) of df_0_1 are 1, and False
        if they do not. Then, it will get (and return) the indeces of df_0_1 where all_ones_df is True. In this case,
        pd.Index([0, 2, 3, 5, 7, 9, 10, 11, 14, 15, 16, 18, 19]) would be returned.
    """
    all_ones_df = (df_0_1 == 1).all(axis=1)
    # Find the indices where all values are 1
    indices_true = df_0_1.index[all_ones_df]
    return indices_true


def remove_tilts(star_file_df, indices_keep_tilts):
    """
    write a new df with only the entries of the all 1 indices_vector
    """
    new_df = pd.DataFrame(index = range(len(indices_keep_tilts)), columns = star_file_df.columns)
    i = 0
    for index in indices_keep_tilts:
        new_df.loc[i] = star_file_df.loc[index]
        i += 1
    return new_df    




        
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
    