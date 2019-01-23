 $(document).ready(function(){
	$('form').submit(function() {
		var selected_docs= $('input[name="document_select"]:checked')
		var doc_ids =''
		selected_docs.each(function(){
			doc_ids += $(this).val()+",";
		});
		//alert(doc_ids)
		$('input[name="document_id_list"]').val(doc_ids);
		return true;
	});

});
