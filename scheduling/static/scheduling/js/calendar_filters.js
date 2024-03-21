function calendarFilterInitialization(calendar){
    /* Se convierte todos los selects a chosen */
    $('select').chosen(
        {
            no_results_text: "No se encontraron resultados para",
        }
    );

    /* datepicker para el filtro de fecha del calendario */
    $('#id_date_filter').mask("00/00/0000");
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
        defaultDate : new Date(),
        onSelectDate:function(ct,$i){
            var d = new Date(ct);
            calendar.gotoDate(d);
        },
        scrollMonth : false,
        scrollInput : false,
    });

    /* Al elegir el filtro del estudio médico */
    $("#id_study_filter").change(function(){
        if ($("#id_study_filter").val() !== ''){
            console.log('Study filter');

            /* Vacía el calendario
            calendar.removeAllEventSources();
             */

            /* Asigna valores a los parametros de filtro
            study_filter_id = $("#id_study_filter").val();
            equipment_filter_id = '';
            doctor_filter_id = '';
             */

            /* Filtrar Turnos por el estudio
            calendar.addEventSource(
                {
                    url: appointments_list_url,
                    method: 'GET',
                    extraParams: {
                        study_id: study_filter_id,
                        equipment_id: equipment_filter_id,
                        doctor_id: doctor_filter_id
                    }
                }
            )
             */

            /* Recarga los eventos
            calendar.refetchEvents();
             */

            /* Traer los datos de ese estudio */
            var url_to_send = get_medical_study_json_url.replace('9999', $("#id_study_filter").val() );
            $.ajax({
                type: 'GET',
                url: url_to_send,
                data: { insurance_plan_id: '' },
                success: function (data, textStatus, jqXHR) {

                    /* Pregunta si el equipo es de tipo ecografía para mostrar los doctores */
                    if(data.sector_code === 'ECO'){
                        $('#div_id_equipment_filter').hide();
                        $('#div_id_doctor_filter').show()
                    }else{
                        $('#div_id_equipment_filter').show();
                        $('#div_id_doctor_filter').hide();
                    }

                },
                error: function (xhr, ajaxOptions, thrownError) {
                    /* Alerta de Error */
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        text: 'Error al tratar de obtener datos del estudio.',
                        footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                    });
                }
            });

            /* Traer equipos de ese estudio */
            $.ajax({
                type: 'GET',
                url: list_medical_equiment_by_study_url.replace('9999', $("#id_study_filter").val() ),
                beforeSend: function(){
                    $('#id_equipment_filter').empty();
                    $('#id_equipment_filter').append('<option value="" selected="">---------</option>');
                },
                success: function (data, textStatus, jqXHR) {
                    data.forEach(function(item, index, array) {
                        $('#id_equipment_filter').append('<option value="' + item.id + '">' + item.name + '</option>');
                    })
                    $('#id_equipment_filter').trigger("chosen:updated");
                    list_medical_equiment_by_study_url = list_medical_equiment_by_study_url.replace($("#id_study_filter").val(), '9999');
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    /* Alerta de Error */
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        text: 'Error al tratar de obtener la lista de equipos para el estudio.',
                        footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                    });
                    list_medical_equiment_by_study_url = list_medical_equiment_by_study_url.replace($("#id_study_filter").val(), '9999');
                }
            });



            /* Traer doctores de ese estudio */
            $.ajax({
                type: 'GET',
                url: list_doctor_by_study_url.replace('9999', $("#id_study_filter").val() ),
                beforeSend: function(){
                    $('#id_doctor_filter').empty();
                    $('#id_doctor_filter').append('<option value="" selected="">---------</option>');
                },
                success: function (data, textStatus, jqXHR) {
                    data.forEach(function(item, index, array) {
                        $('#id_doctor_filter').append('<option value="' + item.id + '">' + item.name + '</option>');
                    })
                    $('#id_doctor_filter').trigger("chosen:updated");
                    list_doctor_by_study_url = list_doctor_by_study_url.replace($("#id_study_filter").val(), '9999');
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    /* Alerta de Error */
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        text: 'Error al tratar de obtener la lista de doctores para el estudio.',
                        footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                    });
                    list_doctor_by_study_url = list_doctor_by_study_url.replace($("#id_study_filter").val(), '9999');
                }
            });



        } else {

            /* Traer todos los equipos */
            $.ajax({
                type: 'GET',
                url: list_medical_equiment_all_url,
                beforeSend: function(){
                    $('#id_equipment_filter').empty();
                    $('#id_equipment_filter').append('<option value="" selected="">---------</option>');
                },
                success: function (data, textStatus, jqXHR) {
                    data.forEach(function(item, index, array) {
                        $('#id_equipment_filter').append('<option value="' + item.id + '">' + item.name + '</option>');
                    })
                    $('#id_equipment_filter').trigger("chosen:updated");
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    /* Alerta de Error */
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        text: 'Error al tratar de obtener la lista de todos los equipos.',
                        footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                    });
                }
            });

            /* Traer todos los doctores */
            $.ajax({
                type: 'GET',
                url: list_doctor_all_url,
                beforeSend: function(){
                    $('#id_doctor_filter').empty();
                    $('#id_doctor_filter').append('<option value="" selected="">---------</option>');
                },
                success: function (data, textStatus, jqXHR) {
                    data.forEach(function(item, index, array) {
                        $('#id_doctor_filter').append('<option value="' + item.id + '">' + item.name + '</option>');
                    })
                    $('#id_doctor_filter').trigger("chosen:updated");
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    /* Alerta de Error */
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        text: 'Error al tratar de obtener la lista de todos los doctores.',
                        footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                    });
                }
            });

            $('#div_id_equipment_filter').show();
            $('#div_id_doctor_filter').show();

            /* Remueve el event Source
            calendar.removeAllEventSources();
             */

            /* Asigna valores a los parametros de filtro
            study_filter_id = '';
            equipment_filter_id = '';
            doctor_filter_id = '';

             */

            /* Agrega un nuevo event source
            calendar.addEventSource(
                {
                    url: appointments_list_url,
                    method: 'GET',
                    extraParams: {
                        study_id: study_filter_id,
                        equipment_id: equipment_filter_id,
                        doctor_id: doctor_filter_id
                    }
                }
            )

             */
            /* Recarga los eventos
            calendar.refetchEvents();

             */
        }

    });

    /* Al elegir el filtro del equipo médico */
    $("#id_equipment_filter").change(function(){
        console.log('Equipment filter');

        if ($("#id_equipment_filter").val() !== '' ){

            /* Remueve el event Source */
            calendar.removeAllEventSources();

            /* Asigna valores a los parametros de filtro */
            study_filter_id = '';
            equipment_filter_id = $("#id_equipment_filter").val();
            doctor_filter_id = '';

            /* Agrega un nuevo event source */
            calendar.addEventSource(
                {
                    url: appointments_list_url,
                    method: 'GET',
                    extraParams: {
                        study_id: study_filter_id,
                        equipment_id: equipment_filter_id,
                        doctor_id: doctor_filter_id
                    }
                }
            )
            /* Recarga los eventos */
            calendar.refetchEvents();
        } else {
            /* Se vacía el select de doctores y se deja la opción vacío
            $('#id_doctor_filter').empty();
            $('#id_doctor_filter').append('<option value="" selected="">---------</option>');
            $('#id_doctor_filter').trigger("chosen:updated");

             */

            /* Remueve el event Source */
            calendar.removeAllEventSources();

            /* Asigna valores a los parametros de filtro */
            study_filter_id = '';
            equipment_filter_id = '';
            doctor_filter_id = '';

            /* Agrega un nuevo event source */
            calendar.addEventSource(
                {
                    url: appointments_list_url,
                    method: 'GET',
                    extraParams: {
                        study_id: study_filter_id,
                        equipment_id: equipment_filter_id,
                        doctor_id: doctor_filter_id
                    }
                }
            )
            /* Recarga los eventos */
            calendar.refetchEvents();
        }

    });

    /* Al elegir el filtro del doctor */
    $("#id_doctor_filter").change(function(){
        console.log('Doctor filter');
        if ($("#id_doctor_filter").val() !== '' ){

            /* Remueve el event Source */
            calendar.removeAllEventSources();

            /* Asigna valores a los parametros de filtro */
            study_filter_id = '';
            equipment_filter_id = $("#id_equipment_filter").val();
            doctor_filter_id = $("#id_doctor_filter").val();

            /* Agrega un nuevo event source */
            calendar.addEventSource(
                {
                    url: appointments_list_url,
                    method: 'GET',
                    extraParams: {
                        study_id: study_filter_id,
                        equipment_id: equipment_filter_id,
                        doctor_id: doctor_filter_id
                    }
                }
            )

            /* Recarga los eventos */
            calendar.refetchEvents();

        } else {

            /* Remueve el event Source */
            calendar.removeAllEventSources();

            /* Asigna valores a los parametros de filtro */
            study_filter_id = '';
            equipment_filter_id = $("#id_equipment_filter").val();
            doctor_filter_id = '';

            /* Agrega un nuevo event source */
            calendar.addEventSource(
                {
                    url: appointments_list_url,
                    method: 'GET',
                    extraParams: {
                        study_id: study_filter_id,
                        equipment_id: equipment_filter_id,
                        doctor_id: doctor_filter_id
                    }
                }
            )

            /* Recarga los eventos */
            calendar.refetchEvents();
        }
    });
}