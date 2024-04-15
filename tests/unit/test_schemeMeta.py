from src.rw.librw import schemeMeta


def test_readScheme():
    inputScheme='config/master_scheme/'
    sc=schemeMeta(inputScheme)
    assert (sc.jobs_in_scheme == ['importmovies', 'motioncorr', 
                                 'ctffind','feature_analysis','exclude_rule_based', 
                                 'aligntilts', 'reconstruction']).all()

def test_writeScheme():
    inputScheme='config/master_scheme/'
    output = 'tmpOut/testScheme/'
    
    sc=schemeMeta(inputScheme)
    sc.write_scheme(output)
    scnew=schemeMeta(output)
    
    assert (sc.jobs_in_scheme == scnew.jobs_in_scheme).all()   
    for job in sc.jobs_in_scheme:
        assert (sc.job_star_dict[job]['joboptions_values'] == scnew.job_star_dict[job]['joboptions_values']).all().all()
        

    