from src.rw.librw import cbconfig
import pytest,os

def idfn(test_input,context):
    
    if (isinstance(test_input, dict)):
        key=list(test_input.keys())[0]
        value = str(test_input[key])
    else:
        key=""
        value = str(test_input)
   
    return f"{context['function_name']} {key}-{value}"

@pytest.mark.parametrize("test_input", 
                         [(("ctffind",2,"p.hpcl8",{'qsub_extra2': 24, 'nr_mpi': 48, 'qsub_extra4': 0, 'qsub_extra1': 2, 'qsub_extra3': 'p.hpcl8','qsub_extra5': '370G', 'nr_threads': 1} )), 
                          ],
                           ids=lambda val: idfn(val, {'function_name': 'cbconfig'}))
@pytest.mark.test_cbconfig
def test_cbconfigGetJobComputingParams(test_input):
    cbHOME=os.getenv("CRYOBOOST_HOME")
    conf=cbconfig(cbHOME+"/config/conf.yaml")
    compParams=conf.getJobComputingParams(test_input,True)
    print(compParams)
    #assert 1==1
    assert compParams==test_input[3]   