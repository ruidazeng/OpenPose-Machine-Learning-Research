import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier


# load a single file as a numpy array
def load_file(filepath):
    dataframe = pd.read_csv(filepath, header=None)
    return dataframe.values


# load a dataset group, such as train or test, return them in the form of DataFrame
def load_dataset_group(data_type, group, prefix, filenames):
    # create a list for x
    x = []
    # load input data
    for name in filenames:
        data = load_file(prefix + data_type + '/' + group + name + '_' + data_type + '.csv')
        x.extend(data)
    df_x = pd.DataFrame(x)
    if data_type == 'Processed_PatientSpace':
        df_x.drop(df_x.columns[0:36], axis=1, inplace=True)
    # create a list for y
    y = []
    # load output data
    for name in filenames:
        data = load_file(prefix + 'Processed_Label/' + group + name + '_label.csv')
        y.extend(data)
    df_y = pd.DataFrame(y)
    return df_x, df_y


# process the feature data using the histogram method
def process_data(feature, dimension, size):
    processed_list = []
    for index, row in feature.iterrows():
        processing_list = []
        for n in range(dimension):
            if dimension == 36:
                processing_list.append(row[n + 36] // size)
            else:
                processing_list.append(row[n] // size)
        processed_list.append(processing_list)
    df_feature = pd.DataFrame(processed_list)
    return df_feature


# load the dataset, returns train and test x and y elements
def load_dataset(data_type, prefix, train_files, test_files, dimension, size):
    # load all train
    trainx, trainy = load_dataset_group(data_type, 'train/', prefix, train_files)
    print(trainx.shape, trainy.shape)
    # process the feature data
    trainx = process_data(trainx, dimension, size)
    print(trainx.shape, trainy.shape)
    # load all test
    testx, testy = load_dataset_group(data_type, 'test/', prefix, test_files)
    print(testx.shape, testy.shape)
    # process the feature data
    testx = process_data(testx, dimension, size)
    print(testx.shape, testy.shape)
    # flatten y
    trainy = trainy.values.flatten()
    testy = testy.values.flatten()
    print(trainx.shape, trainy.shape, testx.shape, testy.shape)
    return trainx, trainy, testx, testy


# create a dict of standard models to evaluate {name:object}
def define_models(models=dict()):
    # nonlinear models
    models['knn'] = KNeighborsClassifier(n_neighbors=7)
    models['cart'] = DecisionTreeClassifier()
    models['svm'] = SVC(gamma='scale')
    models['bayes'] = GaussianNB()
    # ensemble models
    models['bag'] = BaggingClassifier(n_estimators=10)
    models['rf'] = RandomForestClassifier(n_estimators=100)
    models['et'] = ExtraTreesClassifier(n_estimators=100)
    models['gbm'] = GradientBoostingClassifier(n_estimators=100)
    print('Defined %d models' % len(models))
    return models


# evaluate a single model
def evaluate_model(trainx, trainy, testx, testy, model):
    # fit the model
    model.fit(trainx, trainy)
    # make predictions
    yhat = model.predict(testx)
    # evaluate predictions
    accuracy = accuracy_score(testy, yhat)
    print(confusion_matrix(testy, yhat))
    print(classification_report(testy, yhat))
    return accuracy * 100.0


# evaluate a dict of models {name:object}, returns {name:score}
def evaluate_models(trainx, trainy, testx, testy, models):
    results = dict()
    for name, model in models.items():
        # evaluate the model
        results[name] = evaluate_model(trainx, trainy, testx, testy, model)
        # show process
        print('>%s: %.3f' % (name, results[name]))
    return results


# print and plot the results
def summarize_results(results, maximize=True):
    # create a list of (name, mean(scores)) tuples
    mean_scores = [(k, v) for k, v in results.items()]
    # sort tuples by mean score
    mean_scores = sorted(mean_scores, key=lambda x: x[1])
    # reverse for descending order (e.g. for accuracy)
    if maximize:
        mean_scores = list(reversed(mean_scores))
    print()
    for name, score in mean_scores:
        print('Name=%s, Score=%.3f' % (name, score))


def main():
    # User can change the name these training or testing files
    train_files = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
    test_files = ['S7']

    # data_type can be 'Processed_PatientSpace' or 'Processed_RawXY'
    data_type = 'Processed_PatientSpace'
    # path
    path = '/Users/wangyan/Desktop/Research/Experiment_2/'

    # User can adjust the number of windows for the histogram
    window_num = 40

    if data_type == 'Processed_PatientSpace':
        dimension = 36
        # the max distance is calculated by sqrt(1000^2 + 2000^2)
        max_dist = 4472.23595
    else:
        dimension = 72
        max_dist = 4000

    # calculate the size of each window
    size = max_dist / window_num

    # load dataset
    trainx, trainy, testx, testy = load_dataset(data_type, path, train_files, test_files, dimension, size)

    # get model list
    models = define_models()

    # evaluate models
    results = evaluate_models(trainx, trainy, testx, testy, models)

    # summarize result
    summarize_results(results)


main()
