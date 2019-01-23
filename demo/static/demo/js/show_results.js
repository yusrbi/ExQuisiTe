var spans =  $("span.mention-answer")
spans.each(function(){
        var span = $(this)
        span.click(function(){
                var name = $(this).attr("name");
                if (name === null){
                        return;
                }
                var ids = name.split('.');
                if (ids.length < 2){
                        return;
                }
                var table = ids[0];
                var cells = ids[1];
                highlight_cells(table, cells);
        });
});

$('.popover-dismiss').popover({
  trigger: 'focus'
})

$('a.btn-popover').on('click', function(e) { 
        e.preventDefault();       
        var table_cells = $(this).attr("table-cells").split('.');
        if (table_cells.length > 1){
                var table = table_cells[0];
                var cells = table_cells[1];
                var aggr = "Single Value";
                if (table_cells.length > 2){
                        aggr = table_cells[2];
                } 
                // highlight_cells(table, cells);
        }
        
        return true;
});


$(function() {
        $("[data-toggle=popover]").popover({
                container: 'body',
                html: true,
                content: function() {
                        var content = $(this).attr("data-popover-content");
                        
                        var table_cells = $(this).attr("table-cells").split('.');
                        if (table_cells.length > 1){
                            var table = table_cells[0];
                            var cells = table_cells[1];
                            var aggr = "Single Value";
                            if (table_cells.length > 2){
                                aggr = table_cells[2];
                            } 
                            highlight_cells(table, cells);
                        }
                        var table_elem = $(content).children(".popover-body").eq(0);
                        return table_elem.html();
                },
                title: function(){
                        var conf = $(this).attr("confidence")
                        var table_cells = $(this).attr("table-cells").split('.');
                        if (table_cells.length > 2){
                                aggr = table_cells[2];
                        }else{
                                aggr = 'Single Cell'
                        }

                        return "Highlighted Cells are related with conf: " + conf + "; aggr-func: "+ aggr ;
                }
        });
});


function highlight_cells(table, cells){
        var table_cells = $('[id="tbl_'+table+'"] td');
        if (table_cells.length == 0){
            table_cells = $('[id="tbl_'+table+'"] tbody td');
        }
        if (table_cells.length == 0 ){
            return;
        }
        var id = 1;
        var cells_lst = cells.split(',');
        table_cells.each(function(){
                $(this).attr('id',"c_"+table+"."+id);
                if (cells_lst.indexOf(id.toString()) >=0){
                        $(this).addClass('highlight');
                }else{
                        $(this).removeClass('highlight');
                }
                id++;

        });
        var table_headers = $('[id="tbl_'+table+'"] th');
        id =-1;
        table_headers.each(function(){
                $(this).attr('id',"c_"+table+"."+id);
                if (cells_lst.indexOf(id.toString()) >=0){
                        $(this).addClass('highlight');
                }else{
                        $(this).removeClass('highlight');
                }
                id--;
        });

}

