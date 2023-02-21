eval_lang = en
eval_set = test

prediction_file_dir =

compute_e2e_metrics:
	python3 ./scripts/compute_e2e.py --eval_task end2end \
		--reference_file_path genie-workdirs/zeroshot/BiToD/data/$(eval_lang)_$(eval_set).json \
		--prediction_file_path $(prediction_file_dir)/e2e_dialogue_preds.json

compute_genienlp_metrics:
	$(genienlp) evaluate-file --tasks bitod --silent --pred_file $(prediction_file_dir)/bitod.tsv --e2e_dialogue_valid_submetrics em em em casedbleu

compute_auto_annotate_metrics:
	rm -rf tmp/
	mkdir -p tmp/

	# id, pred, gold, input
	for f in $(all_names) ; do \
		paste <(cut -f1,3 $(experiment)/$(source)_annot/$(nmt_model)/$(src_lang)/auto-annotated/$$f.tsv) <(cut -f3 $(experiment)/$(source)/input/$$f.tsv) <(cut -f2 $(experiment)/$(source)/input/$$f.tsv) > tmp/$$f.tsv ; \
		$(genienlp) evaluate-file --tasks bitod --silent --pred_file tmp/$$f.tsv --e2e_dialogue_valid_submetrics em em em casedbleu ; \
	done
