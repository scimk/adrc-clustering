#!/home/mkhali8/anaconda2/envs/adrc-clustering/bin/python

import os
import sys
import argparse
import numpy as np
from sklearn.cluster import KMeans
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from libs.features import *
from libs.clustering import *
from config import *

# Define functions
def compute_sse(X): 
	""" compute_sse
	Compute the sum of squared error for n clusters
	"""
	sse = []
	n_clusters = range(2,15)

	for n in n_clusters:
		km = KMeans(n_clusters=n)
		clustering = km.fit(X)
		sse.append(sum_squared_error(A, clustering.cluster_centers_, km.labels_))

	plot_sse(sse, n_clusters, os.path.join(results_dir, 'sse.png'))

def compute_di(X): 
	""" compute_di
	Compute dunn index for n clusters
	"""
	di = []
	n_clusters = range(2,15)

	for n in n_clusters:
		km = KMeans(n_clusters=n)
		clustering = km.fit(X)
		sse.append(sum_squared_error(A, clustering.cluster_centers_, km.labels_))

	plot_dunn_index(di, n_clusters, os.path.join(results_dir, 'dunn_index.png'))

if __name__ == "__main__":
	# Parse command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-k", "--n_clusters", default=4, type=int, help="number of clusters")
	parser.add_argument("-i", "--input", default=INPUT_FILE, help="Input file (full path)")
	parser.add_argument("-o", "--output", default=OUTPUT_DIR, help="Output directory")
	parser.add_argument("-sse", "--squared_error", help="Compute sum of squared error", action="store_true")
	parser.add_argument("-di", "--dunn_index", help="Compute dunn index", action="store_true")
	args = parser.parse_args()

	# Initialize some variables
	results_dir = os.path.join(args.output, "k"+str(args.n_clusters))							# output dir
	
	# Read patient data from CSV file and convert into Dict
	# Aggregate verbal fluency tests and compute patient 
	# graph and its features
	patients = read_data_from_file(args.input)
	patients = aggregate_fluency_tests(patients)
	patients = word_graph(patients)

	# Generate feature vector matrix using graph features
	n = len(patients)																			# number of patients
	m = len(patients[0].features) + 1 															# number of features
	X = np.zeros(shape=(n,m))																	# Feature matrix
	features = patients[0].features.keys() + ["errors"]

	for patient in patients:
		X[patient.index] = patient.features.values() + [len(patient.errors)]

	if args.squared_error:
		compute_sse(X)
	if args.dunn_index:
		compute_di(X)

	# Run k-means for some k clusters
	km = KMeans(n_clusters=args.n_clusters)
	clustering = km.fit(X)
	centers = clustering.cluster_centers_
	labels = list(set(km.labels_))

	# Given the matrix A and cluster labels
	# Compute distance between centers and patients
	# Reorder the matrix, then save the image
	reordered_dist_matrix(X, km.labels_, os.path.join(results_dir, 'reordered_sim_matrix.png'))

	# Save cluster centers and TF-IDF values for words in each cluster
	clust_centroids = cluster_centroids(X, patients, centers, km.labels_)
	cluster_word_importance(patients, km.labels_, os.path.join(results_dir, 'tfidf.csv'))

	# Find representitive patients for each cluster and save
	# their verbal fluency graph
	for label, centroids in clust_centroids.iteritems():
		for centroid in centroids:
			nx.draw_spectral(centroid.graph)
			output = os.path.join(results_dir, 'cluster_%d_%d.png' % (label, centroid.index))
			plt.savefig(output)
			plt.clf() 

	# Write cluster center to file
	with open(os.path.join(results_dir, "cluster_centers.csv"), "w") as fh:
		w = csv.writer(fh)
		w.writerow(features)

		for center in centers:
			w.writerow(center)
