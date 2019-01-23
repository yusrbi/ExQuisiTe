function highlight_cells(cells){
	var table_cells = $('[name="target-table"] td');
	var id = 1;
	var cells_lst = cells.split(',');
	table_cells.each(function(){
		$(this).attr('id',id);
		if (cells_lst.indexOf(id.toString()) >=0){
			$(this).addClass('highlight');	
		}else{
			$(this).removeClass('highlight');
		}
		id++;

	});
	var table_headers = $('[name="target-table"] th');
	id =-1;
	table_headers.each(function(){
		$(this).attr('id',id);
		if (cells_lst.indexOf(id.toString()) >=0){
			$(this).addClass('highlight');
		}else{
			$(this).removeClass('highlight');
		}
		id--;
	});
	
}
