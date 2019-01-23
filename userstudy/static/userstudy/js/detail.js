$(document).ready(function(){
     var cells = $('td,th');
    $('form input[type="submit"]').click(function() {
	//alert("clicked")
	$('input[type="submit"]', $(this).parents("form")).removeAttr("clicked");
	$(this).attr("clicked","true");
	});
    $('form').submit(function() {
        var related_cells = '';
	var count=0;
        cells.each(function(){
                if($(this).hasClass('highlight')){
                        related_cells += $(this).attr('id') +',';
			count++;
                }
        });
	//alert(related_cells);
	
	var selected_value= $('input[name="relation"]:checked').val()
	var submit_value = $('input[name="submit_btn"][clicked="true"]').val()
	//alert(submit_value)
	if (submit_value == 'Not a Mention'){
		selected_value = 'Not Mention'
	}
	else if (submit_value =='Not Related'){
		selected_value = 'Not Related'
	}

	if(selected_value === 'other' && $('input[name="other_aggregate"]').val() === ''){
		alert("Please fill in the name of the other relation.")
		return false
	}
        if(related_cells ==="" && (selected_value !== 'Not Related' &&  selected_value !== 'Not Mention') ){
	      // alert($('input[name="relation"]:checked').val())
	       alert("Please select the related cells or select 'Not Related' or 'Not a Mention'!")
               return false;
        }else  if(related_cells !=="" && (selected_value  === 'Not Related' || selected_value === 'Not Mention')){
              // alert($('input[name="relation"]:checked').val())
               alert("Please select the correct relation!")
               return false;
        }else{
		if(count === 1 && (selected_value !== 'percentage' && selected_value !== 'header' &&  selected_value !== 'same' &&  selected_value !== 'other')){
			alert("Please select multiple cells for the selected relation!")
			return false;
		} else if(count !== 1 && selected_value === 'same'){
                          alert("Please Select a single cell for the selected relation!")
                          return false;
                  }
	}
        $('input[name="related_cells"]').val(related_cells);
       // alert($('input[name="related_cells"]').val());
	return true;
     });

});


$(function() {
    
    /* Get all rows from your 'table' but not the first one 
     * that includes headers. */
    //var rows = $('tr').not(':first');
    var cells = $('td')
    var headers = $('th');
    var id = 1 

    cells.each(function(){
	$(this).attr('id', id);
	id++;
    });

    cells.on('click', function(e){
	//alert($(this).attr('id'))	
    	var cell =$(this);
      if((e.ctrlKey ||e.metaKey) || e.shiftKey){
      	if(cell.hasClass('highlight')){
          cell.removeClass('highlight')
        } else{
          cell.addClass('highlight');
        }
      }else{         
        if(!cell.hasClass('highlight')){
        	cells.removeClass('highlight')
		headers.removeClass('highlight')
          	cell.addClass('highlight');
        }else{
        	cells.removeClass('highlight')
		headers.removeClass('highlight')
        }
      
      }
     
    });
    var headers = $('th');
    var id =-1;

    headers.each(function(){
	$(this).attr('id',id);
	id--;
    });
    headers.on('click', function(e){
	var header = $(this);
	if((e.ctrlKey ||e.metaKey) || e.shiftKey){
        if(header.hasClass('highlight')){
          header.removeClass('highlight')
        } else{
          header.addClass('highlight');
        }   
      }else{     
        if(!header.hasClass('highlight')){
                headers.removeClass('highlight')
		cells.removeClass('highlight')
                header.addClass('highlight');
        }else{
                headers.removeClass('highlight')
		cells.removeClass('highlight')
        }   
     
      }   	
   });
    /* Create 'click' event handler for rows 
    rows.on('click', function(e) {
        
        // Get current row 
        var row = $(this);
        
        /* Check if 'Ctrl', 'cmd' or 'Shift' keyboard key was pressed
         * 'Ctrl' => is represented by 'e.ctrlKey' or 'e.metaKey'
         * 'Shift' => is represented by 'e.shiftKey' 
        if ((e.ctrlKey || e.metaKey) || e.shiftKey) {
            // If pressed highlight the other row that was clicked 
            row.addClass('highlight');
        } else {
            // Otherwise just highlight one row and clean others 
            rows.removeClass('highlight');
            row.addClass('highlight');
        }
        
    });*/
    
    /* This 'event' is used just to avoid that the table text 
     * gets selected (just for styling). 
     * For example, when pressing 'Shift' keyboard key and clicking 
     * (without this 'event') the text of the 'table' will be selected.
     * You can remove it if you want, I just tested this in 
     * Chrome v30.0.1599.69 */
    $(document).bind('selectstart dragstart', function(e) { 
        e.preventDefault(); return false; 
    });
    
});




