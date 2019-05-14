import argparse
import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble.gradient_boosting import GradientBoostingClassifier


def get_data(path="iris/iris.data", seed=None, test_size=0.3):
    df = pd.read_csv(path, names=["x1", "x2", "x3", "x4", "y"])
    labels = df["y"]
    features = df.drop("y", axis=1)
    return train_test_split(features, labels, test_size=test_size, random_state=seed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datafile", default="iris/iris.data", help="path to iris data")
    parser.add_argument("-s", "--seed", default=0, type=int, help="random seed to be used")
    parser.add_argument("-t", "--test_size", default=0.3, type=float, help="size of test set")
    args = parser.parse_args()

    train_features, test_features, train_labels, test_labels = get_data(path=args.datafile, seed=args.seed,
                                                                        test_size=args.test_size)

    xgb = GradientBoostingClassifier(n_estimators=5)
    hyperparameters = dict(
        n_estimators=list(range(1, 20)),
        min_samples_split=list(range(2, 10)),
        max_depth=[2, 3, 4],
        max_features=[2, 3, 4],
    )
    searcher = RandomizedSearchCV(xgb, param_distributions=hyperparameters, n_iter=40, cv=3, iid=False,
                                  random_state=args.seed)

    print("training on {} samples".format(train_features.shape[0]))
    searcher.fit(train_features, train_labels)

    print("Classification yields a best score of {} with {}".format(searcher.best_score_, searcher.best_params_))
    best_model = searcher.best_estimator_

    print("testing on {} samples".format(test_features.shape[0]))
    best_model.fit(train_features, train_labels)
    score = best_model.score(test_features, test_labels)
    print("testing score = {}".format(score))
