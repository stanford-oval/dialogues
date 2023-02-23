####################################################################################################################
##### translate dialogs using open-source NMT models ###############################################################
####################################################################################################################

model_name_or_path=Helsinki-NLP/opus-mt-$(src_lang)-$(tgt_lang)
#model_name_or_path=facebook/mbart-large-50-many-to-many-mmt
# model_name_or_path=facebook/m2m100_418M
# model_name_or_path=facebook/nllb-200-distilled-600M

nmt_model=nmt

src_lang=
tgt_lang=

is_user_acts = false

skip_translation = false
skip_agent = false
skip_ent_translation = false

do_alignment = true
do_align_help = true
model_parallel_hf = false

translate_extra_args = --temperature 0.2 --val_batch_size 800
ent_translate_extra_args = --top_p 0.9 --temperature 0 0.3 0.5 0.7 1.0 --val_batch_size 800
s3_bucket = https://nfs009a5d03c43b4e7e8ec2.blob.core.windows.net/pvc-a8853620-9ac7-4885-a30e-0ec357f17bb6


do_translate:
	rm -rf tmp/
	mkdir -p tmp/almond/
	ln -f $(input_folder)/*.tsv tmp/almond/
	if ! $(skip_translation) ; then \
		if [ ! -f $(GENIENLP_EMBEDDINGS)/$(model_name_or_path)/best.pth ] ; then \
			mkdir -p $(GENIENLP_EMBEDDINGS)/$(model_name_or_path)/ ; \
			azcopy sync $(s3_bucket)/mehrad/extras/models/hf/$(model_name_or_path)/ $(GENIENLP_EMBEDDINGS)/$(model_name_or_path)/ ; \
		fi ; \
		if [ ! -f $(GENIENLP_EMBEDDINGS)/$(model_name_or_path)/best.pth ] ; then \
			$(genienlp) train --train_iterations 0 --pretrained_model $(model_name_or_path) $(train_default_args) ; \
			azcopy sync $(GENIENLP_EMBEDDINGS)/$(model_name_or_path)/ $(s3_bucket)/mehrad/extras/models/hf/$(model_name_or_path)/ --exclude-pattern 'events*' ; \
		fi ; \
		if ! $(skip_ent_translation) ; then \
			mkdir -p $(output_folder)_entities ; \
			for f in $(all_names) ; do \
				$(genienlp) predict \
				 --pred_set_name $$f \
				 --data tmp/ \
				 --eval_dir $(output_folder)_entities/ \
				 --translate_only_entities \
				 $(translate_shared_args) \
				 $(ent_translate_extra_args) || exit 1 ; \
			done ; \
		fi ; \
		for f in $(all_names) ; do \
			$(genienlp) predict \
			 --pred_set_name $$f \
			 --data tmp/ \
			 --translate_example_split \
			 --eval_dir $(output_folder)/ \
			 `if $(do_alignment) ; then echo "--do_alignment --translate_return_raw_outputs" ; fi` \
			 `if $(do_align_help) ; then echo "--align_helper_file $(output_folder)_entities/valid/almond_translate.tsv" ; fi` \
			 `if $(model_parallel_hf) ; then echo "--model_parallel_hf" ; fi` \
			 $(translate_shared_args) \
			 $(translate_extra_args) || exit 1 ; \
			mv $(output_folder)/valid/almond_translate.tsv $(output_folder)/$$f.tsv ; \
			if [ -e "$(output_folder)/valid/almond_translate.raw.tsv" ] ; then mv $(output_folder)/valid/almond_translate.raw.tsv $(output_folder)/$$f.raw.tsv ; fi ; \
			rm -rf $(output_folder)/valid ; \
		done ; \
	fi
	rm -rf tmp/


$(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/translated-qpis:
	mkdir -p $@-user
	mkdir -p $@-agent

	if $(is_user_acts) ; then \
		for f in $(all_names) ; do \
			data_size=`cat ./$(experiment)/$(source)/input-nmt-user/$$f.tsv | wc -l` ; \
			paste <(cat ./$(experiment)/$(source)/input-nmt-user/$$f.tsv) <(awk "{for(i=0;i<$$data_size;i++)print}" <(echo ".")) > $@-user/$$f.tsv ; \
		done ; \
	else \
		make input_folder="./$(experiment)/$(source)/input-nmt-user/" output_folder="$@-user" do_translate ; \
	fi

	if $(skip_agent) ; then \
		for f in $(all_names) ; do \
			cp $@-user/$$f.tsv $@-agent/$$f.tsv ; \
		done ; \
	else \
		make input_folder="./$(experiment)/$(source)/input-nmt-agent/" output_folder="$@-agent" do_translate ; \
	fi ; \


translate_data: $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/translated-qpis
	# done!
	echo $@

# make -B all_names=valid experiment=risawoz_zh source=v10 src_lang=zh tgt_lang=en model_name_or_path=facebook/mbart-large-50-many-to-many-mmt nmt_model=mbart_m2m translate_extra_args="--val_batch_size 1500 --temperature 0.2"  translate_data


####################################################################################################################
##### Postprocess Translated dataset                 ###############################################################
####################################################################################################################

$(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/refined-qpis: $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/translated-qpis
	mkdir -p $@
	# insert programs (and context)
	for f in $(all_names) ; do \
		python3 scripts/create_translated.py --translated_file_user $<-user/$$f.tsv --translated_file_agent $<-agent/$$f.tsv --ref_file ./$(experiment)/$(source)/input/$$f.tsv --output_file $@/$$f.tmp.tsv ; \
	done

	# refine sentence
	for f in $(all_names) ; do \
		python3 $(ml_scripts)/text_edit.py --no_lower_case --e2e --refine_sentence --post_process_translation --experiment $(experiment) --param_language $(src_lang) --num_columns $(num_columns) --input_file $@/$$f.tmp.tsv --output_file $@/$$f.tsv ; \
	done

	rm -rf $@/*.tmp*


$(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/cleaned-qpis: $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/refined-qpis
	mkdir -p $@
	# fix punctuation and clean dataset
	for f in $(all_names) ; do \
		if $(is_user_acts) ; then \
			cp $</$$f.tsv $@/$$f.tsv ; \
		else \
			python3 $(ml_scripts)/text_edit.py --experiment $(experiment) --no_lower_case --e2e --insert_space_quotes --num_columns $(num_columns) --input_file $</$$f.tsv --output_file $@/$$f.tsv ; \
		fi ; \
	done


$(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/cleaned: $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/cleaned-qpis
	mkdir -p $@
	# remove quotation marks in the sentence
	for f in $(all_names) ; do \
		python3 $(ml_scripts)/text_edit.py --experiment $(experiment) --no_lower_case --e2e --remove_qpis `if $(is_user_acts) ; then echo "--is_user_acts" ; fi` --num_columns $(num_columns) --input_file $</$$f.tsv  --output_file $@/$$f.tsv ; \
	done


$(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/quoted: $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/cleaned
	mkdir -p $@
	# requote dataset (if successful, verifies parameters match in the sentence and in the program)
	for f in $(all_names) ; do \
		python3 $(ml_scripts)/dialogue_edit.py --mode requote --experiment $(experiment) --src_lang $(src_lang) --tgt_lang $(tgt_lang) --input_path $</$$f.tsv --output_path $@/$$f.tsv ; \
	done


$(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/augmented: $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/quoted
	mkdir -p $@
	# augment dataset in target language
	for f in $(all_names) ; do \
		python3 $(ml_scripts)/dialogue_edit.py --mode augment --experiment $(experiment) --aug_mode dictionary --src_lang $(src_lang) --tgt_lang $(tgt_lang) --input_path $</$$f.tsv --output_path $@/$$f.tsv  ; \
	done


$(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final: $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/augmented
	mkdir -p $@
	# remove cjk spaces
	for f in $(all_names) ; do python3 $(ml_scripts)/text_edit.py --no_lower_case --e2e --fix_spaces_cjk --experiment $(experiment) --param_language $(tgt_lang) --num_columns $(num_columns) --input_file $</$$f.tsv  --output_file $@/$$f.tsv  ; done
	for f in $(all_names) ; do python3 $(ml_scripts)/convert_to_json.py --input_file $@/$$f.tsv --output_file $@/$$f.json ; done

postprocess_data: $(experiment)/$(source)/$(nmt_model)/$(tgt_lang)/final
	# done!
	echo $@

# make -B all_names=valid experiment=risawoz_zh source=v10 src_lang=zh tgt_lang=en nmt_model=mbart_m2m skip_translation=true  postprocess_data
