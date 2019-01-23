import urllib
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr, data
from .mention_pairs_extractor.html_page import HtmlPage
from .mention_pairs_extractor.extractor import FeatureExtractor
import array
import pandas as pd
import numpy as np
from rpy2.robjects import pandas2ri
pandas2ri.activate()
from .mention_pairs_extractor.graph_algorithm import solve_document_rwr
from .mention_pairs_extractor.filter_priors import filtered_priors_for_app

caret = importr('caret')
e1071 = importr('e1071')
randomForest = importr('randomForest')
glmnet = importr('glmnet')
kernlab = importr('kernlab')    
base = importr('base')
gbm = importr('gbm')
robjects.r('''
    get_prediction <-function(data.raw){
        data.raw[,c('scale','prec')] <- scale(data.raw[,c('scale','prec')], center = T, scale = T)
        rf_model <- readRDS("RFmodel2_with_sampling.rds")
        pred.RF = predict(rf_model, newdata=data.raw,  type='prob')
        data.raw$prob <- pred.RF$X1
    }''')

rf_model = robjects.r.readRDS("demo/parRF.rds") # Random Forest classifier with none sampling 
mention_type_classifier = robjects.r.readRDS("demo/mention_type_classifier.rds")
prediction_fn = robjects.globalenv['get_prediction']


def process_url(url,  threshold=0.5, rwr_algorithm = True, adaptive_filtering = True):
    results ={'url': url}
    try:
        with urllib.request.urlopen(url) as response:
               html = response.read()
               results = process_html(html, threshold=threshold, rwr_algorithm= rwr_algorithm, adaptive_filtering=adaptive_filtering)
        
    except:
        results ={"error" :"Could not download the webpage"}
    
    return results
def convert_factor(obj):
    """
    Taken from jseabold's PR: https://github.com/pydata/pandas/pull/9187
    """
    ordered = robjects.r["is.ordered"](obj)[0]
    categories = list(obj.levels)
    codes = np.asarray(obj) - 1  # zero-based indexing
    values = pd.Categorical.from_codes(codes, categories=categories,ordered=ordered)
    return values

def process_html(html_content, threshold=0.5, rwr_algorithm = True, adaptive_filtering = True):
    global prediction_fn, rf_model
    results = {'html_file': html_content}
    # load html content into document

    # extract mention pairs

    # call the classifier     

    html_page = HtmlPage(html_content, 1) #.decode('utf-8')
    print("page loaded")
    documents = html_page.create_documents()
    feature_extractor = FeatureExtractor(5, 0) 
    # pick 5 for k!
    #for eta the approx_sim :         0%        25%        50%        75%       100% 
    #                            -0.5985708  2.1250165  2.8879552  3.5073260  6.0000000 
    # Thus I picked 1

    documents = list(map(lambda x: feature_extractor.extract_features_for_document(x), documents))
    all_mention_pairs = list(map(lambda x: feature_extractor.extract_mention_pairs_with_features(x), documents))
    all_mention_pairs_flat = [mp for mp_lst in all_mention_pairs for mp in mp_lst]
    #print(all_mention_pairs_flat)

    text_mentions_with_features = list(map(lambda x: x.get_mention_features_for_classification_as_list(), documents))
    text_mentions_with_features_flat = [m for m_lst in text_mentions_with_features for m in m_lst]



    data = process_mention_pairs_for_classifier(all_mention_pairs_flat)
    mention_data = process_mentions_for_type_classifier(text_mentions_with_features_flat)
    if data.empty:
        results_text = html_page.get_html_with_annotations()
    else:

        #data_with_predictions = prediction_fn(data)
        # Now get the final results just by the classifier
        r_true = rpy2.robjects.BoolVector([True])
        #get predictions first
        predictions =robjects.r.predict(rf_model, newdata = data, type='prob' )
        # get mention types
        mention_type = robjects.r.predict(mention_type_classifier, newdata = mention_data, type='prob' )
 
        # print(mention_type)


        # confert the FactorVector to pandas dataframe
        #predictions = convert_factor(predictions)
        # record the predictions
        # for col in mention_type:
        #     print(col.rclass[0])
        # for col in predictions:
        #     print(col.rclass[0])
        #print(predictions)
        data['pr'] = np.asarray(predictions[1])
        #dif  percentage          rat       same         sum
        mention_data['perc_prob'] = np.asarray(mention_type[1])
        mention_data['rat_prob'] = np.asarray(mention_type[2])
        mention_data['sum_prob'] = np.asarray(mention_type[4])
        mention_data['dif_prob'] = np.asarray(mention_type[0])       
        mention_data['same_prob'] = np.asarray(mention_type[3])
        # filter the probabilities 
        #final_predictions = data.ix[data.pr  >  0.3] 
        #with pd.option_context('display.max_rows', None, 'display.max_columns', 3):
        #        print(final_predictions)
        #print(mention_data)
        if adaptive_filtering:
            filtered_data = filtered_priors_for_app(data, mention_data)
            filtered_data = process_filtered_data(filtered_data)
        else:
            filtered_data = data

        print("documents processed")
        for document in documents:
            solve(document, filtered_data, threshold, rwr_algorithm)

        results_text = html_page.get_html_with_annotations()
        
    #mention_pairs = extract_mention_pairs(html_content)
    #mention_pairs_processed= process_mention_pairs_for_classifier(mention_pairs)
    #predictions = predict_fn(mention_pairs_processed)

    # run the graph/ILP solver  
    #final_predictioins = graph_solver(predictions, 
    # return the results 
    results = {'results':results_text}
    #print(results_text)
    return results
def solve(document, data_with_prob, threshold, rwr_algorithm):
    print("Solving Document:%s"%document.doc_id)
    priors = data_with_prob[data_with_prob.doc_id == document.doc_id]
    #print(document.doc_id, priors)
    if rwr_algorithm:
        edges = document.get_all_edges()
        solve_document_rwr(priors,edges, document, threshold)
    else:
        solve_document(priors, document, threshold)
    # solve with the graph
    # write the solution to the documents 

def solve_document(priors, document, threshold):
    mentions = document.mentions
    for mention in mentions:
        #print("Solving for mention: %s"% mention.surface_form)
        candidates = priors[priors.mXId == str(mention.mention_id)]
        #print("candidates", candidates)
        if candidates.shape[0] ==1:
            #only a single candidate solve to it
            print("A single Solution Exists")
            pr = float(candidates['pr'].iloc[0] )
            if pr > threshold:
                mention.set_solution(candidates['mTid'].iloc[0], candidates['pr'].iloc[0])
                document.track_solution(mention)
                print("Only Single Candidate %s,%s"% mention.solution)
        elif candidates.shape[0] >1:
            print("Multiple Candidates")
            max_p = -1 
            winner = None
            for candidate, prior in candidates[['mTid', 'pr']].values:
                p = prior
                if p > max_p:
                    max_p = p
                    winner = candidate
            if max_p >= threshold:
                # resolve
                mention.set_solution(winner, max_p)
                document.track_solution(mention)
                print("Solution Found: %s,%s,%s"%(mention,winner, max_p))
        else:
            print("No Possible Solution")

def process_mentions_for_type_classifier(text_mentions):
    data = text_mentions
    col_names = ["doc_id","m_id","mod","precision", "scale", 
    "unit", "aggr_fun","glbl_perc","glbl_sum","glbl_diff", "glbl_rat","lcl_perc",
    "lcl_sum","lcl_diff", "lcl_rat","glbl_stats","glbl_finance","glbl_unit","glbl_temp",
    "lcl_stats","lcl_finance","lcl_unit","lcl_temp","exact_count"]
    data_frame = pd.DataFrame(data = data, columns = col_names)
    return data_frame

def process_filtered_data(filtered_data):
    data = filtered_data
    col_names = ['doc_id', 'mXId','mTid','no_scale_diff','diff_max','dif_sum','scale','prec','unit',
    'mod', 'aggr','ltokn','lnps','gtokn', 'gnps','surfaceform','approx_sim'
    ,'mx','mt','scalex','scalet','GT','aggrFunction', 'modApprox', 'modBound', 'modExact','modNone', 'pr', 'aggr_prob']
    data_frame = pd.DataFrame(data = data, columns = col_names)
    return data_frame

def process_mention_pairs_for_classifier(mention_pairs):
#create a data frame withe the following data
#no_scale_diff+diff_max+dif_sum+scale+prec+unit+modApprox+modBound+modExact+modNone+aggr+ltokn+lnps+gtokn+gnps+surfaceform
    data = []
    col_names =['doc_id', 'mXId','mTid','no_scale_diff','diff_max','dif_sum','scale','prec','unit',
    'mod', 'aggr','ltokn','lnps','gtokn', 'gnps','surfaceform','approx_sim'
    ,'mx','mt','scalex','scalet','GT','aggrFunction']
    for mention_pair in mention_pairs:
        item = mention_pair.get_as_list()
        #print(item, "item")
        data.append(item)

    data_frame = pd.DataFrame(data = data, columns = col_names)
    data_frame['modApprox']  = [1 if mod == 'approx'  else 0 for mod  in data_frame['mod']]
    data_frame['modBound']  = [1 if mod == 'bound'  else 0 for mod  in data_frame['mod']]
    data_frame['modExact']  = [1 if mod == 'exact'  else 0 for mod  in data_frame['mod']]
    data_frame['modNone']  = [1 if mod == 'None'  else 0 for mod  in data_frame['mod']]

    #print(data_frame.dtypes)
    #print(data_frame.size)
    #print(data_frame.shape)
    #print(data_frame)
    return data_frame
