[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green)](https://github.com/stanford-oval/dialogues/blob/master/LICENSE)

# Dialogues
This codebase provides a unified interface to dialogue datasets.\
It also contains the code implementation for:\
[_Zero and Few-Shot Localization of Task-Oriented Dialogue Agents with a Distilled Representation_](https://arxiv.org/abs/2302.09424) <br/> Mehrad Moradshahi, Sina J. Semnani, Monica S. Lam <br/>


### Abstract

Task-oriented Dialogue (ToD) agents are mostly limited to a few widely-spoken languages, mainly due to the high cost of acquiring training data for each language.
We propose automatic methods that use ToD training data in a source language to build a high-quality functioning dialogue agent in another target language that has no training data (i.e. zero-shot) or a small training set (i.e. few-shot).
Unlike most prior work in cross-lingual ToD that only focuses on Dialogue State Tracking (DST), we build an end-to-end agent.

We show that our approach closes the accuracy gap between few-shot and existing full-shot methods for ToD agents.
We achieve this by (1) improving the dialogue data representation, (2) improving entity-aware machine translation, and (3) automatic filtering of noisy translations.

We evaluate our approach on the recent bilingual dialogue dataset BiToD. In Chinese to English transfer, in the few-shot setting, we improve the state-of-the-art by 15.2\% and 14.0\%, coming within 5\% of full-shot training.


## Quickstart


1. Clone current repository into your desired folder:
```bash
cd ${SRC_DIR}
git clone https://github.com/stanford-oval/dialogues.git
```

2. Install the required packages:
```bash
pip3 install -e .
```

\
Make sure you run the following commands from directory root (i.e. ${SRC_DIR}).\
3. Process and prepare the dataset for training/ translation (Chinese and English are chosen as the source and target language respectively in this guide).
```bash
python3 dialogues/bitod/src/preprocess.py --max_history 2 --last_two_agent_turns --gen_full_state --only_user_rg --sampling balanced --fewshot_percent 0 --setting zh --version 1 --splits valid
```

Make sure you run the following commands within makefiles directory.\
4. Switch to makefiles directory, and prepare the dataset for translation:
```bash
cd makefiles
make -B all_names=valid experiment=bitod source=zh_v1 src_lang=zh tgt_lang=en process_data
```

4. Translate the dataset:
```bash
 make -B all_names=valid experiment=bitod source=zh_v1 src_lang=zh tgt_lang=en translate_data
```

4. Construct the final translated dataset:
```bash
 make -B all_names=valid experiment=bitod source=zh_v1 src_lang=zh tgt_lang=en skip_translation=true  postprocess_data
```

The final dataset will be in `bitod/zh_v1/marian/en/final` directory.


## Pretrained models and datasets

Stay tuned!
Please refer to our [paper](https://arxiv.org/pdf/2302.09424.pdf) for more details on the dataset and experiments.


## Citation
If you use the software in this repository, please cite:

```
@misc{moradshahi2023zero,
      title={Zero and Few-Shot Localization of Task-Oriented Dialogue Agents with a Distilled Representation},
      author={Mehrad Moradshahi and Sina J. Semnani and Monica S. Lam},
      year={2023},
      eprint={2302.09424},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
