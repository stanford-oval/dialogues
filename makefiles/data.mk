####################################################################################################################
##### Prepare dataset for translation                ###############################################################
####################################################################################################################

src_lang=
tgt_lang=

$(experiment)/$(source)/input: ../dialogues/$(experiment)/data/preprocessed/$(source)/
	mkdir -p $@

	for f in $(all_names) ; do \
		python3 ./scripts/convert_to_tsv.py --input_file $</$$f.json --output_file $</$$f.tsv ; \
	done

	for f in $(all_names) ; do \
		if $(clean_input_quotes) ; then \
			python3 ./scripts/text_edit.py --experiment $(experiment) --no_lower_case --remove_qpis --e2e --experiment $(experiment) --num_columns $(num_columns) --experiment $(experiment) --input_file $</$$f.tsv --output_file $@/$$f.tsv ; \
		else \
			cp $</$$f.tsv $@/$$f.tsv ; \
		fi ; \
	done

$(experiment)/$(source)/input-qpis: $(experiment)/$(source)/input
	mkdir -p $@

	# qpis input data
	for f in $(all_names) ; do python3 ./scripts/dialogue_edit.py --mode qpis --experiment $(experiment) --src_lang $(src_lang) --tgt_lang $(tgt_lang) --input_path $</$$f.tsv --output_path $@/$$f.tsv ; done

$(experiment)/$(source)/input-nmt: $(experiment)/$(source)/input-qpis
	mkdir -p $@
	mkdir -p $@-user
	mkdir -p $@-agent
	# prepare unquoted data for marian translation
	for f in $(all_names) ; do \
		python3 ./scripts/text_edit.py --experiment $(experiment) --no_lower_case --prepare_for_marian --e2e --replace_ids  --num_columns $(num_columns) --input_file $</$$f.tsv --output_file $@/$$f.tmp.tsv ; \
		cut -f1,2 $@/$$f.tmp.tsv | awk 'NR % $(subtask_per_turn) == 0' >  $@-user/$$f.tsv ; \
		cut -f1,3 $@/$$f.tmp.tsv | awk 'NR % $(subtask_per_turn) == 0' >  $@-agent/$$f.tsv ; \
	done
	rm -rf $@

$(experiment)/$(source)/input-sts: $(experiment)/$(source)/input-nmt
	mkdir -p $@-user
	mkdir -p $@-agent
	# prepare unquoted data for marian translation
	for f in $(all_names) ; do \
		sed -E 's/" ([^"]*) "/\1/g' $<-user/$$f.tsv > $@-user/$$f.tsv ; \
		sed -E 's/" ([^"]*) "/\1/g' $<-agent/$$f.tsv > $@-agent/$$f.tsv ; \
	done
	rm -rf $@

$(experiment)/process_data: $(experiment)/$(source)/input-nmt  $(experiment)/$(source)/input-sts
	# done!
	echo $@

process_data:
	make experiment=$(experiment) $(experiment)/process_data


# make -B all_names=valid experiment=risawoz_zh source=v10 src_lang=zh tgt_lang=en process_data
