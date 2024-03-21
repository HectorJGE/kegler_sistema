function initializeFormsets() {

    function setDropifyInputs() {
        $('.dropify').dropify(
            {
                messages: {
                    'default': 'Haga click o arrastre un archivo',
                    'replace': 'Haga click o arrastre un archivo para reemplazarlo',
                    'remove': 'Eliminar',
                    'error': 'Ocurrió un error.'
                },
                error: {
                    'fileSize': 'El tamaño del archivo es muy grande ({{ value }} max).',
                    'minWidth': 'El ancho de la imagen es muy pequeña ({{ value }}}px min).',
                    'maxWidth': 'El ancho de la imagen es muy grande ({{ value }}}px max).',
                    'minHeight': 'El alto de la imagen es muy pequeño  ({{ value }}}px min).',
                    'maxHeight': 'El alto de la imagen es muy grande  ({{ value }}px max).',
                    'imageFormat': 'Formato de imagen no premitido ({{ value }} solamente).'
                }
            }
        );
    }

    /* Setea data de dropify a archivos existentes */
    function setDropifyFileData(){
        /* File */
        $('.dropify').each( function(index, elem) {
                $(this).data('default-file', documents_files[index]);
        });
    }

    function destroyChosenFormsetFields(){
        $('#id_appointment_documents-0-document_type').chosen('destroy');
        $('#id_appointment_documents-1-document_type').chosen('destroy');
        $('#id_appointment_documents-2-document_type').chosen('destroy');
        $('#id_appointment_documents-3-document_type').chosen('destroy');
    }

    setDropifyFileData();
    setDropifyInputs();
    destroyChosenFormsetFields();




    $('#id-table-documents tbody tr').formset({
        'addText': '<i class="fa fa-plus"></i>',
        'deleteText': '<i class="fa fa-trash tiny"></i>',
        'addCssClass': 'btn btn-default',
        'deleteCssClass': 'btn delete-formset-btn',
        'prefix': documents_formset_prefix,
        added: function (elem) {
            $('select').chosen();
            //setDropifyInputs();
            //console.log(elem);
        },
        removed: function () {
        }
    });
}