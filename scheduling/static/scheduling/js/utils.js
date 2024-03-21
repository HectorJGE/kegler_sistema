/* Funcion para mostrar correctamente el string de fecha y hora, dada una fecha */
function dateToDMY(date) {
    var d = date.getDate();
    var m = date.getMonth() + 1; //Month from 0 to 11
    var y = date.getFullYear();
    var h = date.getHours();
    var min = date.getMinutes();

    return '' + (d <= 9 ? '0' + d : d) + '/' + (m <= 9 ? '0' + m : m) + '/' + y + ' ' + (h <= 9 ? '0' + h : h) + ':' + (min <= 9 ? '0' + min : min);
}

/* Funcion para abrir un url en una nueva pestaña */
function openInNewTab(url) {
    var win = window.open(url, '_blank');
    win.focus();
}

/* Función submit ajax de formulario de modal */
var formAjaxSubmit = function (form, modal, calendar) {
    $(form).submit(function (e) {
        e.preventDefault();
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (xhr, ajaxOptions, thrownError) {
                alert("Datos guardados!");
                if ($(xhr).find('.has-error').length > 0) {
                    $(modal).find('.modal-body').html(xhr);
                } else {
                    $(modal).modal('toggle');
                    /* Recarga los eventos */
                    calendar.refetchEvents();
                }
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert("Error al tratar de enviar este formulario.")
            }
        });
    });
}

function calculatePercent(num, percent){
    return (percent / 100) * num;
}