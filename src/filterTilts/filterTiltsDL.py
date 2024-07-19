import os
from src.filterTilts.libFilterTilts import plotFilterTiltsResults

def filterTiltsDL(ts,model,clmethod,outputFolder,plot=None,probThr=0.1,probAction="assingToGood",threads=24):
    
    if (clmethod=="binary"):
        from src.deepLearning.predictTilts_Binary import predict_tilts
        if (model=="default"):
            model=os.getenv("CRYOBOOST_HOME")+"/data/models/model.pkl"
        ts=predict_tilts(ts,model,batchSize=60,gpu=0,probThr=probThr,probAction=probAction,max_workers=threads)
        
    if (clmethod=="oneclass"):    
        assert("not implemented yet")
    
    try:
        plotFilterTiltsResults(ts,outputFolder,classLabelName="cryoBoostDlLabel",predScoreLabelName="cryoBoostDlProbability",titlNameLabel="cryoBoostKey",plot=1,threads=threads)
    except Exception as exc:
        print("error plotting filter tilts result")
        print(exc)
    
    
    filterParams = {"cryoBoostDlLabel": ("good")}
    ts.filterTilts(filterParams)
    
    return ts


