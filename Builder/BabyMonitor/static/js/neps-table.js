/**
 * Provided by Thiago Nepomuceno from Neps Academy under MIT license
 */

function initialize_table(datatable_id, table_id, remove_search_bar){

    $('#' + datatable_id + ' .col-sm-12').get(3).remove();
    $('#' + datatable_id + ' .col-md-6:first').remove();
    $('#' + datatable_id + ' .col-md-6:first').removeClass('col-md-6').addClass('col-12');
    $('#' + datatable_id + ' .col-md-7').removeClass('col-md-7');
    $('#' + datatable_id + ' .row:last').addClass('justify-content-center');
    $('#' + datatable_id + ' .row:last').addClass('text-center');
    $('#' + datatable_id + ' .col-sm-12').removeClass('col-sm-12');

    if(remove_search_bar){
        $('#' + table_id + '_filter').remove();
    }

    $('#' + datatable_id + ' .row').addClass('p-0 m-0');

    $('#' + datatable_id + ' label').contents().unwrap();

    $('#' + datatable_id + ' .pagination a').not(':first').not(':last').addClass('page-number-link');
    //$('.col-sm-12').get(3);

    //$('label:last').text('');

    $('#' + datatable_id + ' input:last').wrap("<div id='search-table-div' class='input-group md-form form-sm form-2 pl-0'> </div>").attr("placeholder", "Search").attr("type", "text");
    $('#' + datatable_id + ' #search-table-div').append('<span class="input-group-text waves-effect secondary-color" id="basic-addon1"><a><i class="fa fa-search white-text" aria-hidden="true"></i></a></span>');
    $('#' + datatable_id + ' input:last').removeClass('form-control-sm').addClass('m-0 p-1 grey-border');
}
