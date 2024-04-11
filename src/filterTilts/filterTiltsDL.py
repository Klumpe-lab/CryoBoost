from src.filterTilts.libFilterTilts import plotFilterTiltsResults

def filterTiltsDL(ts,model,clmethod,outputfolder,plot=None):
    if (clmethod=="binary"):
        from src.deepLearning.predictTilts_Binary import predict_tilts
        ts=predict_tilts(ts,model,batchSize=50,gpu=3,max_workers=20)
        
    if (clmethod=="oneclass"):    
        assert("not implemented yet")
    
    plotFilterTiltsResults(ts,outputfolder,plot)
    filterParams = {"cryoBoostDlLabel": ("good")}
    ts.filterTilts(filterParams)
    
    return ts
