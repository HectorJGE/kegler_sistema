$(function() {
    /* Se contrae el sidebar */
    $('#sidebarToggle').trigger('click');

    /* Se inicializan los formsets */
    initializeFormsets();

    /* Se inicializan los inputs del formulario */
    initializeInputs();

    $('#div_id_payment_method').hide();

    /* Alerta */
    Swal.fire({
        icon: 'warning',
        title: 'ATENCION!!!',
        text: 'Si realiza un cambio en los campos del SEGURO DEL PACIENTE, o del ESTUDIO REALIZADO de la ficha, esta será recalculada, eliminando automáticamente ' +
            'TODOS LOS INSUMOS UTILIZADOS, y TODOS LOS PAGOS REALIZADOS a esta ficha de estudio!!! proceda bajo su propio riesgo.',
    });

});