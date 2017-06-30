import hyperflexcore.intelligence.guihandling as gh
import sys

if __name__ == '__main__':
    if len( sys.argv ) > 1:
        vsdn_id = int(sys.argv[ 1 ])  
    else:
        raise Exception('id required')
    handler = gh.ManagementGuiControllerHandler()
    handler.remove_vsdn(1, vsdn_id)
    
