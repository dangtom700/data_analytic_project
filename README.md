# Introduction to Machine Learning in Mechatronics

## Objectives

- Gain a profound understanding of a diverse range of machine learning algorithms, exploring their principles, functionalisties, and applications
- Develop the capability to evaluate models generated from data, employing techniques to access their accuracy, reliability, and generalization to real-world scenarios.
- Build skills in systematically analyzing complex systems, identifying relevant challenges, and designing effective ML-based solutions for complex diagnostics, monitoring, and control

## Goals

- Explain the strengths and limitations of the various machine leanring algorithms
- Evaluate ML methods performance and select a proper one for your data
Go through the end-to-end pipeline of an ML project (from data cleaning to model evaluation)

## Terminologies

- Artificial intelligent (AI): any effort in the development of computer systems to perform tasks that require human intelligence
- Machine learning (ML): a subset of AI, involves algorithms that allow computers to learn from data rather than being explicitly programmed to do so
- Deep learning (DL): a specialized subset of ML, involves neural networks with several layers (from 1 to hundereds) that can analyze various factors of a dataset
- Generative AI: an advanced subset of AI and DL. GenAI focuses on creating new and unique outputs. It goes beyond the scope of simply analyzing data to making new creations baed on learned patterns

## When to use ML

- A system driven by ML algorithms can learn to make decisions and adapt to its environment
- ML is used when human are unable to explain a system's behavior or when solution needs to be adapted to particular cases

## ML underneath the hood

- Statistics: inference from a sample
- Optimization: a performance criterion evaluation using example data (experience). Every ML algorithm contains an internal optimization algorithm
- Computer science: effecient algorithms to solve the optimization problem and representing and evaluating the model for inference

## Categories of ML

- Supervised (labeled data) are categoried into regression (mapping input variables to some continuous function) and classification (mapping input variables into discrete categories)
- Unsupervised (unlabeled data) are categoried into clustering, dimensionality reduction, outliner detection and association rules learning
- Reinforcement leanring: Ai faces a game-like situation. The computer employs trial and error to come up with a solution to the problem. To get the machine to do what the programmer wants, the AI gets either rewards or penalties for the actions it performs. Its goal is to maximize the total reward

## Machine learning process

In machine learning applications, a data scientist or other analyst

- Identifies relevant data sets and prepares them for analysis
- Chooses the type of machine learning algorithm to use
- Builds an analytical model based on the choosen algorithm
- Trains the model on the data sets, revising it as needed
- Runs the model to generate scores and other findings

Notes:

- Feature engineering: a process that involves determining which features might be useful in training a model and combining existing features to produce a more useful one
- Training: the process of determing the parameter (weights and biases) of an ML model to perform a specific task (regression/classfication)
- Validation: optinal data set to fine tune hyper-parameter of a model
- Test: the process of inputting values that a model has never seen before to get an evaluation of how well the model performs in generalization.

## ML challenges

### Data related issues

- Insufficient quantity of data
- Nonrepresentative data
- Poor quality data
- Irrelevant features

### Algorithm related issues

- Underfitting (high bias): trained model can neither re-produce the training data nor generalize to new data. Poor on both training and generalization. Happens when the model is too simple to learn the underlying structure of the data
- Overfitting (high variance): trained model performs well on the training data, but it generalizes poorly. Happens where a trained model follows the training data too much, or data is too complex, noisy (irrelevant patterns in the training data), or large number of features
