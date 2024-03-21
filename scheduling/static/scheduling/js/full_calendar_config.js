function fullCalendarInitialization(){

    /* Funcion para cancelar un appointment */
    var cancelAppointClick = function (appointment_id){
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
                            title: 'Cancelacion de Turno',
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
                            text: 'Error al tratar de cancelar el Turno.',
                            footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                        });
                        appointments_cancel_url = appointments_cancel_url.replace(appointment_id, '9999');
                    }
                });
            } else if (result.isDenied) {

            }
        });




    }

    /* Se crea el calendario */
    var calendarEl = document.getElementById('appointments_calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridDay',
        headerToolbar: {
            start: 'today prev,next', // will normally be on the left. if RTL, will be on the right
            center: 'title',
            end: 'dayGridMonth timeGridWeek timeGridDay listWeek' // will normally be on the right. if RTL, will be on the left
        },
        /* businessHours
        businessHours: {
            // days of week. an array of zero-based day of week integers (0=Sunday)
            daysOfWeek: [0, 1, 2, 3, 4, 5, 6], // Monday - Sunday
            startTime: '06:00', // a start time (06am in this example)
            endTime: '23:00', // an end time (23pm in this example)
        },
        */
        selectable: true,
        editable: false,
        /*
        selectConstraint: 'businessHours',
        */
        locale: 'es',
        dayOfWeekStart: 1,
        allDaySlot: false,
        nowIndicator: true,
        slotDuration: '00:10:00',
        slotMinTime: '06:00:00',
        slotMaxTime: '24:00:00',
        slotLabelFormat: {
            hour: 'numeric',
            minute: '2-digit',
            omitZeroMinute: false,
            meridiem: 'short',
            hour12: false,
        },
        buttonText: {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día',
            list: 'Listado Semana'
        },
        events: {
            url: appointments_list_url,
            method: 'GET',
            extraParams: {
                study_id: study_filter_id,
                equipment_id: equipment_filter_id,
                doctor_id: doctor_filter_id
            },
            failure: function () {
                /* Alerta de Error */
                Swal.fire({
                    icon: 'error',
                    title: 'Error...',
                    text: 'Ocurrió un error solicitando el listado de citas.',
                    footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                });
            },
            //color: 'blue',   // a non-ajax option
            //textColor: 'white' // a non-ajax option
        },
        /* Al seleccionar una casilla vacía */
        select: function (selectionInfo) {

            /* MODAL DE CREAR CITAS */
            var clicked_datetime = selectionInfo.start
            var now = new Date();
            var study_filter_val = $('#id_study_filter').val();
            var equipment_filter_val = $('#id_equipment_filter').val();
            var doctor_filter_val = $('#id_doctor_filter').val();

            /* Past Date validation */
            if (clicked_datetime < now) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Fecha Pasada',
                    text: 'Atención! Está eligiendo una fecha y horario pasado.',
                })
            }

            /* Get the create view for Appointments and load it into the modal content div */
            $.ajax({
                type: 'GET',
                url: appointments_create_url,
                success: function (data, textStatus, jqXHR) {
                    $('#appointmentModal').find('.modal-content').html(data);
                    $('#appointmentModal').modal('show');
                    $('#id_appointment_date_start').val(dateToDMY(selectionInfo.start));
                    $('#id_appointment_date_end').val(dateToDMY(selectionInfo.end));

                    if (study_filter_val !== ''){
                        $('#id_medical_study').val(study_filter_val);
                        $('#id_medical_study').trigger("chosen:updated");
                    }

                    if (equipment_filter_val !== ''){
                        $('#id_medical_equipment').val(equipment_filter_val);
                        $('#id_medical_equipment').trigger("chosen:updated");

                    }

                    if (doctor_filter_val !== ''){
                        $('#id_doctor').val(doctor_filter_val);
                        $('#id_doctor').trigger("chosen:updated");
                    }

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

        },
        /* Al darle click a una casilla con un evento */
        eventClick: function (calEvent, jsEvent, view){
            appointments_update_url = appointments_update_url.replace('9999', calEvent.event.id);
            /* Get the update view for Appointments and load it into the modal content div */
            $.ajax({
                type: 'GET',
                url: appointments_update_url,
                success: function (data, textStatus, jqXHR) {
                    $('#appointmentModal').find('.modal-content').html(data);
                    $('#appointmentModal').modal('show');
                    $('#btn_cancel_appointment').on('click', function (){
                        cancelAppointClick(calEvent.event.id);
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
                    appointments_update_url = appointments_update_url.replace(calEvent.event.id, '9999');
                    /* Recarga los eventos */
                    calendar.refetchEvents();
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    appointments_update_url = appointments_update_url.replace(calEvent.event.id, '9999');
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
    });
    calendar.render();
    return calendar;
}
