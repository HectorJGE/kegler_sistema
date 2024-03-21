/* Initialization */
document.addEventListener('DOMContentLoaded', function () {

    function resizeChosen() {
        $(".chosen-container").each(function() {
            $(this).attr('style', 'width: 100%');
        });
    }

    //resizeChosen();
    //jQuery(window).on('resize', resizeChosen);

    $('#sidebarToggle').trigger('click');

    /* Se inicializa el calendario */
    var calendar = fullCalendarInitialization();

    /* Se inicializan los modales */
    appointmentModalInitialization();

    /* Se inicializan todos los filtros del calendario */
    calendarFilterInitialization(calendar);

    /* Click en el botón de crear appointment */
    $( "#btn-create-appointment" ).on('click', function(){
        $.ajax({
            type: 'GET',
            url: appointments_create_url,
            success: function (data, textStatus, jqXHR) {
                $('#appointmentModal').find('.modal-content').html(data);
                $('#appointmentModal').modal('show');
                $('#save_appointment').click(function () {
                    let errors = validateAppointmentForm();
                    if (errors.length > 0 ){
                        let error_text_head = "<ul>";
                        let error_text_body = "";
                        let error_text_foot = "</ul>";
                        for (const error of errors){
                            error_text_body = error_text_body + "<li>" + error + "</li>";
                        }
                        /* Alerta de Error */
                        Swal.fire({
                            icon: 'warning',
                            title: 'Datos Inválidos',
                            html: error_text_head + error_text_body + error_text_foot,
                        });

                    } else {
                        $("#id_estimated_cost").unmask();
                        formAjaxSubmit('#appointment_form', '#appointmentModal', calendar);
                        $('#appointment_form').submit();
                    }

                });
            }
        });
    });

    /* Si viene el parametro event_datetime por GET */
    if (event_datetime === 'None'){
        console.log('event_datetime is None');
    }else{
        console.log('event_datetime is:');
        console.log(event_datetime);
        var event_datetime_date = new Date(event_datetime * 1000);
        console.log('event_datetime_date is:');
        console.log(event_datetime_date);
        calendar.gotoDate(event_datetime_date);
        calendar.changeView('timeGridDay');

        /* Funcion para cancelar un appointment */
        var cancelAppointClick = function (appointment_id) {
            Swal.fire({
                title: 'Está seguro que quiere cancelar este turno?',
                showDenyButton: true,
                showCancelButton: true,
                cancelButtonText: 'Cancel',
                confirmButtonText: `Si`,
                denyButtonText: `No`,
            }).then((result) => {
                /* Read more about isConfirmed, isDenied below */
                if (result.isConfirmed) {
                    /* Cancelar turno */
                    $.ajax({
                        type: 'GET',
                        url: appointments_cancel_url.replace('9999', appointment_id ),
                        beforeSend: function(){
                        },
                        success: function (data, textStatus, jqXHR) {
                            /* Alerta */
                            Swal.fire({
                                icon: 'success',
                                title: 'Cancelación de TurnoTurno',
                                text: 'Turno CANCELADO!',
                            });
                            appointments_cancel_url = appointments_cancel_url.replace(appointment_id, '9999');
                            $('#appointmentModal').modal('toggle');
                            /* Recarga los eventos */
                            calendar.refetchEvents();
                        },
                        error: function (xhr, ajaxOptions, thrownError) {
                            /* Alerta de Error */
                            Swal.fire({
                                icon: 'error',
                                title: 'Error...',
                                text: 'Error al tratar de cancelar el turno.',
                                footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                            });
                            appointments_cancel_url = appointments_cancel_url.replace(appointment_id, '9999');
                        }
                    });
                } else if (result.isDenied) {

                }
            });
        }

        /* vuelve a crear el datetime filter con la fecha del parametro get */
        $('#id_date_filter').datetimepicker('destroy');
        $('#id_date_filter').datetimepicker({
            i18n: {
                es: {
                    months: [
                        'Enero', 'Febrero', 'Marzo', 'Abril',
                        'Mayo', 'Junio', 'Julio', 'Agosto',
                        'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
                    ],
                    dayOfWeek: [
                        "Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa",
                    ]
                }
            },
            datepicker: true,
            timepicker: false,
            lang: 'es',
            locale: 'es',
            format: 'd/m/Y',
            inline: true,
            defaultDate : event_datetime_date,
            onSelectDate:function(ct,$i){
                var d = new Date(ct);
                calendar.gotoDate(d);
            }
        });

        /* Llama al modal del Turno */
        appointments_update_url = appointments_update_url.replace('9999', event_id);
        /* Get the update view for Appointments and load it into the modal content div */
        $.ajax({
            type: 'GET',
            url: appointments_update_url,
            success: function (data, textStatus, jqXHR) {
                $('#appointmentModal').find('.modal-content').html(data);
                $('#appointmentModal').modal('show');
                $('#btn_cancel_appointment').on('click', function (){
                    cancelAppointClick(event_id);
                });

                $('#save_appointment').click(function () {
                    let errors = validateAppointmentForm();
                    if (errors.length > 0 ){
                        let error_text_head = "<ul>";
                        let error_text_body = "";
                        let error_text_foot = "</ul>";
                        for (const error of errors){
                            error_text_body = error_text_body + "<li>" + error + "</li>";
                        }
                        /* Alerta de Error */
                        Swal.fire({
                            icon: 'warning',
                            title: 'Datos Inválidos',
                            html: error_text_head + error_text_body + error_text_foot,
                        });

                    } else {
                        $("#id_estimated_cost").unmask();
                        formAjaxSubmit('#appointment_form', '#appointmentModal', calendar);
                        $('#appointment_form').submit();
                    }
                });
                appointments_update_url = appointments_update_url.replace(event_id, '9999');
                /* Recarga los eventos */
                calendar.refetchEvents();
            },
            error: function (xhr, ajaxOptions, thrownError) {
                appointments_update_url = appointments_update_url.replace(event_id, '9999');
                /* Alerta de Error */
                Swal.fire({
                    icon: 'error',
                    title: 'Error...',
                    text: 'Error al tratar de editar este turno.',
                    footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                });
            }
        });

    }

}); /* Fin de document loaded */