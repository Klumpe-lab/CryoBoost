
from fastai.learner import load_learner
from fastai.vision.utils import get_image_files
from torch.utils.data import DataLoader
from fastai.vision.core import PILImage,ToTensor
from fastai.vision.data import ImageDataLoaders
from fastai.vision.augment import Normalize
from fastai.vision.data import imagenet_stats
from fastai.vision.all import vision_learner
from fastai.vision.all import xresnet18
from fastai.metrics import accuracy,error_rate
from torch import torch
from pathlib import Path
import matplotlib.pyplot as plt
import timm
import seaborn as sns
from sklearn.metrics import precision_score, recall_score, accuracy_score,f1_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix
from tqdm import tqdm
from starfile import read as starread   
import mrcfile
from PIL import Image
import os
from concurrent.futures import ProcessPoolExecutor
import mrcfile
from PIL import Image
from skimage.transform import resize
import numpy as np
import pandas as pd

def mrc_to_pil_image(mrc_path,sz):
    """
    Convert an MRC file to a PIL Image object.

    Parameters:
    - mrc_path: Path to the MRC file.

    Returns:
    - A PIL Image object.
    """
    
    with mrcfile.open(mrc_path, permissive=True) as mrc:
        image_array = mrc.data
        from skimage.transform import resize
        image_array = resize(image_array, (sz, sz), anti_aliasing=True)
        image_array = (image_array -image_array.mean())
        if image_array.std() != 0:
            image_array=image_array / image_array.std()
        # Convert to uint8 if the image is not in this format. Adjust according to your data range.
        image_array = (image_array - image_array.min()) / (image_array.max() - image_array.min()) * 255.0
        image_array = image_array.astype('uint8')
        # Create a PIL Image from the NumPy array
        pil_image = Image.fromarray(image_array)
        return pil_image


def getTiltImagePathFromTiltStar(pathToStarFile: str, pathToRelionProj: str) -> pd.Series:
    """
    Reads a RELION tilt series STAR file and returns a pandas Series containing the paths to the tilt images.

    Parameters:
    - pathToStarFile (str): Path to the RELION tilt series STAR file.
    - pathToRelionProj (str): Path to the RELION project folder.

    Returns:
    - A pandas Series containing the paths to the tilt images.
    """
    st = starread(pathToStarFile)
    tilts = pd.Series([])
    for ts in st["rlnTomoTiltSeriesStarFile"]:
        stts = starread(os.path.join(pathToRelionProj, ts))
        #tmp = os.path.join(pathToRelionProj, stts["rlnMicrographName"])
        tmp=pathToRelionProj + "/" + stts['rlnMicrographName']
        tilts = pd.concat([tilts, tmp])

    return tilts, len(st)




def mrc_to_pil_image_parallel(mrc_path_sz):
    """
    Convert an MRC file to a PIL Image object. This function is designed to be called in parallel.
    
    Parameters:
    - mrc_path_sz: A tuple containing the MRC file path and the target size (sz).
    
    Returns:
    - A PIL Image object.
    """
    mrc_path, sz = mrc_path_sz
    with mrcfile.open(mrc_path, permissive=True) as mrc:
        image_array = mrc.data
        image_array = resize(image_array, (sz, sz), anti_aliasing=True)
        image_array = (image_array - image_array.mean())
        if image_array.std() != 0:
            image_array = image_array / image_array.std()
        image_array = (image_array - image_array.min()) / (image_array.max() - image_array.min()) * 255.0
        image_array = image_array.astype('uint8')
        pil_image = Image.fromarray(image_array)
        return pil_image

def mrcFilesToPilImageStackParallel(mrcFiles, sz, max_workers=20):
    """
    Convert MRC files to PIL Image objects in parallel.
    
    Parameters:
    - mrcFiles: A list of paths to MRC files.
    - sz: Target size for the PIL images.
    
    Returns:
    - A list of PIL Image objects.
    """
    
    with ProcessPoolExecutor(max_workers) as executor:
        pil_images = list(executor.map(mrc_to_pil_image_parallel, [(mrc_path, sz) for mrc_path in mrcFiles]))
    return pil_images


def predictPilImageStack(pilImageStack,learn):
    """
    Predict the class of a PIL image stack using a fastai learner.

    Parameters:
    - pilImageStack (PIL Image): The PIL image stack to predict.
    - learn (fastai learner): The fastai learner to use for prediction.
    
    Returns:
    - tuple: A tuple containing the predicted labels and probabilities.
    """
    test_dl = learn.dls.test_dl(pilImageStack, with_labels=False,batch_tfms=Normalize.from_stats(*imagenet_stats))
    preds, _ = learn.get_preds(dl=test_dl)
    decoded_preds = preds.argmax(dim=-1)
    pred_labels = [learn.dls.vocab[pred] for pred in decoded_preds]
    pred_probs = [max(pred).item() for pred in preds]
    return pred_labels,pred_probs
    

def predict_tilts(ts,model,sz=384,batchSize=50,gpu=3,max_workers=20):
    """
    Predict the class of a PIL image stack using a fastai learner.

    Parameters:
    pilImageStack (PIL Image): The PIL image stack to predict.
    learn (fastai learner): The fastai learner to use for prediction.

    Returns:
    tuple: A tuple containing the predicted labels and probabilities.
    """
    torch.cuda.set_device(gpu) 
    print("loading model:",model)
    learn =load_learner(model)
    _=learn.model.eval()
    #print("reading:",tilseriesStar)
    #tiltspath,nrTomo=getTiltImagePathFromTiltStar(tilseriesStar,relionProj)
    tiltspath=ts.getMicrographMovieNameFull()
    print("found:",str(len(tiltspath)),"tilts from",str(ts.nrTomo),'tomograms')
    
    #Custom dataloader refused to work in fastAI switched to direct prediction
    #Images get transformed to pilImages and the batch wise predicted
    nrBatch=round(len(tiltspath)/batchSize)
    if nrBatch<1:
        nrBatch=1
    
    batches = np.array_split(tiltspath,nrBatch )
    all_pLabels = []
    all_pProb = []
    for i, batch in enumerate(tqdm(batches, desc="Predicting Tilts"), 1):
        pilImageBatch=mrcFilesToPilImageStackParallel(batch,sz,max_workers)
        pLables,pProb=predictPilImageStack(pilImageBatch,learn)
        all_pLabels.extend(pLables)
        all_pProb.extend(pProb)
        
    df = pd.DataFrame({
    'cryoBoostDlLables': all_pLabels,
    'cryoBoostDlProbabilities': all_pProb,
    'cryoBoostKey': tiltspath
    })
    
    
    ts.addColumns(df)
        
    return ts    
        