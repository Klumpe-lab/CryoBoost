import os
from src.filterTilts.libFilterTilts import plotFilterTiltsResults

def filterTiltsDL(ts,model,clmethod,outputfolder,plot=None,threads=24):
    
    if (clmethod=="binary"):
        from src.deepLearning.predictTilts_Binary import predict_tilts
        if (model=="default"):
            model=os.getenv("CRYOBOOST_HOME")+"/data/models/model.pkl"
        ts=predict_tilts(ts,model,batchSize=60,gpu=0,max_workers=threads)
        
    if (clmethod=="oneclass"):    
        assert("not implemented yet")
    
    #plotFilterTiltsResults(ts,outputfolder,plot)
    filterParams = {"cryoBoostDlLabel": ("good")}
    ts.filterTilts(filterParams)
    
    return ts


