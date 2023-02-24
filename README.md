[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green)](https://github.com/stanford-oval/dialogues/blob/master/LICENSE)
<a href="https://app.travis-ci.com/github/stanford-oval/dialogues"><img src="https://travis-ci.com/stanford-oval/dialogues.svg?branch=main" alt="Build Status"></a>
<a href="https://pypi.org/project/dialogues/"><img src="https://img.shields.io/pypi/dm/dialogues" alt="PyPI Downloads"></a>

# Dialogues
This codebase provides a unified interface to dialogue datasets.

It also hosts the implementation for the following paper which is published in EACL 2023.\
[_Zero and Few-Shot Localization of Task-Oriented Dialogue Agents with a Distilled Representation_](https://arxiv.org/abs/2302.09424) <br/> Mehrad Moradshahi, Sina J. Semnani, Monica S. Lam <br/>


## Abstract

Task-oriented Dialogue (ToD) agents are mostly limited to a few widely-spoken languages, mainly due to the high cost of acquiring training data for each language.
We propose automatic methods that use ToD training data in a source language to build a high-quality functioning dialogue agent in another target language that has no training data (i.e. zero-shot) or a small training set (i.e. few-shot).
Unlike most prior work in cross-lingual ToD that only focuses on Dialogue State Tracking (DST), we build an end-to-end agent.

We show that our approach closes the accuracy gap between few-shot and existing full-shot methods for ToD agents.
We achieve this by (1) improving the dialogue data representation, (2) improving entity-aware machine translation, and (3) automatic filtering of noisy translations.

We evaluate our approach on the recent bilingual dialogue dataset BiToD. In Chinese to English transfer, in the few-shot setting, we improve the state-of-the-art by 15.2\% and 14.0\%, coming within 5\% of full-shot training.


## Quickstart

### Setup
1. Clone current repository into your desired folder:
```bash
git clone https://github.com/stanford-oval/dialogues.git
```

2. Install the required libraries:
```bash
# install genienlp (used for translation, training, and inference)
pip3 uninstall -y genienlp
pip3 install git+https://github.com/stanford-oval/genienlp.git@wip/e2e-dialogues

# install dialogues and dependent packages
cd dialogues
pip3 install -e .
```

### Translation
Make sure you run the following commands from dialogues library root directory.
1. Process and prepare the dataset for training/ translation (Chinese and English are chosen as the source and target language respectively in this guide).
```bash
python3 dialogues/bitod/src/preprocess.py --max_history 2 --last_two_agent_turns --gen_full_state --only_user_rg --sampling balanced --fewshot_percent 0 --setting zh --version 1 --splits train valid
```

Make sure you run the following commands within `makefiles` directory.
2. Switch to makefiles directory, and prepare the dataset for translation:
```bash
cd makefiles
make -B all_names="train valid" experiment=bitod source=zh_v1 src_lang=zh tgt_lang=en process_data
```

3. Translate the dataset:
```bash
make -B all_names="train valid" experiment=bitod source=zh_v1 src_lang=zh tgt_lang=en nmt_model=marian translate_data
```

4. Construct the final translated dataset:
```bash
make -B all_names="train valid" experiment=bitod source=zh_v1 src_lang=zh tgt_lang=en skip_translation=true  postprocess_data
```

The final dataset will be in `bitod/zh_v1/marian/en/final` directory.


### Training
1. First, copy the dataset into `data/` (run within root dir):
```bash
mkdir -p data/
cp -r makefiles/bitod/zh_v1/marian/en/final/*.json data/
```

2. Train a new model:
```bash
genienlp train \
      --data data
      --save models/mbart/ \
      --train_tasks bitod \
      --train_iterations ${train_iterations} \
      --model TransformerSeq2Seq \
      --pretrained_model facebook/mbart-large-50 \
      --train_languages ${data_language} \
      --eval_languages ${data_language}  \
      --eval_set_name valid \
      --preserve_case \
      --exist_ok
```
For a list of training options run `genienlp train -h`.

### Evaluation
1. Evaluate your trained model (using gold input as context):
```bash
genienlp predict \
      --data data \
      --path models/mbart/ \
      --tasks bitod \
      --eval_dir models/mbart/pred/ \
      --evaluate valid \
      --pred_set_name valid \
      --overwrite
```
For a list of prediction options run `genienlp predict -h`.

2. To evaluate using model predictions as input (end-to-end setting):
```bash
genienlp predict \
      --data data \
      --path models/mbart/ \
      --tasks bitod \
      --eval_dir models/mbart/pred_e2e/ \
      --evaluate valid \
      --pred_set_name valid \
      --overwrite \
      --e2e_dialogue_evaluation
```

3. Compute evaluation metrics:
```bash
python3 makefiles/scripts/compute_e2e.py \
          --reference_file_path dialogues/bitod/data/en_valid.json \
          --prediction_file_path models/mbart/pred_e2e/valid/e2e_dialogue_preds.json \
          --experiment bitod \
          --setting en
```
The results will be printed on the terminal in a dictionary format.



## Pretrained models and datasets

You can download our datasets and pretrained models from [link](https://drive.google.com/drive/folders/1tbJPbp9D1-YvrwA2lyYrDwA6kOBumLWs?usp=sharing).
Please refer to our [paper](https://arxiv.org/pdf/2302.09424.pdf) for more details on the dataset and experiments.


## Citation
If you use our data or the software in this repository, please cite:

```
@inproceedings{moradshahi2023zero,
    title = "Zero and Few-Shot Localization of Task-Oriented Dialogue Agents with a Distilled Representation",
    author = "Moradshahi, Mehrad and Semnani, Sina J and Lam, Monica S",
    booktitle = "Proceedings of the 2023 Conference of the European Chapter of the Association for Computational Linguistics (EACL)",
    publisher = "Association for Computational Linguistics",
}
```
