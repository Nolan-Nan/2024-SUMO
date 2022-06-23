#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
machine learning for rhetorical and relevance classification 
using conditional random fields (CRF) modelling

@author: amyconroy
"""


import numpy as np
import csv

import pickle

class ml():
    def __init__ (self, casenum, rhetRole):
        #Target/label
        ##relevance target
        self.rel_y = np.array([])
        
        ##rhetorical target
        self.rhet_y = np.array([])

        #List of features
        ##for asmo feature-set
        self.agree_X = np.array([])
        self.outcome_X = np.array([])
        
        ##for location feature-set
        self.loc1_X = np.array([]); self.loc2_X = np.array([]); self.loc3_X = np.array([])
        self.loc4_X = np.array([]); self.loc5_X = np.array([]); self.loc6_X = np.array([])
        self.sentlen_X = np.array([])
        self.rhet_X = np.array([])
        self.tfidf_max_X = np.array([])
        self.tfidf_top20_X = np.array([])
        self.wordlist_X = np.array([])
        self.pasttense_X = np.array([])
        
        #Hachey and Grover's original features
        self.HGloc1_X = np.array([]); self.HGloc2_X = np.array([]); self.HGloc3_X = np.array([])
        self.HGloc4_X = np.array([]); self.HGloc5_X = np.array([]); self.HGloc6_X = np.array([])
        self.tfidf_HGavg_X = np.array([])
        self.HGsentlen_X = np.array([])
        self.qb_X = np.array([])
        self.inq_X = np.array([]) 
        
        ##for entities feature-set
        self.enamex_X = np.array([])
        self.legalent_X = np.array([])
        
        ## updated entities feature-set
        self.citationent_X = np.array([])
        
        # black stone entities feature-set
        self.judge_blackstone = np.array([])
        self.blackstone = np.array([])
        self.provision_blackstone = np.array([])
        self.instrument_blackstone = np.array([])
        self.court_blackstone = np.array([])
        self.case_blackstone = np.array([])
        self.citation_blackstone = np.array([])
        
        # spacy entities 
        self.loc_ent_X = np.array([])
        self.org_ent_X = np.array([]) 
        self.date_ent_X = np.array([])
        self.person_ent_X = np.array([]) 
        self.time_ent_X = np.array([])
        self.gpe_ent_X = np.array([])
        self.fac_ent_X = np.array([]) 
        self.ordinal_ent_X = np.array([])
        self.spacy = np.array([])
        self.total_spacy_X  = np.array([])
        
        # all values are 0, thus non-beneficial in ml 
        # self.caseent_X = np.array([])
        ##for cue phrase feature-set
        self.asp_X = np.array([])
        self.modal_X = np.array([])
        self.voice_X = np.array([])
        self.negcue_X = np.array([])
        self.tense_X = np.array([])
        
        self.rhet_X = np.array([])
        

        self.ranking = []
        
        
        self.location = np.array([])
        self.quotation = np.array([])
        self.asmo = np.array([])
        self.cue_phrase = np.array([])
        self.sent_length = np.array([])
        self.tfidf_top20 = np.array([])
        self.rhet_role = np.array([])
        self.blackstone = np.array([])
        self.spacy = np.array([])
        self.SVCpred = [] # change the name to reflect that its DTC now
        self.rhet_predictions = np.array([])
        self.RelPredictions = []
        
        # other data
        self.judgename = []
        self.rhetlabel = []
        
        self.RFpred = []
        
                # new cue phrases
        # modal data on the entire sentence (count and boolean values)
        self.modal_pos_bool_X = np.array([])
        self. modal_dep_bool_X = np.array([])
        self.modal_dep_count_X = np.array([])
        self.modal_pos_count_X = np.array([])
        
        # verb data on the first verb
        self.new_modal_X = np.array([])
        self.new_tense_X = np.array([])
        self.new_dep_X = np.array([])
        self.new_tag_X = np.array([])
        self.new_negative_X = np.array([])
        self.new_stop_X = np.array([])
        self.new_voice_X = np.array([])
        
        # data on the token after the verb 
        self.second_pos_X = np.array([]) 
        self.second_dep_X = np.array([]) 
        self.second_tag_X = np.array([]) 
        self.second_stop_X = np.array([])
        
        
        # FUNCTION CALLS
        if rhetRole:
            print("Beginning rhetorical classification")
            self.rhetData(casenum)
            self.rhet_predict()
            self.rhetClassifiction(casenum)
            print("Rhetorical classification complete")
            self.rewriteFeatures(casenum)
            print("Beginning relevance classification")
            self.__init__(casenum, False) # Re-init the features
        else:
            self.relevanceData(casenum)
            self.cleanRhetLabel()
            self.create_RhetTarget()
            self.relevanceClassification()
            self.rewriteRelFeatures(casenum)
            print("Relevance classification complete")
        
    
    # because of the way CRF separates data, remove the array details etc
    def cleanRhetLabel(self):
        labels = self.rhetlabel
        newlabels = []
        
        for label in labels:
            if label == "['1.0']":
                newlabel = '1.0'
            if label == "['2.0']":
                newlabel = '2.0'
            if label == "['3.0']":
                newlabel= '3.0'
            if label == "['4.0']":
                newlabel = '4.0'
            if label == "['5.0']":
                newlabel = '5.0'
            if label == "['6.0']":
                newlabel = '6.0'
            if label == "['0.0']":
                newlabel = '0.0'
            individual_label = []
            individual_label.append(newlabel)
            newlabels.append(newlabel)
        
        self.rhetlabel = []
        self.rhetlabel = newlabels
    

        
    def get_rel_features(self): 
        features = self.location 
        features = np.vstack((features, self.quotation))
        features = np.vstack((features, self.asmo))
        features = np.vstack((features, self.sent_length))
        features = np.vstack((features, self.tfidf_max))
        features = np.vstack((features, self.rhet_X))    
        features = np.vstack((features, self.HGents))
        features = np.vstack((features, self.cue_phrase))
        features = np.vstack((features,)).T
        return features

    def rhet_predict(self): 
        f = open("RHETORICAL.pickle", "rb")
        classifier = pickle.load(f)
        f.close()
        
        features = self.get_rhet_dtc_features()
        self.rhet_pred = classifier.predict(features)
        print(len(self.rhet_pred))
        self.create_RhetTarget()
        
    def get_rhet_dtc_features(self): 
        features = self.quote
        features = np.vstack((features, self.asmo))
        features = np.vstack((features, self.location))
        features = np.vstack((features,)).T
        return features
    
    def create_RhetTarget(self):
        labels = self.rhet_pred
        self.rhetlabel = labels
        
        for label in labels:
            print(label)
            if label == 2.0:    
                print("yes I predict fact")
                self.rhet_X = np.append(self.rhet_X, [2/6])        
            if label == 3.0:      
                self.rhet_X = np.append(self.rhet_X, [3/6])        
            if label == 4.0:      
                self.rhet_X = np.append(self.rhet_X, [4/6])        
            if label == 5.0:   
                self.rhet_X = np.append(self.rhet_X, [5/6])        
            if label == 6.0:      
                self.rhet_X = np.append(self.rhet_X, [1])        
            if label == 1.0:      
                self.rhet_X = np.append(self.rhet_X, [1/6])        
            if label == 0.0:  
                self.rhet_X = np.append(self.rhet_X, [0]) 
        
        print(len(self.rhet_X))
        

        
        
    def createRhetFeaturesList(self, casenum): 
        all_featureset = []
        previous_judgename = '' 
        y = 0
        newspeech = True
        featureset = []
        tag_history = []
        tagcount = 0 # this is the counter for each sentence in a speech
        judges = self.judgename
        newSpeechLookAheadBy1 = False # checks if the judges are different
        newSpeechLookAheadBy2 = False # indicates a new speech
        
        for judge in judges:
             featureset = []
             newSpeechLookAheadBy1 = False 
             newSpeechLookAheadBy2 = False 
            
             
             if len(judges) == y+2: 
                 newSpeechLookAheadBy2 = True 
             elif len(judges) == y+1: 
                 newSpeechLookAheadBy1 = True
             elif judges[y+1] != judge:
                 newSpeechLookAheadBy1 = True
             elif judges[y+2] != judge:
                 newSpeechLookAheadBy2 = True
             if judge != previous_judgename: 
                 tagcount = 1
                 newspeech = True
                 tag_history = [] # previously assigned tags for that speech
                 newfeatures = self.rhetFeatures(casenum, tagcount, y, tag_history, newspeech, 
                                                     newSpeechLookAheadBy1, newSpeechLookAheadBy2)
                 featureset.append(newfeatures)
                 all_featureset.append(featureset)
                 tag = self.rhet_X[y]
                 tag_history.append(tag)
                 y += 1 
                 tagcount += 1
             else: 
                 newspeech = False
                 newfeatures = self.rhetFeatures(casenum, tagcount, y, tag_history, newspeech, 
                                                     newSpeechLookAheadBy1, newSpeechLookAheadBy2)
                 featureset.append(newfeatures)
                 all_featureset.append(featureset)
                 tag = self.rhet_X[y]
                 tag_history.append(tag)
                 y += 1 
                 tagcount += 1   
             previous_judgename = judge 
        
                    
        return all_featureset    
        
    def rhetClassifiction(self, casenum):
        f = open("RHETORICAL_CRF.pickle", "rb")
        classifier = pickle.load(f)
        f.close()
        case_features = self.createRhetFeaturesList(casenum)
        self.rhet_predictions = classifier.predict(case_features)
        
    #    self.convertRhetToArray(rhetorical_predictions)
        
        # get the predictions 

        
    def relevanceClassification(self): 
        f = open("RELEVANCE.pickle", "rb")
        classifier = pickle.load(f)
        f.close()
        
        case_features = self.get_rel_features()
        curr_RelPredictions = classifier.predict(case_features)
        for prediction in curr_RelPredictions: 
            if prediction == 1: 

                self.RelPredictions = np.append(self.RelPredictions, ['yes'])
            else:
                self.RelPredictions = np.append(self.RelPredictions, ['no'])

        ranks = []
        
        rank = classifier.predict_proba(case_features)


        for v in enumerate(rank):
            yes = v[1]
            yes_confidence = yes[1]
            ranks.append(yes_confidence)
        self.ranking = ranks
        
 

        
    # create the necessary feature sets
    def cleanRelLabels(self):
        labels = self.RFpred
        rellabels = []
        
        for label in labels: 
            label = (int(label))
            if label == 1: 
                label = 'yes'
            elif label == 0:
                label = 'no'

            individual_label = []
            individual_label.append(label)
            rellabels.append(individual_label)
            
        self.RFpred = rellabels
        
  
    
    def ConvertRhetToArray(self, rhetorical_predictions):
        for label in rhetorical_predictions:
            if label == 'FACT':     
                self.rhet_predictions = np.append(self.rhet_predictions, [2])       
            if label == 'PROCEEDINGS':     
                self.rhet_predictions = np.append(self.rhet_predictions, [3])            
            if label == 'BACKGROUND':       
                self.rhet_predictions = np.append(self.rhet_predictions, [4])           
            if label == 'FRAMING':
                self.rhet_predictions = np.append(self.rhet_predictions [5])          
            if label == 'DISPOSAL':
                self.rhet_predictions = np.append(self.rhet_predictions [6])        
            if label == 'TEXTUAL':      
                self.rhet_predictions = np.append(self.rhet_predictions[1])          
            if label == 'NONE':
                self.rhet_predictions = np.append(self.rhet_predictions [0])   
    
    # TODO - CHANGE THIS TO THE WAY THAT YOU DO IT FOR THE RELEVANCE OTHERWISE to match same feature sets
    def rewriteFeatures(self, casenum):
        with open('summarydata/UKHL_'+casenum+'_features.csv', 'w', newline='') as outfile:
                fieldnames = ['sent_id', 'align', 'agree', 'outcome', 'loc1', 'loc2', 'loc3', 
                'loc4', 'loc5', 'loc6', 'sentlen', 'quoteblock', 'inline_q', 'tfidf_top20', 'provision ent', 'instrument ent', 'court ent', 
                'case name ent', 'citation bl ent', 'judge ent', 'loc ent', 'org ent', 'date ent', 
                'person ent','judgename', 'rhet label', 'cp tense', 'cp modal', 'cp pos bool', 'cp dep bool', 'cp dep count', 'cp pos count', 'cp dep', 'cp tag', 'cp negative', 
        'cp stop', 'cp voice', 'cp second pos', 'cp second dep', 'cp second tag', 'cp second stop']        
        
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
        
                for v in range(len(self.sent_id)):
                    writer.writerow({'sent_id': self.sent_id[v], 'agree': self.agree_X[v],
                    'outcome': self.outcome_X[v], 'loc1': self.loc1_X[v], 'loc2': self.loc2_X[v], 'loc3': self.loc3_X[v], 'loc4': self.loc4_X[v], 
                    'loc5': self.loc5_X[v], 'loc6': self.loc6_X[v], 'sentlen': self.sentlen_X[v], 'quoteblock': self.qb_X[v], 'inline_q': self.inq_X[v], 
                     'tfidf_top20': self.tfidf_top20_X[v], 'provision ent' : self.provision_blackstone[v], 'instrument ent' : 
                        self.instrument_blackstone[v], 'court ent' : self.court_blackstone[v], 
                    'case name ent' : self.case_blackstone[v], 'citation bl ent' : self.citation_blackstone[v], 'judge ent' : self.judge_blackstone[v],
                    'loc ent' : self.loc_ent_X[v], 'org ent' : self.org_ent_X[v], 'date ent' : 
                    self.date_ent_X[v], 'person ent' : self.person_ent_X[v], 'judgename' : self.judgename[v], 'rhet label' : self.rhet_predictions[v], 
                    'cp tense': self.new_tense_X[v], 'cp modal': self.new_modal_X[v], 'cp pos bool' :  self.modal_pos_bool_X[v], 'cp dep bool': self.modal_dep_bool_X[v], 
                        'cp dep count':  self.modal_dep_count_X[v], 'cp pos count': self.modal_pos_count_X[v], 'cp dep': self.new_dep_X[v], 'cp tag': self.new_tag_X[v], 'cp negative': self.new_negative_X[v],
                        'cp stop': self.new_stop_X[v], 'cp voice' : self.new_voice_X[v], 'cp second pos': self.second_pos_X[v], 'cp second dep' : self.second_dep_X[v], 
                        'cp second tag' : self.second_tag_X[v], 'cp second stop' : self.second_stop_X[v]}) 
         


    
    def rewriteRelFeatures(self, casenum):

        with open('summarydata/UKHL_'+casenum+'_classification.csv', 'w', newline='') as outfile:
                    fieldnames = ['sent_id', 'rhet label', 'relevant', 'yes confidence']        
            
                    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                    writer.writeheader()
                        
                    for v in range(len(self.sent_id)):
                        writer.writerow({'sent_id': self.sent_id[v], 'rhet label' : self.rhetlabel[v], 
                        'relevant': self.RelPredictions[v], 'yes confidence' : self.ranking[v]}) 
                        
        
    # TODO - UPDATE THIS FOR THE NEW CUE PHRASES
    def rhetFeatures(self, casenum, sentence_id, y, tag_history, newspeech, 
                     newSpeechLookAheadBy1, newSpeechLookAheadBy2):
       
        features = {'loc' : self.location,
                    'quote' : self.quote, 
                    'asmo' : self.asmo, 
                    'cue phrase' : self.cue_phrase, 
                    'sent length' : self.sent_length,
                    'tfidf' : self.tfidf_top20, 
                    'blackstone' : self.blackstone,
                    'spacy' : self.spacy}
        
        sentence_id = (int(sentence_id))
        sentence_features = {}
        if newspeech: # first sentence of a speech, sentence 0 reserved for a new case start
                sentence_features.update({"r-1" : "<START>", 
                                      "r-2 r-1" : "<START> <START>", # previous label and current features
                                      'bias': 1.0,
                                 #     "sentence_id" : y,
                                      "length" : (self.sent_length[y]), 
                                      "length+1" : (self.sent_length[y+1]), 
                                      "length+2" : (self.sent_length[y+2]), 
                                      "tfdif" : (self.tfidf_top20[y]), 
                                      "tfdif+1" : (self.tfidf_top20[y+1]), 
                                      "tfdif+2" : (self.tfidf_top20[y+2]), 
                                      "loc1" : (self.loc1_X[y]),
                                      "loc1+1" : (self.loc1_X[y+1]),
                                      "loc1+2" : (self.loc1_X[y+2]),
                                      "loc2" : (self.loc2_X[y]),
                                      "loc2+1" : (self.loc2_X[y+1]),
                                      "loc2+2" : (self.loc2_X[y+2]),
                                      "loc3" : (self.loc3_X[y]),
                                      "loc3+1" : (self.loc3_X[y+1]),
                                      "loc3+2" : (self.loc3_X[y+2]),
                                      "loc4" : (self.loc4_X[y]),
                                      "loc4+1" : (self.loc4_X[y+1]),
                                      "loc4+2" : (self.loc4_X[y+2]),
                                      "loc5" : (self.loc5_X[y]),
                                      "loc5+1" : (self.loc5_X[y+1]),
                                      "loc5+2" : (self.loc5_X[y+2]),
                                      "loc6" : (self.loc6_X[y]),
                                      "loc6+1" : (self.loc6_X[y+1]),
                                      "loc6+2" : (self.loc6_X[y+2]),
                                      "quote1" : (self.inq_X[y]),
                                      "quote1+1" : (self.inq_X[y+1]),
                                      "quote1+2" : (self.inq_X[y+2]),
                                      "quote2" : (self.qb_X[y]),
                                      "quote2+1" : (self.qb_X[y+1]),
                                      "quote2+2" : (self.qb_X[y+2]),
                                      "asmo1" : (self.agree_X[y]),
                                      "asmo1+1" : (self.agree_X[y+1]),
                                      "asmo1+2" : (self.agree_X[y+2]),
                                      "asmo2" : (self.outcome_X[y]),
                                      "asmo2+1" : (self.outcome_X[y+1]),
                                      "asmo2+2" : (self.outcome_X[y+2]),
                                      "cue1" : (self.modal_dep_bool_X[y]), 
                                      "cue1+1" : (self.modal_dep_bool_X[y+1]), 
                                      "cue1+2" : (self.modal_dep_bool_X[y+2]), 
                                      "cue2" : (self.modal_dep_count_X[y]), 
                                      "cue2+1" : (self.modal_dep_count_X[y+1]), 
                                      "cue2+2" : (self.modal_dep_count_X[y+2]), 
                                      "cue3" : (self.new_modal_X[y]), 
                                      "cue3+1" : (self.new_modal_X[y+1]), 
                                      "cue3+2" : (self.new_modal_X[y+2]), 
                                      "cue4" : (self.new_tense_X[y]), 
                                      "cue4+1" : (self.new_tense_X[y+1]), 
                                      "cue4+2" : (self.new_tense_X[y+2]), 
                                      "cue5" : (self.new_dep_X[y]), 
                                      "cue5+1" : (self.new_dep_X[y+1]), 
                                      "cue5+2" : (self.new_dep_X[y+2]), 
                                      "cue6" : (self.new_tag_X[y]), 
                                      "cue6+1" : (self.new_tag_X[y+1]), 
                                      "cue6+2" : (self.new_tag_X[y+2]), 
                                      "cue7" : (self.new_negative_X[y]), 
                                      "cue7+1" : (self.new_negative_X[y+1]), 
                                      "cue7+2" : (self.new_negative_X[y+2]), 
                                      "cue8" : (self.new_stop_X[y]), 
                                      "cue8+1" : (self.new_stop_X[y+1]), 
                                      "cue8+2" : (self.new_stop_X[y+2]), 
                                      "cue9" : (self.new_voice_X[y]), 
                                      "cue9+1" : (self.new_voice_X[y+1]), 
                                      "cue9+2" : (self.new_voice_X[y+2]), 
                                      "cue10" : (self.second_pos_X[y]), 
                                      "cue10+1" : (self.second_pos_X[y+1]), 
                                      "cue10+2" : (self.second_pos_X[y+2]), 
                                      "cue11" : (self.second_dep_X[y]), 
                                      "cue11+1" : (self.second_dep_X[y+1]), 
                                      "cue11+2" : (self.second_dep_X[y+2]), 
                                      "cue12" : (self.second_tag_X[y]), 
                                      "cue12+1" : (self.second_tag_X[y+1]), 
                                      "cue12+2" : (self.second_tag_X[y+2]), 
                                      "cue13" : (self.second_stop_X[y]), 
                                      "cue13+1" : (self.second_stop_X[y+1]), 
                                      "cue13+2" : (self.second_stop_X[y+2]), 
                                      "bl1" : (self.provision_blackstone[y]), 
                                      "bl1+1" : (self.provision_blackstone[y+1]), 
                                      "bl1+2" : (self.provision_blackstone[y+2]), 
                                      "bl2" : (self.instrument_blackstone[y]), 
                                      "bl2+1" : (self.instrument_blackstone[y+1]), 
                                      "bl2+2" : (self.instrument_blackstone[y+2]), 
                                      "bl3" : (self.court_blackstone [y]), 
                                      "bl3+1" : (self.court_blackstone [y+1]), 
                                      "bl3+2" : (self.court_blackstone [y+2]), 
                                      "bl4" : (self.case_blackstone[y]), 
                                      "bl4+1" : (self.case_blackstone[y+1]), 
                                      "bl4+2" : (self.case_blackstone[y+2]), 
                                      "bl5" : (self.citation_blackstone[y]), 
                                      "bl5+1" : (self.citation_blackstone[y+1]), 
                                      "bl5+2" : (self.citation_blackstone[y+2]), 
                                      "bl6" : (self.judge_blackstone[y]), 
                                      "bl6+1" : (self.judge_blackstone[y+1]), 
                                      "bl6+2" : (self.judge_blackstone[y+2]),
                                      "spacy1" : (self.loc_ent_X[y]),
                                      "spacy1+1" : (self.loc_ent_X[y+1]),
                                      "spacy1+2" : (self.loc_ent_X[y+2]),
                                      "spacy2" : (self.org_ent_X[y]),
                                      "spacy2+1" : (self.org_ent_X[y+1]),
                                      "spacy2+2" : (self.org_ent_X[y+2]),
                                      "spacy3" : (self.date_ent_X[y]),
                                      "spacy3+1" : (self.date_ent_X[y+1]),
                                      "spacy3+2" : (self.date_ent_X[y+2]),
                                      "spacy4" : (self.person_ent_X[y]),
                                      "spacy4+1" : (self.person_ent_X[y+1]),
                                      "spacy4+2" : (self.person_ent_X[y+2])
                                      })
        # second word of the sentence
        
        elif sentence_id == 2 and (not newSpeechLookAheadBy1 and not newSpeechLookAheadBy2): 
                sentence_features.update({"r-1" : tag_history[sentence_id-2], 
                                      "r-2 r-1" : "<START> %s" % (tag_history[sentence_id-2]),
                                      'bias': 1.0,
                               #       "sentence_id" : y,
                               #       "r+1" : tag_history[y+1],
                              #        "r+2 r+1" : "%s %s" % (tag_history[y+2], tag_history[y+1]),
                                      "length" : (self.sent_length[y]), 
                                      "length+1" : (self.sent_length[y+1]), 
                                      "length+2" : (self.sent_length[y+2]), 
                                      "length-1" : (self.sent_length[y-1]), 
                                      "tfdif" : (self.tfidf_top20[y]), 
                                      "tfdif+1" : (self.tfidf_top20[y+1]), 
                                      "tfdif+2" : (self.tfidf_top20[y+2]), 
                                      "tfdif-1" : (self.tfidf_top20[y-1]), 
                                      "loc1" : (self.loc1_X[y]),
                                      "loc1+1" : (self.loc1_X[y+1]),
                                      "loc1+2" : (self.loc1_X[y+2]),
                                      "loc1-1" : (self.loc1_X[y-1]),
                                      "loc2" : (self.loc2_X[y]),
                                      "loc2+1" : (self.loc2_X[y+1]),
                                      "loc2+2" : (self.loc2_X[y+2]),
                                      "loc2-1" : (self.loc1_X[y-1]),
                                      "loc3" : (self.loc3_X[y]),
                                      "loc3+1" : (self.loc3_X[y+1]),
                                      "loc3+2" : (self.loc3_X[y+2]),
                                      "loc3-1" : (self.loc1_X[y-1]),
                                      "loc4" : (self.loc4_X[y]),
                                      "loc4+1" : (self.loc4_X[y+1]),
                                      "loc4+2" : (self.loc4_X[y+2]),
                                      "loc4-1" : (self.loc1_X[y-1]),
                                      "loc5" : (self.loc5_X[y]),
                                      "loc5+1" : (self.loc5_X[y+1]),
                                      "loc5+2" : (self.loc5_X[y+2]),
                                      "loc5-1" : (self.loc1_X[y-1]),
                                      "loc6" : (self.loc6_X[y]),
                                      "loc6+1" : (self.loc6_X[y+1]),
                                      "loc6+2" : (self.loc6_X[y+2]),
                                      "loc6-1" : (self.loc1_X[y-1]),
                                      "quote1" : (self.inq_X[y]),
                                      "quote1+1" : (self.inq_X[y+1]),
                                      "quote1+2" : (self.inq_X[y+2]),
                                      "quote1-1" : (self.inq_X[y-1]),
                                      "quote2" : (self.qb_X[y]),
                                      "quote2+1" : (self.qb_X[y+1]),
                                      "quote2+2" : (self.qb_X[y+2]),
                                      "quote2-1" : (self.qb_X[y-1]),
                                      "asmo1" : (self.agree_X[y]),
                                      "asmo1+1" : (self.agree_X[y+1]),
                                      "asmo1+2" : (self.agree_X[y+2]),
                                      "asmo1-1" : (self.agree_X[y-1]),
                                      "asmo2" : (self.outcome_X[y]),
                                      "asmo2+1" : (self.outcome_X[y+1]),
                                      "asmo2+2" : (self.outcome_X[y+2]),
                                      "asmo2-1" : (self.outcome_X[y-1]),
                                      "cue1" : (self.modal_dep_bool_X[y]), 
                                      "cue1+1" : (self.modal_dep_bool_X[y+1]), 
                                      "cue1+2" : (self.modal_dep_bool_X[y+2]), 
                                      "cue1-1" : (self.modal_dep_bool_X[y-1]), 
                                      "cue2" : (self.modal_dep_count_X[y]), 
                                      "cue2+1" : (self.modal_dep_count_X[y+1]), 
                                      "cue2+2" : (self.modal_dep_count_X[y+2]), 
                                      "cue2-1" : (self.modal_dep_count_X[y-1]), 
                                      "cue3" : (self.new_modal_X[y]), 
                                      "cue3+1" : (self.new_modal_X[y+1]), 
                                      "cue3+2" : (self.new_modal_X[y+2]), 
                                      "cue3-1" : (self.new_modal_X[y-1]), 
                                      "cue4" : (self.new_tense_X[y]), 
                                      "cue4+1" : (self.new_tense_X[y+1]), 
                                      "cue4+2" : (self.new_tense_X[y+2]), 
                                      "cue4-1" : (self.new_tense_X[y-1]), 
                                      "cue5" : (self.new_dep_X[y]), 
                                      "cue5+1" : (self.new_dep_X[y+1]), 
                                      "cue5+2" : (self.new_dep_X[y+2]), 
                                      "cue5-1" : (self.new_dep_X[y-1]), 
                                      "cue6" : (self.new_tag_X[y]), 
                                      "cue6+1" : (self.new_tag_X[y+1]), 
                                      "cue6+2" : (self.new_tag_X[y+2]), 
                                      "cue6-1" : (self.new_tag_X[y-1]), 
                                      "cue7" : (self.new_negative_X[y]), 
                                      "cue7+1" : (self.new_negative_X[y+1]), 
                                      "cue7+2" : (self.new_negative_X[y+2]), 
                                      "cue7-1" : (self.new_negative_X[y-1]), 
                                      "cue8" : (self.new_stop_X[y]), 
                                      "cue8+1" : (self.new_stop_X[y+1]), 
                                      "cue8+2" : (self.new_stop_X[y+2]), 
                                      "cue8-1" : (self.new_stop_X[y-1]), 
                                      "cue9" : (self.new_voice_X[y]), 
                                      "cue9+1" : (self.new_voice_X[y+1]), 
                                      "cue9+2" : (self.new_voice_X[y+2]), 
                                      "cue9-1" : (self.new_voice_X[y-1]), 
                                      "cue10" : (self.second_pos_X[y]), 
                                      "cue10+1" : (self.second_pos_X[y+1]), 
                                      "cue10+2" : (self.second_pos_X[y+2]), 
                                      "cue10-1" : (self.second_pos_X[y-1]), 
                                      "cue11" : (self.second_dep_X[y]), 
                                      "cue11+1" : (self.second_dep_X[y+1]), 
                                      "cue11+2" : (self.second_dep_X[y+2]), 
                                      "cue11-1" : (self.second_dep_X[y-1]), 
                                      "cue12" : (self.second_tag_X[y]), 
                                      "cue12+1" : (self.second_tag_X[y+1]), 
                                      "cue12+2" : (self.second_tag_X[y+2]), 
                                      "cue12-1" : (self.second_tag_X[y-1]), 
                                      "cue13" : (self.second_stop_X[y]), 
                                      "cue13+1" : (self.second_stop_X[y+1]), 
                                      "cue13+2" : (self.second_stop_X[y+2]), 
                                      "cue13-1" : (self.second_stop_X[y-1]), 
                                      "bl1" : (self.provision_blackstone[y]), 
                                      "bl1+1" : (self.provision_blackstone[y+1]), 
                                      "bl1+2" : (self.provision_blackstone[y+2]), 
                                      "bl1-1" : (self.provision_blackstone[y-1]), 
                                      "bl2" : (self.instrument_blackstone[y]), 
                                      "bl2+1" : (self.instrument_blackstone[y+1]), 
                                      "bl2+2" : (self.instrument_blackstone[y+2]), 
                                      "bl2-1" : (self.instrument_blackstone[y-1]), 
                                      "bl3" : (self.court_blackstone [y]), 
                                      "bl3+1" : (self.court_blackstone [y+1]), 
                                      "bl3+2" : (self.court_blackstone [y+2]), 
                                      "bl3-1" : (self.court_blackstone [y-1]), 
                                      "bl4" : (self.case_blackstone[y]), 
                                      "bl4+1" : (self.case_blackstone[y+1]), 
                                      "bl4+2" : (self.case_blackstone[y+2]), 
                                      "bl4-1" : (self.case_blackstone[y-1]), 
                                      "bl5" : (self.citation_blackstone[y]), 
                                      "bl5+1" : (self.citation_blackstone[y+1]), 
                                      "bl5+2" : (self.citation_blackstone[y+2]), 
                                      "bl5-1" : (self.citation_blackstone[y-1]), 
                                      "bl6" : (self.judge_blackstone[y]), 
                                      "bl6+1" : (self.judge_blackstone[y+1]), 
                                      "bl6+2" : (self.judge_blackstone[y+2]), 
                                      "bl6-1" : (self.judge_blackstone[y-1]),
                                      "spacy1" : (self.loc_ent_X[y]),
                                      "spacy1+1" : (self.loc_ent_X[y+1]),
                                      "spacy1+2" : (self.loc_ent_X[y+2]),
                                      "spacy1-1" : (self.loc_ent_X[y-1]),
                                      "spacy2" : (self.org_ent_X[y]),
                                      "spacy2+1" : (self.org_ent_X[y+1]),
                                      "spacy2+2" : (self.org_ent_X[y+2]),
                                      "spacy2-1" : (self.org_ent_X[y-1]),
                                      "spacy3" : (self.date_ent_X[y]),
                                      "spacy3+1" : (self.date_ent_X[y+1]),
                                      "spacy3+2" : (self.date_ent_X[y+2]),
                                      "spacy3-1" : (self.date_ent_X[y-1]),
                                      "spacy4" : (self.person_ent_X[y]),
                                      "spacy4+1" : (self.person_ent_X[y+1]),
                                      "spacy4+2" : (self.person_ent_X[y+2]),
                                      "spacy4-1" : (self.person_ent_X[y-1])
                                      })
                
        elif newSpeechLookAheadBy1:
                sentence_features.update({"r-1" : tag_history[sentence_id-2], 
                                      "r-2 r-1" : "%s %s" % (tag_history[sentence_id-3], tag_history[sentence_id-2]),
                                      'bias': 1.0,
                               #       "sentence_id" : y,
                              #        "r+1" : "<END>",
                              #        "r+2 r+1" : "<END> <END>", 
                                      "length" : (self.sent_length[y]), 
                                      "length-1" : (self.sent_length[y-1]), 
                                      "length-2" : (self.sent_length[y-2]), 
                                      "tfdif" : (self.tfidf_top20[y]),  
                                      "tfdif-1" : (self.tfidf_top20[y-1]), 
                                      "tfdif-2" : (self.tfidf_top20[y-2]), 
                                      "loc1" : (self.loc1_X[y]),
                                      "loc1-1" : (self.loc1_X[y-1]),
                                      "loc1-2" : (self.loc1_X[y-2]),
                                      "loc2" : (self.loc1_X[y]),
                                      "loc2-1" : (self.loc1_X[y-1]),
                                      "loc2-2" : (self.loc1_X[y-2]),
                                      "loc3" : (self.loc1_X[y]),
                                      "loc3-1" : (self.loc1_X[y-1]),
                                      "loc3-2" : (self.loc1_X[y-2]),
                                      "loc4" : (self.loc1_X[y]),
                                      "loc4-1" : (self.loc1_X[y-1]),
                                      "loc4-2" : (self.loc1_X[y-2]),
                                      "loc5" : (self.loc1_X[y]),
                                      "loc5-1" : (self.loc1_X[y-1]),
                                      "loc5-2" : (self.loc1_X[y-2]),
                                      "loc6" :  (self.loc1_X[y]),
                                      "loc6-1" : (self.loc1_X[y-1]),
                                      "loc6-2" : (self.loc1_X[y-2]),
                                      "quote1" : (self.inq_X[y]),
                                      "quote1-1" : (self.inq_X[y-1]),
                                      "quote1-2" : (self.inq_X[y-2]),
                                      "quote2" :  (self.qb_X[y]),
                                      "quote2-1" : (self.qb_X[y-1]),
                                      "quote2-2" : (self.inq_X[y-2]),
                                      "asmo1" : (self.agree_X[y]),
                                      "asmo1-1" : (self.agree_X[y-1]),
                                      "asmo1-2" : (self.agree_X[y-2]),
                                      "asmo2" : (self.outcome_X[y]),
                                      "asmo2-1" : (self.outcome_X[y-1]),
                                      "asmo2-2" : (self.outcome_X[y-2]),
                                      "cue1" : (self.modal_dep_bool_X[y]), 
                                      "cue1-2" : (self.modal_dep_bool_X[y-2]), 
                                      "cue1-1" : (self.modal_dep_bool_X[y-1]), 
                                      "cue2" : (self.modal_dep_count_X[y]), 
                                      "cue2-2" : (self.modal_dep_count_X[y-2]), 
                                      "cue2-1" : (self.modal_dep_count_X[y-1]), 
                                      "cue3" : (self.new_modal_X[y]), 
                                      "cue3-1" : (self.new_modal_X[y-1]), 
                                      "cue3-2" : (self.new_modal_X[y-2]), 
                                      "cue4" : (self.new_tense_X[y]), 
                                      "cue4-2" : (self.new_tense_X[y-2]), 
                                      "cue4-1" : (self.new_tense_X[y-1]), 
                                      "cue5" : (self.new_dep_X[y]), 
                                      "cue5-2" : (self.new_dep_X[y-2]), 
                                      "cue5-1" : (self.new_dep_X[y-1]), 
                                      "cue6" : (self.new_tag_X[y]), 
                                      "cue6-2" : (self.new_tag_X[y-2]), 
                                      "cue6-1" : (self.new_tag_X[y-1]), 
                                      "cue7" : (self.new_negative_X[y]),  
                                      "cue7-2" : (self.new_negative_X[y-2]), 
                                      "cue7-1" : (self.new_negative_X[y-1]), 
                                      "cue8" : (self.new_stop_X[y]), 
                                      "cue8-2" : (self.new_stop_X[y-2]), 
                                      "cue8-1" : (self.new_stop_X[y-1]), 
                                      "cue9" : (self.new_voice_X[y]), 
                                      "cue9-2" : (self.new_voice_X[y-2]), 
                                      "cue9-1" : (self.new_voice_X[y-1]), 
                                      "cue10" : (self.second_pos_X[y]), 
                                      "cue10-2" : (self.second_pos_X[y-2]), 
                                      "cue10-1" : (self.second_pos_X[y-1]), 
                                      "cue11" : (self.second_dep_X[y]), 
                                      "cue11-2" : (self.second_dep_X[y-2]), 
                                      "cue11-1" : (self.second_dep_X[y-1]), 
                                      "cue12" : (self.second_tag_X[y]), 
                                      "cue12-2" : (self.second_tag_X[y-2]), 
                                      "cue12-1" : (self.second_tag_X[y-1]), 
                                      "cue13" : (self.second_stop_X[y]), 
                                      "cue13-2" : (self.second_stop_X[y-2]), 
                                      "cue13-1" : (self.second_stop_X[y-1]), 
                                      "bl1" : (self.provision_blackstone[y]), 
                                      "bl1-1" : (self.provision_blackstone[y-1]), 
                                      "bl1-2" : (self.provision_blackstone[y-2]), 
                                      "bl2" : (self.instrument_blackstone[y]),
                                      "bl2-1" : (self.instrument_blackstone[y-1]), 
                                      "bl2-2" : (self.instrument_blackstone[y-2]), 
                                      "bl3" : (self.court_blackstone [y]), 
                                      "bl3-1" : (self.court_blackstone [y-1]), 
                                      "bl3-2" : (self.court_blackstone [y-2]), 
                                      "bl4" : (self.case_blackstone[y]),
                                      "bl4-1" : (self.case_blackstone[y-1]), 
                                      "bl4-2" : (self.case_blackstone[y-2]), 
                                      "bl5" :  (self.citation_blackstone[y]), 
                                      "bl5-1" : (self.citation_blackstone[y-1]), 
                                      "bl5-2" : (self.citation_blackstone[y-2]), 
                                      "bl6" : (self.judge_blackstone[y]),
                                      "bl6-1" : (self.judge_blackstone[y-1]), 
                                      "bl6-2" : (self.judge_blackstone[y-2]),
                                      "spacy1" : (self.loc_ent_X[y]),
                                      "spacy1-1" : (self.loc_ent_X[y-1]),
                                      "spacy1-2" : (self.loc_ent_X[y-2]),
                                      "spacy2" : (self.org_ent_X[y]),
                                      "spacy2-1" : (self.org_ent_X[y-1]),
                                      "spacy2-2" : (self.org_ent_X[y-2]),
                                      "spacy3" : (self.date_ent_X[y]),
                                      "spacy3-1" : (self.date_ent_X[y-1]),
                                      "spacy3-2" : (self.date_ent_X[y-2]),
                                      "spacy4" : (self.person_ent_X[y]),
                                      "spacy4-1" : (self.person_ent_X[y-1]),
                                      "spacy4-2" : (self.person_ent_X[y-2])
                                      })
        elif newSpeechLookAheadBy2:
                sentence_features.update({"r-1" : tag_history[sentence_id-2], 
                                      "r-2 r-1" : "%s %s" % (tag_history[sentence_id-3], tag_history[sentence_id-2]),
                                      'bias': 1.0,
                             #         "sentence_id" : y,
                                      "length" : (self.sent_length[y]), 
                                      "length+1" : (self.sent_length[y+1]), 
                                      "length-1" : (self.sent_length[y-1]), 
                                      "length-2" : (self.sent_length[y-2]), 
                                      "tfdif" : (self.tfidf_top20[y]), 
                                      "tfdif+1" : (self.tfidf_top20[y+1]), 
                                      "tfdif-1" : (self.tfidf_top20[y-1]), 
                                      "tfdif-2" : (self.tfidf_top20[y-2]), 
                                      "loc1" : (self.loc1_X[y]),
                                      "loc1+1" : (self.loc1_X[y+1]),
                                      "loc1-1" : (self.loc1_X[y-1]),
                                      "loc1-2" : (self.loc1_X[y-2]),
                                      "loc2" : (self.loc2_X[y]),
                                      "loc2+1" : (self.loc2_X[y+1]),
                                      "loc2-1" : (self.loc1_X[y-1]),
                                      "loc2-2" : (self.loc1_X[y-2]),
                                      "loc3" : (self.loc3_X[y]),
                                      "loc3+1" : (self.loc3_X[y+1]),
                                      "loc3-1" : (self.loc1_X[y-1]),
                                      "loc3-2" : (self.loc1_X[y-2]),
                                      "loc4" : (self.loc4_X[y]),
                                      "loc4+1" : (self.loc4_X[y+1]),
                                      "loc4-1" : (self.loc1_X[y-1]),
                                      "loc4-2" : (self.loc1_X[y-2]),
                                      "loc5" : (self.loc5_X[y]),
                                      "loc5+1" : (self.loc5_X[y+1]),
                                      "loc5-1" : (self.loc1_X[y-1]),
                                      "loc5-2" : (self.loc1_X[y-2]),
                                      "loc6" : (self.loc6_X[y]),
                                      "loc6+1" : (self.loc6_X[y+1]),
                                      "loc6-1" : (self.loc1_X[y-1]),
                                      "loc6-2" : (self.loc1_X[y-2]),
                                      "quote1" : (self.inq_X[y]),
                                      "quote1+1" : (self.inq_X[y+1]),
                                      "quote1-1" : (self.inq_X[y-1]),
                                      "quote1-2" : (self.inq_X[y-2]),
                                      "quote2" : (self.qb_X[y]),
                                      "quote2+1" : (self.qb_X[y+1]),
                                      "quote2-1" : (self.qb_X[y-1]),
                                      "quote2-2" : (self.inq_X[y-2]),
                                      "asmo1" : (self.agree_X[y]),
                                      "asmo1+1" : (self.agree_X[y+1]),
                                      "asmo1-1" : (self.agree_X[y-1]),
                                      "asmo1-2" : (self.agree_X[y-2]),
                                      "asmo2" : (self.outcome_X[y]),
                                      "asmo2+1" : (self.outcome_X[y+1]),
                                      "asmo2-1" : (self.outcome_X[y-1]),
                                      "asmo2-2" : (self.outcome_X[y-2]),
                                      "cue1" : (self.modal_dep_bool_X[y]), 
                                      "cue1+1" : (self.modal_dep_bool_X[y+1]), 
                                      "cue1-2" : (self.modal_dep_bool_X[y-2]), 
                                      "cue1-1" : (self.modal_dep_bool_X[y-1]), 
                                      "cue2" : (self.modal_dep_count_X[y]), 
                                      "cue2+1" : (self.modal_dep_count_X[y+1]), 
                                      "cue2-2" : (self.modal_dep_count_X[y-2]), 
                                      "cue2-1" : (self.modal_dep_count_X[y-1]), 
                                      "cue3" : (self.new_modal_X[y]), 
                                      "cue3+1" : (self.new_modal_X[y+1]), 
                                      "cue3-1" : (self.new_modal_X[y-1]), 
                                      "cue3-2" : (self.new_modal_X[y-2]), 
                                      "cue4" : (self.new_tense_X[y]), 
                                      "cue4+1" : (self.new_tense_X[y+1]), 
                                      "cue4-2" : (self.new_tense_X[y-2]), 
                                      "cue4-1" : (self.new_tense_X[y-1]), 
                                      "cue5" : (self.new_dep_X[y]), 
                                      "cue5+1" : (self.new_dep_X[y+1]), 
                                      "cue5-2" : (self.new_dep_X[y-2]), 
                                      "cue5-1" : (self.new_dep_X[y-1]), 
                                      "cue6" : (self.new_tag_X[y]), 
                                      "cue6+1" : (self.new_tag_X[y+1]), 
                                      "cue6-2" : (self.new_tag_X[y-2]), 
                                      "cue6-1" : (self.new_tag_X[y-1]), 
                                      "cue7" : (self.new_negative_X[y]),
                                      "cue7+1" : (self.new_negative_X[y+1]), 
                                      "cue7-2" : (self.new_negative_X[y-2]), 
                                      "cue7-1" : (self.new_negative_X[y-1]), 
                                      "cue8" : (self.new_stop_X[y]), 
                                      "cue8+1" : (self.new_stop_X[y+1]), 
                                      "cue8-2" : (self.new_stop_X[y-2]), 
                                      "cue8-1" : (self.new_stop_X[y-1]), 
                                      "cue9" : (self.new_voice_X[y]), 
                                      "cue9+1" : (self.new_voice_X[y+1]), 
                                      "cue9-2" : (self.new_voice_X[y-2]), 
                                      "cue9-1" : (self.new_voice_X[y-1]), 
                                      "cue10" : (self.second_pos_X[y]), 
                                      "cue10+1" : (self.second_pos_X[y+1]), 
                                      "cue10-2" : (self.second_pos_X[y-2]), 
                                      "cue10-1" : (self.second_pos_X[y-1]), 
                                      "cue11" : (self.second_dep_X[y]), 
                                      "cue11+1" : (self.second_dep_X[y+1]), 
                                      "cue11-2" : (self.second_dep_X[y-2]), 
                                      "cue11-1" : (self.second_dep_X[y-1]), 
                                      "cue12" : (self.second_tag_X[y]), 
                                      "cue12+1" : (self.second_tag_X[y+1]), 
                                      "cue12-2" : (self.second_tag_X[y-2]), 
                                      "cue12-1" : (self.second_tag_X[y-1]), 
                                      "cue13" : (self.second_stop_X[y]), 
                                      "cue13+1" : (self.second_stop_X[y+1]), 
                                      "cue13-2" : (self.second_stop_X[y-2]), 
                                      "cue13-1" : (self.second_stop_X[y-1]), 
                                      "bl1" : (self.provision_blackstone[y]), 
                                      "bl1+1" : (self.provision_blackstone[y+1]), 
                                      "bl1-1" : (self.provision_blackstone[y-1]), 
                                      "bl1-2" : (self.provision_blackstone[y-2]), 
                                      "bl2" : (self.instrument_blackstone[y]), 
                                      "bl2+1" : (self.instrument_blackstone[y+1]), 
                                      "bl2-1" : (self.instrument_blackstone[y-1]), 
                                      "bl2-2" : (self.instrument_blackstone[y-2]), 
                                      "bl3" : (self.court_blackstone [y]), 
                                      "bl3+1" : (self.court_blackstone [y+1]), 
                                      "bl3-1" : (self.court_blackstone [y-1]), 
                                      "bl3-2" : (self.court_blackstone [y-2]), 
                                      "bl4" : (self.case_blackstone[y]), 
                                      "bl4+1" : (self.case_blackstone[y+1]), 
                                      "bl4-1" : (self.case_blackstone[y-1]), 
                                      "bl4-2" : (self.case_blackstone[y-2]), 
                                      "bl5" : (self.citation_blackstone[y]), 
                                      "bl5+1" : (self.citation_blackstone[y+1]), 
                                      "bl5-1" : (self.citation_blackstone[y-1]), 
                                      "bl5-2" : (self.citation_blackstone[y-2]), 
                                      "bl6" : (self.judge_blackstone[y]), 
                                      "bl6+1" : (self.judge_blackstone[y+1]), 
                                      "bl6-1" : (self.judge_blackstone[y-1]), 
                                      "bl6-2" : (self.judge_blackstone[y-2]),
                                      "spacy1" : (self.loc_ent_X[y]),
                                      "spacy1+1" : (self.loc_ent_X[y+1]),
                                      "spacy1-1" : (self.loc_ent_X[y-1]),
                                      "spacy1-2" : (self.loc_ent_X[y-2]),
                                      "spacy2" : (self.org_ent_X[y]),
                                      "spacy2+1" : (self.org_ent_X[y+1]),
                                      "spacy2-1" : (self.org_ent_X[y-1]),
                                      "spacy2-2" : (self.org_ent_X[y-2]),
                                      "spacy3" : (self.date_ent_X[y]),
                                      "spacy3+1" : (self.date_ent_X[y+1]),
                                      "spacy3-1" : (self.date_ent_X[y-1]),
                                      "spacy3-2" : (self.date_ent_X[y-2]),
                                      "spacy4" : (self.person_ent_X[y]),
                                      "spacy4+1" : (self.person_ent_X[y+1]),
                                      "spacy4-1" : (self.person_ent_X[y-1]),
                                      "spacy4-2" : (self.person_ent_X[y-2])
                                      })   
        else: 
                sentence_features.update({"r-1" : tag_history[sentence_id-2], 
                                      "r-2 r-1" : "%s %s" % (tag_history[sentence_id-3], tag_history[sentence_id-2]),
                                      'bias': 1.0,
                                 #     "sentence_id" : y,
                                      "length" : (self.sent_length[y]), 
                                      "length+1" : (self.sent_length[y+1]), 
                                      "length+2" : (self.sent_length[y+2]), 
                                      "length-1" : (self.sent_length[y-1]), 
                                      "length-2" : (self.sent_length[y-2]), 
                                      "tfdif" : (self.tfidf_top20[y]), 
                                      "tfdif+1" : (self.tfidf_top20[y+1]), 
                                      "tfdif+2" : (self.tfidf_top20[y+2]), 
                                      "tfdif-1" : (self.tfidf_top20[y-1]), 
                                      "tfdif-2" : (self.tfidf_top20[y-2]), 
                                      "loc1" : (self.loc1_X[y]),
                                      "loc1+1" : (self.loc1_X[y+1]),
                                      "loc1+2" : (self.loc1_X[y+2]),
                                      "loc1-1" : (self.loc1_X[y-1]),
                                      "loc1-2" : (self.loc1_X[y-2]),
                                      "loc2" : (self.loc2_X[y]),
                                      "loc2+1" : (self.loc2_X[y+1]),
                                      "loc2+2" : (self.loc2_X[y+2]),
                                      "loc2-1" : (self.loc1_X[y-1]),
                                      "loc2-2" : (self.loc1_X[y-2]),
                                      "loc3" : (self.loc3_X[y]),
                                      "loc3+1" : (self.loc3_X[y+1]),
                                      "loc3+2" : (self.loc3_X[y+2]),
                                      "loc3-1" : (self.loc1_X[y-1]),
                                      "loc3-2" : (self.loc1_X[y-2]),
                                      "loc4" : (self.loc4_X[y]),
                                      "loc4+1" : (self.loc4_X[y+1]),
                                      "loc4+2" : (self.loc4_X[y+2]),
                                      "loc4-1" : (self.loc1_X[y-1]),
                                      "loc4-2" : (self.loc1_X[y-2]),
                                      "loc5" : (self.loc5_X[y]),
                                      "loc5+1" : (self.loc5_X[y+1]),
                                      "loc5+2" : (self.loc5_X[y+2]),
                                      "loc5-1" : (self.loc1_X[y-1]),
                                      "loc5-2" : (self.loc1_X[y-2]),
                                      "loc6" : (self.loc6_X[y]),
                                      "loc6+1" : (self.loc6_X[y+1]),
                                      "loc6+2" : (self.loc6_X[y+2]),
                                      "loc6-1" : (self.loc1_X[y-1]),
                                      "loc6-2" : (self.loc1_X[y-2]),
                                      "quote1" : (self.inq_X[y]),
                                      "quote1+1" : (self.inq_X[y+1]),
                                      "quote1+2" : (self.inq_X[y+2]),
                                      "quote1-1" : (self.inq_X[y-1]),
                                      "quote1-2" : (self.inq_X[y-2]),
                                      "quote2" : (self.qb_X[y]),
                                      "quote2+1" : (self.qb_X[y+1]),
                                      "quote2+2" : (self.qb_X[y+2]),
                                      "quote2-1" : (self.qb_X[y-1]),
                                      "quote2-2" : (self.inq_X[y-2]),
                                      "asmo1" : (self.agree_X[y]),
                                      "asmo1+1" : (self.agree_X[y+1]),
                                      "asmo1+2" : (self.agree_X[y+2]),
                                      "asmo1-1" : (self.agree_X[y-1]),
                                      "asmo1-2" : (self.agree_X[y-2]),
                                      "asmo2" : (self.outcome_X[y]),
                                      "asmo2+1" : (self.outcome_X[y+1]),
                                      "asmo2+2" : (self.outcome_X[y+2]),
                                      "asmo2-1" : (self.outcome_X[y-1]),
                                      "asmo2-2" : (self.outcome_X[y-2]),
                                      "cue1" : (self.modal_dep_bool_X[y]), 
                                      "cue1+1" : (self.modal_dep_bool_X[y+1]), 
                                      "cue1+2" : (self.modal_dep_bool_X[y+2]), 
                                      "cue1-2" : (self.modal_dep_bool_X[y-2]), 
                                      "cue1-1" : (self.modal_dep_bool_X[y-1]), 
                                      "cue2" : (self.modal_dep_count_X[y]), 
                                      "cue2+1" : (self.modal_dep_count_X[y+1]), 
                                      "cue2+2" : (self.modal_dep_count_X[y+2]), 
                                      "cue2-2" : (self.modal_dep_count_X[y-2]), 
                                      "cue2-1" : (self.modal_dep_count_X[y-1]), 
                                      "cue3" : (self.new_modal_X[y]), 
                                      "cue3+1" : (self.new_modal_X[y+1]), 
                                      "cue3+2" : (self.new_modal_X[y+2]),
                                      "cue3-1" : (self.new_modal_X[y-1]), 
                                      "cue3-2" : (self.new_modal_X[y-2]), 
                                      "cue4" : (self.new_tense_X[y]), 
                                      "cue4+1" : (self.new_tense_X[y+1]), 
                                      "cue4+2" : (self.new_tense_X[y+2]), 
                                      "cue4-2" : (self.new_tense_X[y-2]), 
                                      "cue4-1" : (self.new_tense_X[y-1]), 
                                      "cue5" : (self.new_dep_X[y]), 
                                      "cue5+1" : (self.new_dep_X[y+1]), 
                                      "cue5+2" : (self.new_dep_X[y+2]), 
                                      "cue5-2" : (self.new_dep_X[y-2]), 
                                      "cue5-1" : (self.new_dep_X[y-1]), 
                                      "cue6" : (self.new_tag_X[y]), 
                                      "cue6+1" : (self.new_tag_X[y+1]), 
                                      "cue6+2" : (self.new_tag_X[y+2]), 
                                      "cue6-2" : (self.new_tag_X[y-2]), 
                                      "cue6-1" : (self.new_tag_X[y-1]), 
                                      "cue7" : (self.new_negative_X[y]),
                                      "cue7+1" : (self.new_negative_X[y+1]), 
                                      "cue7+2" : (self.new_negative_X[y+2]), 
                                      "cue7-2" : (self.new_negative_X[y-2]), 
                                      "cue7-1" : (self.new_negative_X[y-1]), 
                                      "cue8" : (self.new_stop_X[y]), 
                                      "cue8+1" : (self.new_stop_X[y+1]), 
                                      "cue8+2" : (self.new_stop_X[y+2]), 
                                      "cue8-2" : (self.new_stop_X[y-2]), 
                                      "cue8-1" : (self.new_stop_X[y-1]), 
                                      "cue9" : (self.new_voice_X[y]), 
                                      "cue9+1" : (self.new_voice_X[y+1]), 
                                      "cue9+2" : (self.new_voice_X[y+2]), 
                                      "cue9-2" : (self.new_voice_X[y-2]), 
                                      "cue9-1" : (self.new_voice_X[y-1]), 
                                      "cue10" : (self.second_pos_X[y]), 
                                      "cue10+1" : (self.second_pos_X[y+1]), 
                                      "cue10+2" : (self.second_pos_X[y+2]), 
                                      "cue10-2" : (self.second_pos_X[y-2]), 
                                      "cue10-1" : (self.second_pos_X[y-1]), 
                                      "cue11" : (self.second_dep_X[y]), 
                                      "cue11+1" : (self.second_dep_X[y+1]), 
                                      "cue11+2" : (self.second_dep_X[y+2]), 
                                      "cue11-2" : (self.second_dep_X[y-2]), 
                                      "cue11-1" : (self.second_dep_X[y-1]), 
                                      "cue12" : (self.second_tag_X[y]), 
                                      "cue12+1" : (self.second_tag_X[y+1]), 
                                      "cue12+2" : (self.second_tag_X[y+2]), 
                                      "cue12-2" : (self.second_tag_X[y-2]), 
                                      "cue12-1" : (self.second_tag_X[y-1]), 
                                      "cue13" : (self.second_stop_X[y]), 
                                      "cue13+1" : (self.second_stop_X[y+1]),
                                      "cue13+2" : (self.second_stop_X[y+2]),
                                      "cue13-2" : (self.second_stop_X[y-2]), 
                                      "cue13-1" : (self.second_stop_X[y-1]), 
                                      "bl1" : (self.provision_blackstone[y]), 
                                      "bl1+1" : (self.provision_blackstone[y+1]), 
                                      "bl1+2" : (self.provision_blackstone[y+2]), 
                                      "bl1-1" : (self.provision_blackstone[y-1]), 
                                      "bl1-2" : (self.provision_blackstone[y-2]), 
                                      "bl2" : (self.instrument_blackstone[y]), 
                                      "bl2+1" : (self.instrument_blackstone[y+1]), 
                                      "bl2+2" : (self.instrument_blackstone[y+2]), 
                                      "bl2-1" : (self.instrument_blackstone[y-1]), 
                                      "bl2-2" : (self.instrument_blackstone[y-2]), 
                                      "bl3" : (self.court_blackstone [y]), 
                                      "bl3+1" : (self.court_blackstone [y+1]), 
                                      "bl3+2" : (self.court_blackstone [y+2]), 
                                      "bl3-1" : (self.court_blackstone [y-1]), 
                                      "bl3-2" : (self.court_blackstone [y-2]), 
                                      "bl4" : (self.case_blackstone[y]), 
                                      "bl4+1" : (self.case_blackstone[y+1]), 
                                      "bl4+2" : (self.case_blackstone[y+2]), 
                                      "bl4-1" : (self.case_blackstone[y-1]), 
                                      "bl4-2" : (self.case_blackstone[y-2]), 
                                      "bl5" : (self.citation_blackstone[y]), 
                                      "bl5+1" : (self.citation_blackstone[y+1]), 
                                      "bl5+2" : (self.citation_blackstone[y+2]), 
                                      "bl5-1" : (self.citation_blackstone[y-1]), 
                                      "bl5-2" : (self.citation_blackstone[y-2]), 
                                      "bl6" : (self.judge_blackstone[y]), 
                                      "bl6+1" : (self.judge_blackstone[y+1]), 
                                      "bl6+2" : (self.judge_blackstone[y+2]), 
                                      "bl6-1" : (self.judge_blackstone[y-1]), 
                                      "bl6-2" : (self.judge_blackstone[y-2]),
                                      "spacy1" : (self.loc_ent_X[y]),
                                      "spacy1+1" : (self.loc_ent_X[y+1]),
                                      "spacy1+2" : (self.loc_ent_X[y+2]),
                                      "spacy1-1" : (self.loc_ent_X[y-1]),
                                      "spacy1-2" : (self.loc_ent_X[y-2]),
                                      "spacy2" : (self.org_ent_X[y]),
                                      "spacy2+1" : (self.org_ent_X[y+1]),
                                      "spacy2+2" : (self.org_ent_X[y+2]),
                                      "spacy2-1" : (self.org_ent_X[y-1]),
                                      "spacy2-2" : (self.org_ent_X[y-2]),
                                      "spacy3" : (self.date_ent_X[y]),
                                      "spacy3+1" : (self.date_ent_X[y+1]),
                                      "spacy3+2" : (self.date_ent_X[y+2]),
                                      "spacy3-1" : (self.date_ent_X[y-1]),
                                      "spacy3-2" : (self.date_ent_X[y-2]),
                                      "spacy4" : (self.person_ent_X[y]),
                                      "spacy4+1" : (self.person_ent_X[y+1]),
                                      "spacy4+2" : (self.person_ent_X[y+2]),
                                      "spacy4-1" : (self.person_ent_X[y-1]),
                                      "spacy4-2" : (self.person_ent_X[y-2])
                                      })  
        return sentence_features

        

    def rhetData(self, casenum):
        self.sent_id = []
        with open('summarydata/UKHL_'+casenum+'_features.csv', 'r') as infile:
            reader = csv.DictReader(infile)

        # for each row in the MLDATA cv file, get the corresponding result - add to array
            for row in reader:
                self.agree_X = np.append(self.agree_X, [float(row['agree'])])
                self.outcome_X = np.append(self.outcome_X, [float(row['outcome'])])
                self.loc1_X = np.append(self.loc1_X, [float(row['loc1'])])
                self.loc2_X = np.append(self.loc2_X, [float(row['loc2'])])
                self.loc3_X = np.append(self.loc3_X, [float(row['loc3'])])
                self.loc4_X = np.append(self.loc4_X, [float(row['loc4'])])
                self.loc5_X = np.append(self.loc5_X, [float(row['loc5'])])
                self.loc6_X = np.append(self.loc6_X, [float(row['loc6'])])
                self.sentlen_X = np.append(self.sentlen_X, [float(row['sentlen'])])
                self.qb_X = np.append(self.qb_X, [float(row['quoteblock'])])
                self.inq_X = np.append(self.inq_X, [float(row['inline_q'])])
                self.tfidf_top20_X = np.append(self.tfidf_top20_X, [float(row['tfidf_top20'])])
                
                self.provision_blackstone = np.append(self.provision_blackstone, [float(row['provision ent'])])
                self.instrument_blackstone = np.append(self.instrument_blackstone, [float(row['instrument ent'])])
                self.court_blackstone = np.append(self.court_blackstone, [float(row['court ent'])])
                self.case_blackstone = np.append(self.case_blackstone, [float(row['case name ent'])])
                self.citation_blackstone = np.append(self.citation_blackstone, [float(row['citation bl ent'])])
                self.judge_blackstone = np.append(self.judge_blackstone, [float(row['judge ent'])])
                self.loc_ent_X = np.append(self.loc_ent_X, [float(row['loc ent'])])
                self.org_ent_X = np.append(self.org_ent_X, [float(row['org ent'])])
                self.date_ent_X = np.append(self.date_ent_X, [float(row['date ent'])])
                self.person_ent_X = np.append(self.person_ent_X, [float(row['person ent'])])
                self.judgename.append(row['judgename'])
                self.sent_id.append(row['sent_id'])
                
                self.modal_pos_bool_X =  np.append(self.modal_pos_bool_X, [float(row['cp pos bool'])])
                self.modal_dep_bool_X = np.append(self.modal_dep_bool_X, [float(row['cp dep bool'])])
                self.modal_dep_count_X = np.append(self.modal_dep_count_X, [float(row['cp dep count'])])
                self.modal_pos_count_X = np.append(self.modal_pos_count_X, [float(row['cp pos count'])])
                self.new_modal_X = np.append(self.new_modal_X, [float(row['cp modal'])])
                self.new_tense_X = np.append(self.new_tense_X, [float(row['cp tense'])])
                self.new_dep_X = np.append(self.new_dep_X, [float(row['cp dep'])])
                self.new_tag_X = np.append(self.new_tag_X, [float(row['cp tag'])])
                self.new_negative_X = np.append(self.new_negative_X, [float(row['cp negative'])])
                self.new_stop_X = np.append(self.new_stop_X, [float(row['cp stop'])])
                self.new_voice_X = np.append(self.new_voice_X, [float(row['cp voice'])])
  
                self.second_pos_X = np.append(self.second_pos_X, [float(row['cp second pos'])])
                self.second_dep_X = np.append(self.second_dep_X, [float(row['cp second dep'])])
                self.second_tag_X = np.append(self.second_tag_X, [float(row['cp second tag'])])
                self.second_stop_X = np.append(self.second_stop_X, [float(row['cp second stop'])])

        self.location = self.loc1_X, self.loc2_X, self.loc3_X, self.loc4_X, self.loc5_X, self.loc6_X
        self.quote = self.inq_X, self.qb_X
        self.asmo = self.agree_X, self.outcome_X
        self.cue_phrase = self.modal_dep_bool_X,  self.modal_dep_count_X, self.new_tense_X, self.new_tag_X, self.new_negative_X, self.new_stop_X, self.new_voice_X, self.new_modal_X, self.second_pos_X, self.second_dep_X, self.second_tag_X, self.second_stop_X 
        self.sent_length =  self.sentlen_X
        self.tfidf_top20 = self.tfidf_top20_X 
        self.blackstone = self.provision_blackstone, self.instrument_blackstone, self.court_blackstone, self.case_blackstone, self.citation_blackstone, self.judge_blackstone
        self.spacy = self.loc_ent_X, self.org_ent_X, self.date_ent_X, self.person_ent_X
      
    def relevanceData(self, casenum):
        with open('summarydata/UKHL_'+casenum+'_features.csv', 'r') as infile:
            reader = csv.DictReader(infile)

        # for each row in the MLDATA cv file, get the corresponding result - add to array
            for row in reader:
                self.agree_X = np.append(self.agree_X, [float(row['agree'])])
                self.outcome_X = np.append(self.outcome_X, [float(row['outcome'])])
                self.loc1_X = np.append(self.loc1_X, [float(row['loc1'])])
                self.loc2_X = np.append(self.loc2_X, [float(row['loc2'])])
                self.loc3_X = np.append(self.loc3_X, [float(row['loc3'])])
                self.loc4_X = np.append(self.loc4_X, [float(row['loc4'])])
                self.loc5_X = np.append(self.loc5_X, [float(row['loc5'])])
                self.loc6_X = np.append(self.loc6_X, [float(row['loc6'])])

                self.sentlen_X = np.append(self.sentlen_X, [float(row['sentlen'])])
                self.qb_X = np.append(self.qb_X, [float(row['quoteblock'])])
                self.inq_X = np.append(self.inq_X, [float(row['inline_q'])])
  
                self.tfidf_max_X = np.append(self.tfidf_max_X, [float(row['tfidf_top20'])])

                self.provision_blackstone = np.append(self.provision_blackstone, [float(row['provision ent'])])
                self.instrument_blackstone = np.append(self.instrument_blackstone, [float(row['instrument ent'])])
                self.court_blackstone = np.append(self.court_blackstone, [float(row['court ent'])])
                self.case_blackstone = np.append(self.case_blackstone, [float(row['case name ent'])])
                self.citation_blackstone = np.append(self.citation_blackstone, [float(row['citation bl ent'])])
                self.judge_blackstone = np.append(self.judge_blackstone, [float(row['judge ent'])])
                self.loc_ent_X = np.append(self.loc_ent_X, [float(row['loc ent'])])
                self.org_ent_X = np.append(self.org_ent_X, [float(row['org ent'])])
                self.date_ent_X = np.append(self.date_ent_X, [float(row['date ent'])])
                self.person_ent_X = np.append(self.person_ent_X, [float(row['person ent'])])
    
                self.modal_pos_bool_X =  np.append(self.modal_pos_bool_X, [float(row['cp pos bool'])])
                self.modal_dep_bool_X = np.append(self.modal_dep_bool_X, [float(row['cp dep bool'])])
                self.modal_dep_count_X = np.append(self.modal_dep_count_X, [float(row['cp dep count'])])
                self.modal_pos_count_X = np.append(self.modal_pos_count_X, [float(row['cp pos count'])])
                self.new_modal_X = np.append(self.new_modal_X, [float(row['cp modal'])])
                self.new_tense_X = np.append(self.new_tense_X, [float(row['cp tense'])])
                self.new_dep_X = np.append(self.new_dep_X, [float(row['cp dep'])])
                self.new_tag_X = np.append(self.new_tag_X, [float(row['cp tag'])])
                self.new_negative_X = np.append(self.new_negative_X, [float(row['cp negative'])])
                self.new_stop_X = np.append(self.new_stop_X, [float(row['cp stop'])])
                self.new_voice_X = np.append(self.new_voice_X, [float(row['cp voice'])])
  
                self.second_pos_X = np.append(self.second_pos_X, [float(row['cp second pos'])])
                self.second_dep_X = np.append(self.second_dep_X, [float(row['cp second dep'])])
                self.second_tag_X = np.append(self.second_tag_X, [float(row['cp second tag'])])
                self.second_stop_X = np.append(self.second_stop_X, [float(row['cp second stop'])])


        self.location = self.loc1_X, self.loc2_X, self.loc3_X, self.loc4_X, self.loc5_X, self.loc6_X
        self.quotation = self.inq_X, self.qb_X
        self.asmo = self.agree_X, self.outcome_X
        self.sent_length = self.sentlen_X
        self.tfidf_max = self.tfidf_max_X
        self.HGents = self.provision_blackstone, self.instrument_blackstone, self.court_blackstone, self.case_blackstone, self.citation_blackstone, self.judge_blackstone, self.loc_ent_X, self.org_ent_X, self.date_ent_X, self.person_ent_X
        self.cue_phrase = self.modal_dep_bool_X,  self.modal_dep_count_X, self.new_tense_X, self.new_tag_X, self.new_negative_X, self.new_stop_X, self.new_voice_X, self.new_modal_X, self.second_pos_X, self.second_dep_X, self.second_tag_X, self.second_stop_X 
     
        