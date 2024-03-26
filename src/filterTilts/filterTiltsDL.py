

def filterTiltsDL(tilseriesStar,relionProj,model,clmethod):
    if (clmethod=="binary"):
        from src.deepLearning.predictTilts_Binary import predict_tilts
        lables,probs,titlspath=predict_tilts(tilseriesStar,relionProj,model,batchSize=50,gpu=3,max_workers=20)
    if (clmethod=="oneclass"):    
        assert("not implemented yet")
 
    return lables,probs,titlspath
