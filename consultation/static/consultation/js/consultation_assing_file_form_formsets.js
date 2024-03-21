function initializeFormsets(){
    /* Inicializar tabla de formset de archivos */
    $('#id-table-consultation-files tbody tr').formset({
        'addText': '<i class="fa fa-plus"></i>',
        'deleteText': '<i class="fa fa-trash tiny"></i>',
        'addCssClass': 'btn btn-default',
        'deleteCssClass': 'btn delete-formset-btn',
        'prefix': consultation_files_formset_prefix,
        added: function (elem) {
            $('select').chosen();
        },
        removed: function () {
        }
    });

}