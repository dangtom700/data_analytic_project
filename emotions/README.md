# Emotion analysis

This collection of EEG brainwave data was analyzed using our unique statistical extraction approach (see the paper below).

Two individuals—one male and one female—were asked to provide data for three minutes in each of the following states: positive, neutral, and negative. The TP9, AF7, AF8, and TP10 EEG locations were recorded using dry electrodes and a Muse EEG headgear. The stimuli used to elicit the emotions are listed below, along with six minutes of resting neutral data.

Source link:
- [EEG Brainwave Dataset: Feeling Emotions Positive and Negative emotional experiences captured from the brain](https://www.kaggle.com/datasets/birdy654/eeg-brainwave-dataset-feeling-emotions)
- https://www.researchgate.net/publication/329403546_Mental_Emotional_Sentiment_Classification_with_an_EEG-based_Brain-machine_Interface
- https://www.researchgate.net/publication/335173767_A_Deep_Evolutionary_Approach_to_Bioinspired_Classifier_Optimisation_for_Brain-Machine_Interaction

Citations:
- J. J. Bird, L. J. Manso, E. P. Ribiero, A. Ekart, and D. R. Faria, “A study on mental state classification using eeg-based brain-machine interface,”in 9th International Conference on Intelligent Systems, IEEE, 2018.
- J. J. Bird, A. Ekart, C. D. Buckingham, and D. R. Faria, “Mental emotional sentiment classification with an eeg-based brain-machine interface,” in The International Conference on Digital Image and Signal Processing (DISP’19), Springer, 2019.

---

# Cognitive State Data

The Cognitive State Discrimination Dataset was collected using a 64-channel electroencephalography (EEG) system at a sampling rate of 512 Hz. The EEG electrodes were placed according to the international 10-20 system, ensuring standard placement for optimal brain wave capture. The dataset comprises EEG recordings from multiple participants as they performed a series of cognitive tasks designed to elicit different mental states.

Source: [Conigitive State Data](https://www.kaggle.com/datasets/ziya07/cognitive-state-data)

1. Participant and Task Information:

- Participants: Human subjects (with individual identifiers provided in the Participant_ID column) engaged in various cognitive tasks.
- Tasks: The tasks include memory recall, arithmetic calculations, and visual pattern recognition, chosen to invoke different cognitive states, such as attention, working memory, and problem-solving.

2. Data Collection Protocol:

The EEG data was recorded in a controlled laboratory environment designed to minimize external distractions. Each participant underwent a session lasting approximately 30 minutes, with breaks between tasks to avoid fatigue. Baseline recordings were taken before task onset to capture resting-state EEG activity.

3. EEG Features:

The dataset includes 64 EEG channels capturing brain activity during the tasks. Each channel's data is recorded as power spectral density (PSD), a key measure of the brain's oscillatory activity across different frequency bands. This includes both low-frequency and high-frequency brain waves that are indicative of different cognitive processes.

In addition to the PSD, Event-Related Potentials (ERP) are also included for specific tasks. ERPs reflect the brain's response to stimuli during cognitive tasks, providing crucial insight into task-related mental states.
Coherence metrics between different EEG channels can also be derived to measure the synchrony of brain regions, which is important for understanding how different brain areas work together during cognitive tasks.

4. Data Structure:

- The dataset consists of multiple columns:
- Participant_ID: Unique identifier for each participant.
- Task: The cognitive task being performed (e.g., memory recall, arithmetic, etc.).
- Channel_1_PSD to Channel_64_PSD: Power Spectral Density values for each of the 64 EEG channels.
- ERP_Memory_Recall, ERP_Arithmetic, ERP_Visual_Pattern: Event-Related Potentials for the specific tasks.
- Time_Stamp: The timestamp of the EEG recording, which allows for time-series analysis.
- Target_Label: The label indicating the cognitive state for classification (e.g., active, resting, focused).

---

# EEG data / Distance learning

- Hardware used: The EEG device used in the experiment is the Emotiv Epoc X 14 channel headset

- Experiment: 
    - During the Covid-19 lockdown, we invited several students with varying levels of education (High school, Middle school, Undergraduate) to watch an online lecture and we recorded their EEG data and brain waves during the lecture. 
    - We began by asking them several questions to understand their knowledge base and picked several videos that they would be able to understand and several videos that they wouldn't be able to understand. We then recorded their EEG data, Brain waves, and added a binary variable that indicated whether the student understood the lecture or not. (1 = Understood the lecture | 0 = Did not understand the lecture). 
    - We compiled all of our recordings and appended them to a single dataset (EEG data.csv). We also recorded various details relating to the students and videos used, they can be found in Subject details.csv and Video details.csv
    - We collected EEG data and various brain waves from 8 students as they were engaged in an online lecture during the Covid-19 lockdown. This experiment was conducted in the U.A.E. when the the distance learning policies were put in place to mitigate the spread of the Coronavirus.

- Methodology of experiment
    - We began our experiment by asking our participants various questions to gauge his/her intellectual and mental capacity. We asked them what they were currently studying in their classes and which topics they were confident in learning, and which subjects they found difficult to understand and remain engaged with. 
    - We did this to decide which videos would confuse our participant and which subjects would be simple to understand. We then proceeded to soak the sensors of the EEG device with saline solution to ensure high contact quality between the scalp of the user and the sensors before starting the recording and online lecture. 
    - Upon ending the recording, we asked our participant if they understood what was being taught by the lecturer and recorded their answer, we also tested some of our subjects by using the test questions provided on Khan Academy and seeing whether they answered correctly or incorrectly, to ensure that our participant truly understood the topic that was being taught during the lecture.

- Column content in EEG_data.csv
    - The first column (A) contains a variable that indicates the video used during the experiment. The videos can be found in Video_details.csv.
    - The second column (B) contains a variable that indicates who watched the video. More details pertaining to the student can be found in Subject_details.csv.
    - Columns 3-16 (C - P) contains raw EEG data from the 14 sensors.
    - Columns 17-86 (Q - CH) contains 5 Brain waves for each sensor.
    - Column 87 (CI) contains the binary variable that indicates whether the subject understood the lecture or not.

Source: [EEG data / Distance learning - EEG data obtained from students as they are engaged in an online learning system](https://www.kaggle.com/datasets/madyanomar/eeg-data-distance-learning-environment)

---

# Raw EEG data files

This is the raw EEG data for the study. Data is in BioSemi Data Format (BDF). Files with only "II" in the file name were recorded during the reported 1-Exemplar categorization task; "RB-II" files were recorded during the reported 2-Exemplar categorization task. "Resting" files were recorded during wakeful resting state data. (2018-11-26)

Source: [Trujillo (2019) Entropy Journal Article](https://dataverse.tdl.org/dataset.xhtml?persistentId=doi:10.18738/T8/9TTLK8&version=1.1)

Metadata:

- Persistent Identifier: doi:10.18738/T8/9TTLK8
- Publication Date: 2019-01-12
- Title: Raw EEG Data Files
- Author: Trujillo, Logan(Texas State University)
- Point of Contact: Trujillo, Logan (Texas State University)
- Description: This is the raw EEG data for the study. Data is in BioSemi Data Format (BDF). Files with only "II" in the file name were recorded during the reported 1-Exemplar categorization task; "RB-II" files were recorded during the reported 2-Exemplar categorization task. "Resting" files were recorded during wakeful resting state data. (2018-11-26)
- Subject: Medicine, Health and Life Sciences; Computer and Information Science; Mathematical Sciences; Social Sciences
- Production Date: 2018-11-26
- Production Location: Texas State University
- Depositor: Trujillo, Logan
- Deposit Date: 2018-11-26
- Data Type: Empirical EEG Data