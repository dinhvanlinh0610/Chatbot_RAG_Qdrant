import numpy as np
import json
import os

class SemanticRouter():
    def __init__(self, embedding, routes):
        self.routes = routes
        self.embedding = embedding
        self.routesEmbedding = {}


        for route in self.routes:
            self.routesEmbedding[route.name] = self.embedding.encode(route.samples)

    def get_routes(self):
        return self.routes

    def guide(self, query):
        queryEmbedding = self.embedding.encode([query])
        queryEmbedding = queryEmbedding / np.linalg.norm(queryEmbedding)
        scores = []

        for route in self.routes:
            routesEmbedding = self.routesEmbedding[route.name] / np.linalg.norm(self.routesEmbedding[route.name])
            score = np.mean(np.dot(queryEmbedding, routesEmbedding.T).flatten())
            scores.append((score, route.name))

        scores.sort(reverse=True)
        best_route = scores[0]

        return best_route
