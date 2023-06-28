[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green)](https://github.com/stanford-oval/dialogues/blob/master/LICENSE)
<a href="https://app.travis-ci.com/github/stanford-oval/dialogues"><img src="https://travis-ci.com/stanford-oval/dialogues.svg?branch=main" alt="Build Status"></a>
<a href="https://pypi.org/project/dialogues/"><img src="https://img.shields.io/pypi/dm/dialogues" alt="PyPI Downloads"></a>

# Dialogues
This codebase provides a unified interface to dialogue datasets.

It also hosts the implementation for the following paper which is published in ACL 2023.\
[_X-RiSAWOZ: High-Quality End-to-End Multilingual Dialogue Datasets
and Few-shot Agents_](https://arxiv.org/abs/2302.09424) <br/> Mehrad Moradshahi, Tianhao Shen, Kalika Bali, Monojit Choudhury, Gael de Chalendar, Anmol Goel, Sungkyun Kim, Prashant Kodali, Ponnurangam Kumaraguru, Nasredine Semmar, Sina Semnani, Jiwon Seo, Vivek Seshadri, Manish Shrivastava, Michael Sun, Aditya Yadavalli, Chaobin You, Deyi Xiong, Monica Lam <br/>


## Abstract

Task-oriented dialogue research has mainly focused on a few popular languages like English and Chinese, due to the high dataset creation cost for a new language. To reduce the cost,
we apply manual editing to automatically translated data. We create a new multilingual benchmark, X-RiSAWOZ, by translating the Chinese RiSAWOZ to 4 languages: English, French,
Hindi, Korean; and a code-mixed English-Hindi language. X-RiSAWOZ has more than 18,000 human-verified dialogue utterances for each language, and unlike most multilingual prior work, is an end-to-end dataset for building fully-functioning agents.

The many difficulties we encountered in creating X-RiSAWOZ led us to develop a toolset to accelerate the post-editing of a new language dataset after translation. This toolset improves machine translation with a hybrid entity alignment technique that combines neural with dictionary-based methods, along with many automated and semi-automated validation checks.

We establish strong baselines for X-RiSAWOZ by training dialogue agents in the zero- and few-shot settings where limited gold data is available in the target language. Our results suggest that our translation and post-editing methodology and toolset can be used to create new high-quality multilingual dialogue agents cost-effectively. Our dataset, code, and toolkit are released open-source.

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
pip3 install git+https://github.com/stanford-oval/genienlp.git@wip/risawoz

# install dialogues and dependent packages
cd dialogues
pip3 install -e .
```

### Translation
Make sure you run the following commands from dialogues library root directory.
1. Process and prepare the dataset for training/ translation (Chinese and English are chosen as the source and target language respectively in this guide).
```bash
python3 dialogues/risawoz/src/preprocess.py --max_history 2 --last_two_agent_turns --gen_full_state --only_user_rg --sampling balanced --fewshot_percent 0 --setting zh --version 1 --splits train valid
```

Make sure you run the following commands within `makefiles` directory.
2. Switch to makefiles directory, and prepare the dataset for translation:
```bash
cd makefiles
make -B all_names="train valid" experiment=risawoz source=zh_v1 src_lang=zh tgt_lang=en process_data
```

3. Translate the dataset:
```bash
make -B all_names="train valid" experiment=risawoz source=zh_v1 src_lang=zh tgt_lang=en nmt_model=marian translate_data
```

4. Construct the final translated dataset:
```bash
make -B all_names="train valid" experiment=risawoz source=zh_v1 src_lang=zh tgt_lang=en skip_translation=true  postprocess_data
```

The final dataset will be in `risawoz/zh_v1/marian/en/final` directory.


### Training
1. First, copy the dataset into `data/` (run within root dir):
```bash
mkdir -p data/
cp -r makefiles/risawoz/zh_v1/marian/en/final/*.json data/
```

2. Train a new model:
```bash
genienlp train \
      --data data
      --save models/mbart/ \
      --train_tasks risawoz \
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
      --tasks risawoz \
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
      --tasks risawoz \
      --eval_dir models/mbart/pred_e2e/ \
      --evaluate valid \
      --pred_set_name valid \
      --overwrite \
      --e2e_dialogue_evaluation
```

3. Compute evaluation metrics:
```bash
python3 makefiles/scripts/compute_e2e.py \
          --reference_file_path dialogues/risawoz/data/en_valid.json \
          --prediction_file_path models/mbart/pred_e2e/valid/e2e_dialogue_preds.json \
          --experiment risawoz \
          --setting en
```
The results will be printed on the terminal in a dictionary format.



## Pretrained models and datasets

[//]: # (You can download our datasets and pretrained models from [link]&#40;https://drive.google.com/drive/folders/1tbJPbp9D1-YvrwA2lyYrDwA6kOBumLWs?usp=sharing&#41;.)

[//]: # (Please refer to our [paper]&#40;https://arxiv.org/pdf/2302.09424.pdf&#41; for more details on the dataset and experiments.)


## Citation
If you use our data or the software in this repository, please cite:

```

[//]: # (@inproceedings{moradshahi2023zero,)

[//]: # (    title = "Zero and Few-Shot Localization of Task-Oriented Dialogue Agents with a Distilled Representation",)

[//]: # (    author = "Moradshahi, Mehrad and Semnani, Sina J and Lam, Monica S",)

[//]: # (    booktitle = "Proceedings of the 2023 Conference of the European Chapter of the Association for Computational Linguistics &#40;EACL&#41;",)

[//]: # (    publisher = "Association for Computational Linguistics",)

[//]: # (})


```



# Dialogues
This codebase provides a unified interface to several dialogue datasets.

# Available datasets:
- risawoz
- RiSAWOZ


# Data
Adding a new language:
- Look at `risawoz/data/original/en_{split}.json` to understand how the dataset is formatted.
- "user_utterance" and "system_utterance" contain the following: 1) utterance in natural language 2) entities and their word-spans in the utterance
- "db_results" contain the retrieved entries from database when agent makes an api call
- For a new language, the following needs to be done:
- Data Translation:
  - "user_utterance" and "system_utterance" should be translated to the target language. We let translators use their best judgment on how each entity should be translated given the context.
  - Translators need to annotate span of entities in the translated sentences which would be used to create a mapping between source entities and target entities. We have a UI tool that aids translators in doing so.
  - This results in a one-to-many mapping as each source entity may have multiple translations. For reasons mentioned later, we need to choose one of the translations as the canonical one and create a second mapping to map all possible translations to the canonical one (en2canonical.json).
- Database Translation:
  - The entity values in English database needs to be translated to the target langauge according to the alignment information. You can use the second mapping to do this.
  - Similarly, you can use this mapping to translate "db_results" in the dataset.

# Validating your work:
- Once you've created the dataset in the target language, put the content in the following file `risawoz/data/original/{language}_{split}.json`
- Add the new database files under `risawoz/database/db_{lang}/`. Follow the same formatting as English. The slot names don't need to be translated, only slot values.
- Run `python3 dialogues/risawoz/src/convert.py --setting {language} --splits {split}` to convert your data into a format suitable for preprocessing.
- You'll likely see the following in your output logs "API call likely failed for...". This could mean many things ranging from wrong alignment during translation, mismatch between entities in the translated sentence and database values, etc. To have a more accurate check, we restore the API calls from the existing search results. You should also try your best to solve the failed API calls by correcting belief states annotations and the two mappings. Our script will show some clues for you to solve these issues (e.g., the mismatches between the belief states and ground-truth search results which make an API call fail). If you get only a few of these errors, it means that the translated dataset is already of relatively high quality.
- If conversions is successful, you will see the converted file: `risawoz/data/{language}_{split}.json`. You can check the file to make sure it looks good.
- Run `python3 dialogues/risawoz/src/preprocess.py --max_history 2 --last_two_agent_turns --gen_full_state --only_user_rg --sampling balanced --setting {lang} --fewshot_percent 0 --version 1 --splits {split}` to preprocess the data for training.
- If preprocessing is successful, you will see the resulting file: `risawoz/data/preprocessed/{language}_{split}.json`.
- Run `python3 dialogues/risawoz/scripts/check_entity.py --directory dialogues/risawoz/data/preprocessed/ --version 1 --splits {split}` to sanity check the data. This script ensures that entities in the output are present in the input. This is necessary since our models are trained to copy entities from the input. This script will create a file `dialogues/risawoz/data/preprocessed/{split}_entity_check_1.tsv` including erroneous turns.
- To fix erroneous turns, you need to backtrack and sanity check every step of the data processing until you find the bug.
- If everything passes without errors, congrats! We will soon have a dialogue agent that can speak your language!
