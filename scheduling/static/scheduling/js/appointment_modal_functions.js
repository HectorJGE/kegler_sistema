function appointmentModalInitialization(){

    /* Funcion al mostrar modal */
    $( "#appointmentModal" ).on('shown.bs.modal', function() {

        /* Chosen para los selects del modal */
        $('.select.form-control').chosen(
            {
                no_results_text: "No se encontraron resultados para",

            }
        );

        $("#id_patient_birth_date").mask("00/00/0000");
        $("#id_appointment_date_start").mask("00/00/0000 00:00:00");
        $("#id_appointment_date_end").mask("00/00/0000 00:00:00");

        $("#id_patient_birth_date").click(function (){
            $(this).select();
        });
        $("#id_appointment_date_start").click(function (){
            $(this).select();
        });
        $("#id_appointment_date_end").click(function (){
            $(this).select();
        });


        /* Se esconden los inputs de crear pacientes */
        $("#div_id_patient_name").hide();
        $("#div_id_patient_last_name").hide();
        $("#div_id_patient_sex").hide();
        $("#div_id_patient_document_number").hide();

        /* Se esconden los inputs de crear doctor tratante */
        $("#div_id_treating_doctor_name").hide();
        $("#div_id_treating_doctor_last_name").hide();
        $("#div_id_treating_doctor_sex").hide();

        $("#div_id_patient_birth_date").hide();


        if ($('#id_patient').val() !== ''){
            $('#div_id_new_patient').hide();
        } else {
            $('#div_id_new_patient').show();
        }

        /* Mask para costo estimado */
        if ($('#id_estimated_cost').val() !== ''){
            var estimated_cost = $('#id_estimated_cost').val().replace('.0', '');
            $('#id_estimated_cost').val('');
            $('#id_estimated_cost').val(estimated_cost);
            $('#id_estimated_cost').mask("###.###.##0", {reverse: true});
        } else {
            $('#id_estimated_cost').mask("###.###.##0", {reverse: true});
        }

        $('#id_estimated_cost').on('keyup', function () {
            if ($('#id_estimated_cost').val() === '') {
                $('#id_estimated_cost').val('0');
                $('#id_estimated_cost').trigger('input');
            }
        });

        /* Al checkear Paciente nuevo */
        $('#id_new_patient').on('click', function (){
            console.log('new patient');
            if ( $('#id_new_patient').prop('checked') === false ){
                $("#div_id_patient_autocomplete").show();
                $("#div_id_patient_name").hide();
                $("#div_id_patient_last_name").hide();
                $("#div_id_patient_sex").hide();
                $("#div_id_patient_document_number").hide();

                $("#div_id_patient_birth_date").hide();

            } else {
                $("#div_id_patient_autocomplete").hide();
                $("#div_id_patient_name").show();
                $("#div_id_patient_last_name").show();
                $("#div_id_patient_sex").show();
                $("#div_id_patient_document_number").show();

                $("#div_id_patient_birth_date").show();

            }
        });

        /* Al checkear Doctor Tratante nuevo */
        $('#id_new_treating_doctor').on('click', function (){
            console.log('new treating_doctor');
            if ( $('#id_new_treating_doctor').prop('checked') === false ){
                $("#div_id_treating_doctor").show();
                $("#div_id_treating_doctor_name").hide();
                $("#div_id_treating_doctor_last_name").hide();
                $("#div_id_treating_doctor_sex").hide();

            } else {
                $("#div_id_treating_doctor").hide();
                $("#div_id_treating_doctor_name").show();
                $("#div_id_treating_doctor_last_name").show();
                $("#div_id_treating_doctor_sex").show();

            }
        });

        /* Si el campo de fecha no está vacío */
        if ($("#id_patient_birth_date").val() !== '') {
            var fecha = $("#id_patient_birth_date").val();
            var fecha_date = moment(fecha, 'DD/MM/YYYY HH:mm').toDate();

            /* Datetimepicker */
            var datetimepicker_birth_date = $("#id_patient_birth_date").datetimepicker({
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
                inline: false,
                defaultDate : fecha_date
            });
        } else {
            $('#id_patient_birth_date').datetimepicker({
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
                inline: false,
            });
        }

        /* Al cambiar el plan de seguro */
        $("#id_insurance_plan").on('change', function (){
            getMedicalStudyDetails();
        });


        /* Cambio en el select de pacientes */
        $("#id_patient").on('change', function (){
            console.log("Se activó patient change");
            if ($('#id_patient').val() === ''){
                console.log('no patient selected');
                $('#div_id_new_patient').show();
            } else {
                $.ajax({
                    type: 'GET',
                    url: get_patient_json_url.replace('9999', $('#id_patient').val() ),
                    success: function (data, textStatus, jqXHR) {
                        $('#div_id_new_patient').hide();
                        $('#id_insurance_plan').val(data.fields.insurance_plan);
                        $('#id_insurance_plan').trigger("chosen:updated");
                        $('#id_patient_name').val(data.fields.name);
                        $('#id_patient_last_name').val(data.fields.last_name);
                        $('#id_patient_sex').val(data.fields.sex);
                        $('#id_patient_document_number').val(data.fields.document_number);
                        /* invoicing */
                        $('#id_contact_number').val(data.fields.phone_number);
                        $('#id_contact_email').val(data.fields.email);
                        $('#id_patient_tax_id_number').val(data.fields.tax_identification_number);
                        $('#id_patient_tax_id_name').val(data.fields.tax_identification_name);
                        $('#id_patient_address').val(data.fields.address);
                        $('#id_patient_is_taxpayer').prop('checked', data.fields.is_taxpayer);


                        $('#id_patient_birth_date').val(data.fields.birth_date);
                        $('#id_patient_weight').val(data.fields.weight);
                        $('#id_patient_city').val(data.fields.city);


                        getMedicalStudyDetails();
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        /* Alerta de Error */
                        Swal.fire({
                            icon: 'error',
                            title: 'Error...',
                            text: 'Error al tratar de obtener el plan de seguro del paciente.',
                            footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                        });
                    }
                });


            }
        });

        $('#id_patient_autocomplete').autocomplete({
            source: get_patient_autocomplete_json_url,
            select: function (event, ui) {
                console.log(ui.item);
                event.preventDefault();
                $('#id_patient').val(ui.item.value);
                $('#id_patient_autocomplete').val(ui.item.label);
                $('#id_patient').trigger('change');
            }
        });

        $('.to-upper-case').keyup(function (){
            $(this).val( $(this).val().toUpperCase() );
        });


        /* Si el campo de fecha no está vacío */
        if ($("#id_appointment_date_start").val() !== '') {
            var str_fecha = $("#id_appointment_date_start").val();
            str_fecha = str_fecha.substring(0, 16);
            $("#id_appointment_date_start").val(str_fecha);
            var fecha_inicio = $("#id_appointment_date_start").val();

            str_fecha = $("#id_appointment_date_end").val();
            str_fecha = str_fecha.substring(0, 16);
            $("#id_appointment_date_end").val(str_fecha);
            var fecha_fin = $("#id_appointment_date_end").val();

            var fecha_inicio_date = moment(fecha_inicio, 'DD/MM/YYYY HH:mm').toDate();
            var fecha_fin_date = moment(fecha_fin, 'DD/MM/YYYY HH:mm').toDate();

            /* Datetimepicker */
            var datetimepicker_start = $("#id_appointment_date_start").datetimepicker({
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
                lang: 'es',
                locale: 'es',
                format: 'd/m/Y H:i',
                inline: false,
                step: 15,
                defaultDate : fecha_inicio_date
            });

            var datetimepicker_end = $("#id_appointment_date_end").datetimepicker({
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
                lang: 'es',
                locale: 'es',
                format: 'd/m/Y H:i',
                inline: false,
                step: 15,
                defaultDate : fecha_fin_date
            });


            /* Si el campo de fecha está vacío */
        } else {
            /* Datetimepicker */
            var datetimepicker_start = $("#id_appointment_date_start").datetimepicker({
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
                lang: 'es',
                locale: 'es',
                format: 'd/m/Y H:i',
                inline: false,
                step: 15,
                defaultDate : new Date()
            });
            var datetimepicker_end = $("#id_appointment_date_end").datetimepicker({
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
                lang: 'es',
                locale: 'es',
                format: 'd/m/Y H:i',
                inline: false,
                step: 15,
                defaultDate : new Date()
            });
        }


        /* Al elegir un estudio médico */
        $("#id_medical_study").change(function(){
            console.log("Se activó medical study change");
            if ($("#id_medical_study").val() !== ''){
                getMedicalStudyDetails();
                let medical_equipment_val = $('#id_medical_equipment').val();

                /* Traer equipos de ese estudio */
                $.ajax({
                    type: 'GET',
                    url: list_medical_equiment_by_study_url.replace('9999', $("#id_medical_study").val()),
                    beforeSend: function () {
                        $('#id_medical_equipment').empty();
                        $('#id_medical_equipment').append('<option value="" selected="">---------</option>');
                    },
                    success: function (data, textStatus, jqXHR) {
                        data.forEach(function (item, index, array) {
                            $('#id_medical_equipment').append('<option value="' + item.id + '">' + item.name + '</option>');
                        })
                        if (medical_equipment_val !== '') {
                            $('#id_medical_equipment').val(medical_equipment_val);
                        }
                        $('#id_medical_equipment').trigger("chosen:updated");
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        /* Alerta de Error */
                        Swal.fire({
                            icon: 'error',
                            title: 'Error...',
                            text: 'Error al tratar de obtener la lista de equipos para el estudio.',
                            footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                        });
                    }
                });

                let doctor_val = $("#id_doctor").val();

                /* Traer doctores de ese estudio */
                $.ajax({
                    type: 'GET',
                    url: list_doctor_by_study_url.replace('9999', $("#id_medical_study").val()),
                    beforeSend: function () {
                        $('#id_doctor').empty();
                        $('#id_doctor').append('<option value="" selected="">---------</option>');
                    },
                    success: function (data, textStatus, jqXHR) {
                        data.forEach(function (item, index, array) {
                            $('#id_doctor').append('<option value="' + item.id + '">' + item.name + '</option>');
                        })
                        if (doctor_val !== '') {
                            $('#id_doctor').val(doctor_val);
                        }

                        $('#id_doctor').trigger("chosen:updated");
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        /* Alerta de Error */
                        Swal.fire({
                            icon: 'error',
                            title: 'Error...',
                            text: 'Error al tratar de obtener la lista de doctores para el estudio.',
                            footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                        });
                    }
                });

            }
        });

        $('#id_medical_study_autocomplete').autocomplete({
            source: get_medical_study_autocomplete_json_url,
            select: function (event, ui) {
                console.log(ui.item);
                event.preventDefault();
                $('#id_medical_study').val(ui.item.value);
                $('#id_medical_study_autocomplete').val(ui.item.label);
                $('#id_medical_study').trigger('change');
            }
        });

        $('#id_patient_autocomplete').keyup(function (){
            if ( $('#id_patient_autocomplete').val() === '' ) {
                $('#div_id_new_patient').show();
            } else {
                $('#div_id_new_patient').hide();
            }
        });

        /* Al Elegir un equipo médico */
        $('#id_medical_equipment').change(function (){
            if ( $('#id_medical_equipment').val() !== '' ){
                /* Controlar disponibilidad de Horario Equipo médico */
                $.ajax({
                    type: 'GET',
                    url: appointments_check_equipment_availability_url,
                    data:
                        {
                            'event_datetime_start': $("#id_appointment_date_start").val(),
                            'event_datetime_end': $("#id_appointment_date_end").val(),
                            'equipment_id': $("#id_medical_equipment").val(),
                        },
                    success: function (data, textStatus, jqXHR) {
                        if (data.msg !== ''){
                            Swal.fire({
                                icon: 'warning',
                                title: 'Alerta Disponibilidad Equipo Médico',
                                text: data.msg,
                            });
                        }
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        /* Alerta de Error */
                        Swal.fire({
                            icon: 'error',
                            title: 'Error...',
                            text: 'Error al tratar de obtener la disponibilidad del equipo médico\n Puede continuar su agendamiento, pero con el riesgo de agendar 2 estudios en el mismo horario y con el mismo equipo. \n Por favor contacte con el equipo de mantenimiento del sistema.',
                            footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                        });
                    }
                });
            }

        });

        /* Al Elegir un doctor */
        $('#id_doctor').change(function (){
            if ( $('#id_doctor').val() !== '' ){
                /* Controlar disponibilidad de Horario y calendario de doctor */
                $.ajax({
                    type: 'GET',
                    url: appointments_check_doctor_availability_url,
                    data:
                        {
                            'event_datetime_start': $("#id_appointment_date_start").val(),
                            'event_datetime_end': $("#id_appointment_date_end").val(),
                            'doctor_id': $("#id_doctor").val(),
                        },
                    success: function (data, textStatus, jqXHR) {
                        if (data.msg !== ''){
                            Swal.fire({
                                icon: 'warning',
                                title: 'Alerta Disponibilidad Doctor',
                                text: data.msg,
                            });
                        }
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        /* Alerta de Error */
                        Swal.fire({
                            icon: 'error',
                            title: 'Error...',
                            text: "Error al tratar de obtener la disponibilidad del doctor.\n " +
                                "Puede continuar su agendamiento, pero con el riesgo de agendar 2 estudios en el mismo horario y con el mismo doctor. \n " +
                                "Por favor contacte con el equipo de mantenimiento del sistema.",
                            footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                        });
                    }
                });
            }

        });

        /* Cambio en el select de Doctores tratantes */
        $("#id_treating_doctor").on('change', function () {
            if ($('#id_treating_doctor').val() === '') {
                console.log('no treating doctor selected');
                $('#div_id_new_treating_doctor').show();
            } else {
                $('#div_id_new_treating_doctor').hide();
            }
        });

        /* Función para obtener detalles de estudio médico */
        function getMedicalStudyDetails(){
            /* Traer costo estimado y duración */
            var insurance_plan_val = $('#id_insurance_plan').val();
            var medical_study_val = $("#id_medical_study").val();
            if (medical_study_val !== ''){
                var url_to_send = get_medical_study_json_url.replace('9999', medical_study_val );
                $.ajax({
                    type: 'GET',
                    url: url_to_send,
                    data: { insurance_plan_id: insurance_plan_val },
                    success: function (data, textStatus, jqXHR) {
                        var total_price =  parseFloat(data.price);
                        var percent = data.insurance_coverage_percent;

                        var amount_to_pay_insurance = calculatePercent(total_price, percent);
                        var amount_to_pay_patient = total_price - amount_to_pay_insurance;

                        $('#id_estimated_cost').val(amount_to_pay_patient);
                        $('#id_estimated_cost').trigger('input');

                        /* Pregunta si el equipo es de tipo ecografía para mostrar los doctores */
                        if(data.sector_code === 'ECO'){
                            $('#div_id_medical_equipment').hide();
                            $('#div_id_doctor').show();
                            $('#id_medical_equipment').val('');
                            $('#id_medical_equipment').trigger("chosen:updated");
                        }else{
                            $('#div_id_medical_equipment').show();
                            $('#div_id_doctor').hide();
                            $('#id_doctor').val('');
                            $('#id_doctor').trigger("chosen:updated");
                        }

                        var fecha_inicio = $("#id_appointment_date_start").val();
                        var fecha_fin_date = moment(fecha_inicio, 'DD/MM/YYYY HH:mm').add(data.duration_in_minutes, 'minutes').toDate();
                        $("#id_appointment_date_end").val(dateToDMY(fecha_fin_date));
                        datetimepicker_end.datetimepicker("setDate", fecha_fin_date);
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        /* Alerta de Error */
                        Swal.fire({
                            icon: 'error',
                            title: 'Error...',
                            text: "Error al tratar de obtener el precio del estudio.",
                            footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                        });
                    }
                });
            }
        }

        /* Esconder los divs campos de equipos y doctores dependiendo de si tiene valores al cargarse */
        $('#div_id_medical_equipment').hide();
        $('#div_id_doctor').hide();

        var medical_equipment_value = $('#id_medical_equipment').val();
        var doctor_value = $('#id_doctor').val();

        if (medical_equipment_value !== ''){
            $('#div_id_medical_equipment').show();
            /* Controlar disponibilidad de Horario Equipo médico */
            $.ajax({
                type: 'GET',
                url: appointments_check_equipment_availability_url,
                data:
                    {
                        'event_datetime_start': $("#id_appointment_date_start").val(),
                        'event_datetime_end': $("#id_appointment_date_end").val(),
                        'equipment_id': $("#id_medical_equipment").val(),
                    },
                success: function (data, textStatus, jqXHR) {
                    if (data.msg !== ''){
                        Swal.fire({
                            icon: 'warning',
                            title: 'Alerta Disponibilidad de Equipo Médico',
                            text: data.msg,
                        });
                    }
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    /* Alerta de Error */
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        text: "Error al tratar de obtener la disponibilidad del equipo médico\n Puede continuar su agendamiento, pero con el riesgo de agendar 2 estudios en el mismo horario y con el mismo equipo. \n Por favor contacte con el equipo de mantenimiento del sistema.",
                        footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                    });
                }
            });
        }

        if(doctor_value !== ''){
            $('#div_id_doctor').show();
            /* Controlar disponibilidad de Horario y calendario de doctor */
            $.ajax({
                type: 'GET',
                url: appointments_check_doctor_availability_url,
                data:
                    {
                        'event_datetime_start': $("#id_appointment_date_start").val(),
                        'event_datetime_end': $("#id_appointment_date_end").val(),
                        'doctor_id': $("#id_doctor").val(),
                    },
                success: function (data, textStatus, jqXHR) {
                    if (data.msg !== ''){
                        Swal.fire({
                            icon: 'warning',
                            title: 'Alerta Disponibilidad Doctor',
                            text: data.msg,
                        });
                    }
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    /* Alerta de Error */
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        text: "Error al tratar de obtener la disponibilidad del doctor.\n " +
                            "Puede continuar su agendamiento, pero con el riesgo de agendar 2 estudios en el mismo horario y con el mismo doctor. \n " +
                            "Por favor contacte con el equipo de mantenimiento del sistema.",
                        footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                    });
                }
            });
        }

        initializeFormsets();

    });

}