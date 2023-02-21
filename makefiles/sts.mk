filtering_threshold ?= 0.8
filtering_model_name ?= LaBSE

########################################
# create data to feed into sts
calculate_sts_scores:
	mkdir -p $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final-sts-agent
	for f in $(all_names) ; do \
		paste <(cut -f1,2 $(experiment)/$(source)/input-sts-agent/$$f.tsv) <(cut -f2 $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/translated-qpis-agent/$$f.raw.tsv) >  $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final-sts-agent/$$f.tsv ; \
		if [ ! -f $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final-sts-agent/$$f-with-scores.tsv ] ; then \
		 	$(genienlp) sts-calculate-scores --model_name $(filtering_model_name) --input_file $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final-sts-agent/$$f.tsv --output_file $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final-sts-agent/$$f-with-scores.tsv ; \
		fi ; \
		$(genienlp) sts-filter --filtering_metric constant --filtering_threshold $(filtering_threshold) --input_file $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final-sts-agent/$$f-with-scores.tsv --output_file $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final-sts-agent/$$f-filt.tsv ; \
	done

########################################
# remove unwanted things
filter_data: calculate_sts_scores
	mkdir -p $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final-filtered-$(filtering_threshold)-agent
	for f in $(all_names) ; do python3 ../spl/scripts/text_edit.py --no_lower_case --subtask_per_turn $(subtask_per_turn) --e2e --filter_examples --id_file $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final-sts-agent/$$f-filt.tsv --experiment $(experiment) --param_language $(tgt_lang) --num_columns $(num_columns) --input_file $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final/$$f.tsv  --output_file $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final-filtered-$(filtering_threshold)-agent/$$f.tsv  ; done
	for f in $(all_names) ; do python3 ./scripts/convert_to_json.py --input_file $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final-filtered-$(filtering_threshold)-agent/$$f.tsv --output_file $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final-filtered-$(filtering_threshold)-agent/$$f.json ; done
