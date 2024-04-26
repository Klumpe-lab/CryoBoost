from src.rw.librw import schemeMeta
import shutil,os

def test_readScheme():
    inputScheme='config/Schemes/relion_tomo_prep/'
    sc=schemeMeta(inputScheme)
    assert (sc.jobs_in_scheme == ['importmovies', 'motioncorr', 
                                 'ctffind','filtertilts', 
                                 'aligntilts', 'reconstruction']).all()

def test_writeScheme():
    inputScheme='config/Schemes/relion_tomo_prep/'
    output = 'tmpOut/testScheme/'
    
    if ((output[0]!='/') and ('tmpOut' in output) and os.path.exists(output)): 
        shutil.rmtree(output)
        
    sc=schemeMeta(inputScheme)
    sc.write_scheme(output)
    scnew=schemeMeta(output)
    
    assert (sc.jobs_in_scheme == scnew.jobs_in_scheme).all()   
    for job in sc.jobs_in_scheme:
        assert (sc.job_star[job].dict['joboptions_values'] == scnew.job_star[job].dict['joboptions_values']).all().all()
 
def test_filterScheme():
     inputScheme='config/Schemes/relion_tomo_prep/'
     nodesToFilter={0:"importmovies",1:"motioncorr",2:"ctffind",
                    3:"aligntilts",4:"reconstruction"}
     
     sc=schemeMeta(inputScheme)
     scFilt=sc.filterSchemeByNodes(nodesToFilter)
     
     
     assert list(nodesToFilter.values()) == list(scFilt.jobs_in_scheme)     

    