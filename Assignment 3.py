# -*- coding: utf-8 -*-
"""Copy of Assignment3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PbPc7BccIgvgJZdEEEtqpJdIV8RJ6Pyp

# Assignment 3 - PCA and

##Part 1 - PCA: Face Recognition using Eigenfaces

In this part we will implement and apply PCA to a dataset of celebrity faces, before finally building a very simple face classifier. To do this, we are going to: preprocess our images, implement PCA, and finally visualize the results of applying it to our dataset.

Complete the sections of the assignment prefixed with **"TODO"**:

* [2. PCA](#scrollTo=EHMIljnpdaBE)
* [3.1 Eigenfaces](#scrollTo=A_JqQwEmu7ef)
* [3.2 Eigenfaces](#scrollTo=YTdZF-O6daaK)
* [4.2 Face Classification](#scrollTo=IDhubLwVh2Vr)

### 1) Preparing the Dataset

First, we need to download the dataset and preprocess the data. To accomplish this, we will load the images into a (N, H, W) NumPy matrix (where N is the number of images, and H, W are the image dimensions). Furthermore, we will also need to center crop the images to remove the background and only keep the face. In addition, it is also recommended to make sure that the images in our dataset are aligned (e.g. eyes, nose, etc.); fortunately, the dataset we will be using has this already done!

**Bonus:** If you have a few pictures of your friends, you can also add them to the dataset! Later on, we will be building a face recognition system which you can use on your own photos.

#### 1.1) First, download the dataset and extract the images
"""

# Download the dataset (subset of CelebA).
!wget -O a3_face_dataset.tar.gz https://www.dropbox.com/s/4nmsiafyvw0o5fx/a3_face_dataset.tar.gz?dl=0

# Extract the contents of the compressed file.
!tar xzf a3_face_dataset.tar.gz
!ls

"""#### 1.2) Preview a few images from the dataset"""

import glob
import matplotlib.pyplot as plt
from IPython.display import display, Image

# Display the first images from the dataset. You can also browse these by
# navigating through the notebook's file system!
sample_images = glob.glob('a3_face_dataset/*.jpg')[:5]
for file_path in sample_images:
  display(Image(file_path))

"""#### 1.3) Load the dataset and convert into a NumPy matrix"""

import cv2
import numpy as np

# Load images in greyscale.
image_paths = list(glob.glob('a3_face_dataset/*.jpg'))
images = np.stack([cv2.imread(str(x), cv2.IMREAD_GRAYSCALE) 
                   for x in image_paths])
print('Original Image Shape (N, H, W):', images.shape)

"""####1.4) Center crop the images and visualize the results"""

import PIL

# Helper function for cropping the center of the image to remove the background
# and only keep the face.
def center_crop(img):
    h, w = img.shape
    center_y, center_x = h // 2, w // 2
    offset_y, offset_x = center_y // 2, center_x // 2
    return img[center_y - offset_y: center_y + offset_y,
               center_x - offset_x: center_x + offset_x]
  
# Center crop our images.
images = np.stack([center_crop(img) for img in images])
img_height, img_width = images.shape[1:3]
print('Cropped Image Shape (N, H, W):', images.shape)

# Visualize a few results.
for i in range(5):
  display(PIL.Image.fromarray(images[i]))

"""####1.5) Lastly, flatten each image into a single vector"""

# Flatten the images into a (N, HxW) sized array, where N is the number of 
# images and H, W are the dimensions of the image.
num_images = len(images)
images = images.reshape(num_images, -1)
print('Matrix Shape (N, H*W):', images.shape)

"""### 2) PCA Implementation

**Note that there are several methods to solve for the eigenvectors of a matrix; for this assignment, you must use the eigenvectors of $A^TA$ to solve for those
of $AA^T$. Please read the following 'Theory' section carefully for more details.**

#### 2.1) Theory

The simplest way to implement PCA is to compute the covariance
matrix and solve for the eigenvalues and eigenvectors. For the derivation,
we will use the notation that our input, $A$, is a matrix with a row for each pixel in the input image, and a column for each sample (i.e., $A = X^T$). In this case, that means $A$ should be a $9504$x$500$ dimensional matrix, where $n=500$. Lastly, we will also presume that $X$ is zero-centered and has a mean of zero.

The covariance matrix is given by $\mathrm{cov}(A) =  \frac{1}{n}AA^T$, resulting in a $9504$x$9504$ matrix for which we need to solve the eigenvalues and eigenvectors. In reality, this approach is impractical as it is extremely time consuming to work with such large matrices (e.g. if we were to work with HD images, the number of elements in this matrix would be of the order of $10^{12}$).

Instead, we will use a clever trick to work around this: if we can find a mapping between the eigenvectors of $\mathrm{cov}(A^T)$ to those of $\mathrm{cov}(A)$, then we only have to work with a $500$x$500$ matrix. This saves an immense amount of computation so long as the number of data samples is less than the number of pixels (which is almost always the case).

**Your task will be to complete / make sense of the following derivation, and then use it to implement PCA.** As an aside, note that the constant term $n$ has been omitted for simplification.
$$
\mathrm{cov}(A^T)v = \lambda v \\
A^TAv =  \lambda v \\
AA^TAv = A\lambda v \\
...
$$
____________________________________________________

For further reading, please refer to the class notes and the following resources as a guideline for implementing PCA. Keep in mind that notation may vary between resources; make sure that your matrices are arranged in the correct order:
* https://en.wikipedia.org/wiki/Eigenface  
* https://en.wikipedia.org/wiki/Eigenface#Computing_the_eigenvectors  
* http://www.vision.jhu.edu/teaching/vision08/Handouts/case_study_pca1.pdf  
* http://www.face-rec.org/algorithms/pca/jcn.pdf

#### 2.2) Implementation

For this assignment we will be implementing PCA using only linear algebra libraries. As a guideline, we will loosely follow
the interface of the scikit-learn version of PCA.
"""

class PCA:
    """
    Custom implementation of PCA with an interface similar to scikit-learn's version of PCA.
    """

    def __init__(self, n_components):
        self.n_components_ = n_components
        self.mean_ = None
        self.components_ = None
        self.eigenvalues_ = None

    # TODO
    def fit(self, x):
        x = x.astype(np.float32)

        # Normalize X so that it has a mean of 0. You can accomplish this
        # by computing the mean image vector and subtracting it from X.
        # The mean should be assigned to the 'self.mean_' attribute.
        # --> Your code here <--
        self.mean_ = x.mean(axis=0)
        x = x - self.mean_

        # Set-up your variables, A, and A^TA
        # --> Your code here <--
        A = x.T
        At_A = np.matmul(x,A)

        # Sanity check.
        assert A.shape == (9504, 500)
        assert At_A.shape == (500, 500)

        # Compute the eigenvectors using the method discussed above.
        # --> Your code here <--
        cov_At = (1/500)*(At_A)
        (w, v) = np.linalg.eig(cov_At)
        eigenvectors = np.matmul(A,v)

        # Tranpose the dimensions of your eigenvectors to return to the
        # notation where each eigenvector is it's own row.
        eigenvectors = eigenvectors.T
        assert eigenvectors.shape == (500, 9504)

        # Ensure that each of the N eigenvectors are normalized to a magnitude of 1.
        # --> Your code here <--
        for i in range(eigenvectors.shape[0]):
          eigenvectors[i] /= (np.linalg.norm(eigenvectors[i]))

        # Only retain the best N components (eigenvectors). These should be assigned
        # to the 'self.components_' attribute.
        # --> Your code here <--
        eigs = {}
        for i in range(w.shape[0]):
          eigs[w[i]] = eigenvectors[i]
        sorted_eigs = sorted(eigs.items(),key=lambda x:x[0],reverse=True)
        result = []
        for i in range(self.n_components_):
          result.append(sorted_eigs[i][1])
        self.components_ = np.array(result)

        # Keep all of the eigenvalues, but make sure to sort them. This is done so we can
        # visualize the variance versus number of components kept later in the assignment.
        # This should be assigned to the 'self.eigenvalues_' attribute.
        # --> Your code here <--
        self.eigenvalues_ = np.sort(w)
        assert self.eigenvalues_.shape == (500, )

    def transform(self, x):
      x = x.astype(np.float32)
      result = None

      # Project the input vector 'x' onto your PCA object's principal
      # components and return the result. Make sure you subtract the mean face
      # like in the fit(...) method.
      # --> Your code here <--
      x = x - x.mean(axis=0)
      result = (self.components_)@(x.T)
      return result

    def fit_transform(self, x):
        self.fit(x)
        return self.transform(x)

"""### 3) Computing Eigenfaces

With the implementation of PCA complete, lets try running it on our dataset and visualizing some of the eigenfaces of the training set. To accomplish this, we first run PCA on the training matrix and then we take the eigenvectors and plot them as 2D images.

####3.1) Perform PCA on our image matrix
"""

# Settings
num_components = 50

# TODO: PCA. Create a PCA instance and fit it on the training data.
# --> Your code here <--
pca = PCA(num_components)
pca.fit(images)

pca.components_.shape

"""####3.2) Visualize the eigenfaces"""

import os

# Output directory.
os.makedirs('./eigenfaces/', exist_ok=True)

# Visualize the mean face.
print('Saving mean face...', end='')
mean_face = pca.mean_.reshape(img_height, img_width)
norm_img = cv2.normalize(mean_face, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
cv2.imwrite('./eigenfaces/mean_face.png', norm_img)
print('Done.')

# TODO: Visualize the first few eigenfaces, and save them as './eigenfaces/eigenface_{i}.png'.
# Don't forget to normalize the image like the the mean face example above.
print('Saving first ten eigen-faces to ./outputs/...', end='')
eigenfaces = pca.components_.reshape(num_components, img_height, img_width)[:10]
# --> Your code here <--
for i in range(10):
  norm_img = cv2.normalize(eigenfaces[i],None,0,255,cv2.NORM_MINMAX).astype(np.uint8)
  cv2.imwrite('./eigenfaces/eigenface_{}.png'.format(i),norm_img)

# Display the mean face and eigenfaces. You can also browse these by
# navigating through the notebooks file system (see left side toolbar)!
print('Mean Face')
display(Image('./eigenfaces/mean_face.png'))

print('Eigenfaces')
for i in range(10):
  display(Image(f'./eigenfaces/eigenface_{i}.png'))

"""####3.3) Variance versus number of components"""

import matplotlib.pyplot as plt

# Compute the cumulative sum of total variance as we increase the number of 
# principal components we use.
n_components_to_plot = 300
total_variance = sum(pca.eigenvalues_)
var_exp = [(i / total_variance) * 100 for i in
           sorted(pca.eigenvalues_, reverse=True)[:n_components_to_plot]]
cum_var_exp = np.cumsum(var_exp)

# Generate the plot.
plt.step(range(1, n_components_to_plot + 1), cum_var_exp)
plt.title('Fraction of Total Variance versus Number of Components')
plt.ylabel('Fraction of Total Variance')
plt.xlabel('Number of Components')
plt.show()

"""### 4) Face Recognition

In this section, we're going to build a simple face recognition system using eigenfaces. To accomplish this, we're going to take a test image and project it onto our principal components learned from our training set of celebrity faces. Finally, we will compare the resulting vector to all of the other faces in the training set and find the closet match based on Euclidean distance (i.e., 1-nearest-neighbour classification).

For instance, this training set has photos of Obama—in theory then, if we were to test another photo of Obama (not in the training set, cropped and aligned), we should find that the closest match in the training set will also be a photo of Obama.

#### 4.1) Download the test image
"""

# Download a photo of Obama which isn't in the training set.
!wget -O "006357.jpg" https://www.dropbox.com/s/ffw2621k0gmix1z/006357.jpg?dl=0
display(Image('006357.jpg'))

"""#### 4.2) Find the closet image in the training set to our test image"""

from numpy.linalg import norm

# Load our test image into a NumPy matrix
test_img = center_crop(cv2.imread('006357.jpg', cv2.IMREAD_GRAYSCALE))
test_img = np.expand_dims(test_img.flatten(), axis=0)

# TODO: Transform our training matrix and test image using our PCA implementation
# from earlier.
# --> Your code here <--
images = pca.transform(images).T
test_img = pca.transform(test_img)

# TODO: For our face recognition classifier, we will use a 1-nearest-neighbour
# model. The classifier should return the index of the best matching image.
# --> Your code here <--
best_match_index = None
min = np.linalg.norm(images[0].reshape(50,1)-test_img)
best_match_index = 0
for i in range(500):
  dist = np.linalg.norm((images[i].reshape(50,1)-(test_img)))
  if dist < min:
    min = dist
    best_match_index = i


#print((np.linalg.norm(images[best_match_index].reshape(50,1)-(test_img))))
# If all goes well, the best match in our training set should be another
# photo of Obama.
print('Best match:', image_paths[best_match_index])
display(Image(image_paths[best_match_index]))

"""## Theoretical questions

#### Explain the difference between overfitting and underfitting

Underfitting occurs when our model does not capture the main trend of data in the dataset, whereas overfitting happens when our model captures too much detail about the dataset. Underfitting renders high bias and low variance while overffiting results in low bias and high variance.

####Explain bagging and boosting. Clearly illustrate the difference between these methods. (less than 4 sentances)

Both bagging and boosting reduces variance in a model by generating additionally multiple sets out of a dataset by randomly selecting data with replacement. 
In bagging, each data has the same probablity to be selected.
While in boosting, weights of some data are adjusted so that some appear more often than the other in selection.

#### What is a DECISION TREE (less than 3 sentances)? What are the advantages and disadvantages of a decision tree?

Decision tree is a tree-structure classification model in which each internal node represents a feature and each leaf represents a label.
Advantages: easy to reason about and to implement
            ;no need for normalization or scaling.
Disadvantages: high variance so behaving poorly on unseen data;
                susceptible to overfitting

#### What is a RANDOM FOREST (less than 3 sentances)? What are the advantages and disadvantages of a random forest compared to a decision tree?

Random Forest is a classification model that bags several decision trees.
Advantages: not as easy to overfit as a single decision tree; high accuracy; still no need for normalizing or scaling.
Disadvantages: training process very complex and time consuming.
"""