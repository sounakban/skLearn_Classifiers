#Feature Extraction
from nltk.corpus import reuters
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from nltk.corpus import stopwords
stop_words = stopwords.words("english")
import cooccurence_main
from text_processing import tokenize, get_TF, get_TFIDF
import numpy

#Classification
from CopulaClassifier import CopulaClassifier

#Evaluation
from sklearn.metrics import f1_score, precision_score, recall_score

#Common
from sys import getsizeof
import time
def print_time(start_time):
    tm = time.time() - start_time
    if tm > 100:
        return "{} minuites".format(tm/60.0)
    else:
        return "{} seconds".format(tm)



#Take required user inputs
weight = input("Enter weighing algorithm in QUOTES [tf or tfidf] : ")
if weight != "tfidf" and weight != "tf":
    raise ValueError ("Unrecognised option for weighing algorithm.")
cor_type = input("Enter correlation coefficient in QUOTES [P for PMI, J for Jaccard] : ")
if cor_type != "J" and cor_type != "j" and cor_type != "P" and cor_type != "p":
    raise ValueError ("Unrecognised option for correlation coefficient.")

start_time = time.time()
program_start = start_time


#----------------Feature Extraction--------------------------

# List documents & ids
documents = reuters.fileids()

train_docs_id = list(filter(lambda doc: doc.startswith("train"), documents))
test_docs_id = list(filter(lambda doc: doc.startswith("test"), documents))

train_docs = [reuters.raw(doc_id) for doc_id in train_docs_id]
test_docs = [reuters.raw(doc_id) for doc_id in test_docs_id]

# Transform for multilabel compatibility
mlb = MultiLabelBinarizer()
train_labels = mlb.fit_transform([reuters.categories(doc_id) for doc_id in train_docs_id])
test_labels = mlb.transform([reuters.categories(doc_id) for doc_id in test_docs_id])

print "Building file list complete and it took : ", print_time(start_time)
start_time = time.time()

#Process all documents
if (weight == "tf" and cor_type == "J") or cor_type == "P":
    # Learn and transform documents [tf]
    vectorizer_tf = CountVectorizer(stop_words=stop_words, tokenizer=tokenize)
    vectorised_train_documents_tf = vectorizer_tf.fit_transform(train_docs)
    vectorised_test_documents_tf = vectorizer_tf.transform(test_docs)
if weight == "tfidf":
    # Learn and transform documents [tfidf]
    vectorizer_tfidf = TfidfVectorizer(stop_words=stop_words, tokenizer=tokenize)
    vectorised_train_documents_tfidf = vectorizer_tfidf.fit_transform(train_docs)
    vectorised_test_documents_tfidf = vectorizer_tfidf.transform(test_docs)

#Devide features by class
if (weight == "tf" and cor_type == "J") or cor_type == "P":
    vocab_tf = {}
    for i in range(train_labels.shape[1]):
        classdoc_ids = numpy.nonzero(train_labels[:, i])[0].tolist()
        vocab_tf[i] = get_TF(vectorizer_tf, vectorised_train_documents_tf, classdoc_ids)
    vocab_choice = vocab_tf
if weight == "tfidf":
    vocab_tfidf = {}
    for i in range(train_labels.shape[1]):
        classdoc_ids = numpy.nonzero(train_labels[:, i])[0].tolist()
        vocab_tfidf[i] = get_TFIDF(vectorizer_tfidf, vectorised_train_documents_tfidf, classdoc_ids)
    vocab_choice = vocab_tfidf

print "Generating term-weights complete and it took : ", print_time(start_time)
start_time = time.time()

#Find cooccurences for all classes
cooccurences_by_class = cooccurence_main.get_cooccurences(train_labels, train_docs)

print "Generating term-cooccurences complete and it took : ", print_time(start_time)
start_time = time.time()

#Find Correlation Coefficient Values
if cor_type == "J" or cor_type == "j":
    vocab_raw = {}
    for i in range(train_labels.shape[1]):
        classdoc_ids = numpy.nonzero(train_labels[:, i])[0].tolist()
        vocab_raw[i] = get_TF(vectorizer_tf, vectorised_train_documents_tf, classdoc_ids, raw_tf=True)
    corcoeff = cooccurence_main.calc_corcoff(cooccurences_by_class, vocab_raw, cor_type)
elif cor_type == "P" or cor_type == "p":
    corcoeff = cooccurence_main.calc_corcoff(cooccurences_by_class, vocab_tf, cor_type)


print "Calculating correlation-coefficients complete and it took : ", print_time(start_time)
start_time = time.time()



#----------------Classification--------------------------

classifier = CopulaClassifier(corcoeff, vocab_choice)
predictions = classifier.predict_multilabel(test_docs[0:10])

print "The Classification is complete and it took", print_time(start_time)
start_time = time.time()


print "Original:"
print test_labels[0:10]
print "Predicted:"
print predictions

"""
#-----------------Evaluation ----------------------
precision = precision_score(test_labels[0:10], predictions, average='micro')
recall = recall_score(test_labels[0:10], predictions, average='micro')
f1 = f1_score(test_labels[0:10], predictions, average='micro')

print("Micro-average quality numbers")
print("Precision: {:.4f}, Recall: {:.4f}, F1-measure: {:.4f}".format(precision, recall, f1))

precision = precision_score(test_labels[0:10], predictions, average='macro')
recall = recall_score(test_labels[0:10], predictions, average='macro')
f1 = f1_score(test_labels[0:10], predictions, average='macro')

print("Macro-average quality numbers")
print("Precision: {:.4f}, Recall: {:.4f}, F1-measure: {:.4f}".format(precision, recall, f1))

print "Evaluation complete and it took : ", print_time(start_time)

print "Total time taken : ", (time.time() - program_start)/60.0, "minuites"
"""







"######################### Bugs #########################"

#print "Documents : ", getsizeof(documents)

#print numpy.nonzero(train_labels[4, :])[0].tolist()

"""
Rows: Docs ; Columns: Terms
print vectorised_test_documents_tfidf[[1, 3], :].shape
print vectorised_test_documents_tfidf.shape
print len(train_docs), " : ", vectorised_train_documents_tfidf.shape
print len(test_docs), " : ", vectorised_test_documents_tfidf.shape
"""

"""
print numpy.nonzero(vocab_tf[4].values())
print vocab_tf[4].keys()[9], " : ", vocab_tf[4].values()[9]
"""

"""
print "cooccurences_by_class : ", getsizeof(cooccurences_by_class)
print cooccurences_by_class[4].values()
"""

#print corcoeff[4].values()[:20]
