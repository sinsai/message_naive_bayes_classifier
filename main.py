#!/use/bin/env python
# -*- coding:utf-8 -*-
import sys
import simplejson
import model
import mecab
import nltk
from collections import defaultdict
import cPickle as pickle

mecab_path = "/usr/lib/libmecab.so.1"

class ShNaiveBayes(object):
    def __init__(self):
        self.all_words = set()

    def getAuthData(self, fileName):
        file = open(fileName,'r')
        a = simplejson.loads(file.read())
        file.close()
        return a

    def sparse_sentence(self, s):
        #print s
        s_sparse =\
        mecab.sparse_all(s.encode("utf-8"),mecab_path).split("\n")[:-2]
        candidate = set()
        for s2 in s_sparse: # この時点で単語レベルのハズ(ただしs2=単語 品詞
                            # とかかなぁ
            #print "s2",
            s3 = s2.decode("utf-8").split("\t")
            s4 = s3[1].split(",")
            #print s3[0],s4[0]
            if s4[0] != u"記号" and s4[0] != u"助動詞" \
                and s4[0] != u"助詞":#数が集まったら名詞のみにしたい
                candidate.add(s3[0])
        return candidate
    
    def create_data(self, message, bows, flag = None):
        words = dict()
        sparce_words = self.sparse_sentence(message)
        for s in sparce_words:
            words[s] = 1
            if flag != None: self.all_words.add(s)
        if flag != None: data = [words, flag]
        else: data = (words)
        bows.append(data)

    def append_bows(self, query, bows, flag = None):
        sentences = []
        for q in query:
            if q.message == None: continue
            self.create_data(q.message, bows, flag)
            sentences.append(q.message)
        return sentences

    def complete_bows(self, tmp_bows, test = False):
        bows = []
        for b in tmp_bows:
            new_b0 = dict()
            for a2 in self.all_words:
                if test:
                    new_b0[a2] = 0 if a2 in b else 1 #complemental
                else:
                    new_b0[a2] = 0 if a2 in b[0] else 1 #complemental
            if test:
                bows.append((new_b0 ))
            else:
                bows.append((new_b0, b[1] ))
        return bows

    def learn(self):
        print "learn start"

        tmp_bows = []
        bows = []
        # まず正解データを読み込む
        correct_query = self.dbSession.query(model.Message).filter(\
            model.Message.message_type==1).limit(1000)
        self.append_bows(correct_query, tmp_bows,"True")

        wrong_query = self.dbSession.query(model.Message).filter(\
            model.Message.message_type==3).limit(1000)
        self.append_bows(wrong_query, tmp_bows,"False")

        bows = self.complete_bows(tmp_bows)
        self.classifier = nltk.NaiveBayesClassifier.train(bows)
        print "end learn"

    def batch_test(self):
        test_bows = []
        tmp_bows = []
        test_query = self.dbSession.query(model.Message).filter(\
            model.Message.message_type==1).slice(2000, 2100)
        test_sentences = self.append_bows(test_query, tmp_bows)
        
        test_bows = self.complete_bows(tmp_bows, test = True)
        #print test_bows
        pdists = self.classifier.batch_prob_classify(test_bows)
        for i in xrange(len(pdists)):
            print "%s : %.4f" % (test_sentences[i] ,pdists[i].prob("True"))

    def prob_classify(self, sentence):
        tmp_bows = []
        self.create_data(sentence, tmp_bows)
        bows = self.complete_bows(tmp_bows, test = True)
        return self.classifier.prob_classify(bows[0]).prob("True")

    def write_probdist(self):
        f = open("label_probdist.dat", "w")
        f.write( pickle.dumps(self.classifier._label_probdist) )
        f.close()

        f = open("feature_probdist.dat", "w")
        f.write( pickle.dumps(self.classifier._feature_probdist) )
        f.close()

        f = open("all_words.dat", "w")
        f.write( pickle.dumps(self.all_words))
        f.close()

    def read_probdist(self):
        f = open("label_probdist.dat")
        label_probdist = pickle.loads(f.read() )
        f.close()

        f = open("feature_probdist.dat")
        feature_probdist = pickle.loads(f.read() )
        f.close()

        f = open("all_words.dat")
        self.all_words = pickle.loads(f.read())
        f.close()

        self.classifier = nltk.NaiveBayesClassifier(label_probdist,
            feature_probdist)
    
    def init_session(self):
        userdata = self.getAuthData("./config.json")
        self.dbSession = model.startSession(userdata)
    
    def main(self):
        self.init_session()
        self.learn()
        self.write_probdist()
        self.batch_test()


if __name__ == "__main__":

    s = ShNaiveBayes()

    #s.main()
    s.init_session()
    #s.learn()
    #s.write_probdist()
    #s.classifier = None
    s.read_probdist()
    s.batch_test()
    #print s.prob_classify(u"茨城県北部はライフラインがほぼ全滅。原発100キロ圏内にあります。救援物資も大変不足しておりますが報道も皆無に等しく茨城県が取り残されています。一刻も早い状況の把握と救援をお願いします。助けてください。")
