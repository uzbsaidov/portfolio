from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
import numpy as np

class SurveyClustering:
    def __init__(self):
        self.model = None

    def find_optimal_k(self, X, k_range=range(2, 8)):
        scores = {}
        for k in k_range:
            if k >= len(X):
                break
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = km.fit_predict(X)
            if len(np.unique(labels)) < 2:
                continue
            scores[k] = silhouette_score(X, labels)
        if not scores:
            return 2, {2: 0.0}
        best_k = max(scores, key=scores.get)
        return best_k, scores

    def fit_predict(self, X, k=4):
        k = min(k, len(X) - 1)
        self.model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = self.model.fit_predict(X)
        return labels

    def get_elbow_data(self, X, max_k=10):
        inertias = {}
        silhouettes = {}
        for k in range(1, min(max_k + 1, len(X))):
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            lbl = km.fit_predict(X)
            inertias[k] = round(float(km.inertia_), 2)
            if k >= 2 and len(np.unique(lbl)) >= 2:
                silhouettes[k] = round(float(silhouette_score(X, lbl)), 3)
        return inertias, silhouettes
