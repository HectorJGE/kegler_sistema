function initializeInputs(){
    /* Variables de posibles campos iniciales */
    var initial_medical_study_val = $('#id_medical_study').val();
    var initial_doctor_val = $('#id_doctor').val();
    var initial_medical_equipment_val = $('#id_medical_equipment').val();

    /* Se agregan chosen a todos los select */
    $('select').chosen();

    /* Si el campo de fecha no está vacío */
    if ($("#id_internal_results_delivery_date").val() !== '') {
        var fecha = $("#id_internal_results_delivery_date").val();
        var fecha_date = moment(fecha, 'DD/MM/YYYY HH:mm').toDate();

        /* Datetimepicker */
        var datetimepicker_internal_results_delivery_date = $("#id_internal_results_delivery_date").datetimepicker({
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
            timepicker: true,
            lang: 'es',
            locale: 'es',
            step: 15,
            format: 'd/m/Y H:i',
            inline: false,
            defaultDate : fecha_date
        });
    } else {
        var datetimepicker_internal_results_delivery_date = $('#id_internal_results_delivery_date').datetimepicker({
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
            timepicker: true,
            lang: 'es',
            locale: 'es',
            step: 15,
            format: 'd/m/Y H:i',
            inline: false,
        });
    }

    $("#id_consultation_date").mask("00/00/0000 00:00");
    $("#id_internal_results_delivery_date").mask("00/00/0000 00:00");
    $("#id_patient_results_delivery_date").mask("00/00/0000 00:00");
    $("#id_patient_birth_date").mask("00/00/0000");

    $("#id_consultation_date").click(function (){
        $(this).select();
    });
    $("#id_internal_results_delivery_date").click(function (){
        $(this).select();
    });
    $("#id_patient_results_delivery_date").click(function (){
        $(this).select();
    });
    $("#id_patient_birth_date").click(function (){
        $(this).select();
    });


    /* Si el campo de fecha no está vacío */
    if ($("#id_patient_results_delivery_date").val() !== '') {
        var fecha = $("#id_patient_results_delivery_date").val();
        var fecha_date = moment(fecha, 'DD/MM/YYYY HH:mm').toDate();

        /* Datetimepicker */
        var datetimepicker_patient_results_delivery_date = $("#id_patient_results_delivery_date").datetimepicker({
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
            timepicker: true,
            lang: 'es',
            locale: 'es',
            step: 15,
            format: 'd/m/Y H:i',
            inline: false,
            defaultDate : fecha_date
        });
    } else {
        $('#id_patient_results_delivery_date').datetimepicker({
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
            timepicker: true,
            lang: 'es',
            locale: 'es',
            step: 15,
            format: 'd/m/Y H:i',
            inline: false,
        });
    }

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

    if ($('#id_treating_doctor').val() !== ''){
        $('#div_id_new_treating_doctor').hide();
    } else {
        $('#div_id_new_treating_doctor').show();
    }

    /* Al checkear Paciente nuevo */
    $('#id_new_patient').on('click', function (){
        console.log('new patient');
        if ( $('#id_new_patient').prop('checked') === false ){
            $("#div_id_patient").show();
            $("#div_id_patient_name").hide();
            $("#div_id_patient_sex").hide();
            $("#div_id_patient_last_name").hide();
            $("#div_id_patient_document_number").hide();

            $("#div_id_patient_birth_date").hide();


        } else {
            $("#div_id_patient").hide();
            $("#div_id_patient_name").show();
            $("#div_id_patient_last_name").show();
            $("#div_id_patient_sex").show();
            $("#div_id_patient_document_number").show();

            $("#div_id_patient_birth_date").show();

        }
    });

    /* Al checkear Doctor tratante nuevo */
    $('#id_new_treating_doctor').on('click', function (){
        console.log('new treating_doctor');
        if ( $('#id_new_treating_doctor').prop('checked') === false ){
            $("#div_id_treating_doctor").show();
            $("#div_id_treating_doctor_name").hide();
            $("#div_id_treating_doctor_sex").hide();
            $("#div_id_treating_doctor_last_name").hide();

        } else {
            $("#div_id_treating_doctor").hide();
            $("#div_id_treating_doctor_name").show();
            $("#div_id_treating_doctor_last_name").show();
            $("#div_id_treating_doctor_sex").show();

        }
    });

    /* Funcion al enviarse el formulario */
    $("form").submit(function (e) {
        if( parseFloat($('#id_total_ammount_to_pay_patient_with_discount').val()) > 0 && $('#id_payment_method').val() === '' ){
            /* Alerta */
            Swal.fire({
                icon: 'warning',
                title: 'Método de Pago',
                text: 'Debe elegir un método de Pago cuando el monto a pagar del cliente es mayor a cero!',
            });
            return false
        }

        if ( $("#id_medical_equipment").val() === '' &&   $("#id_doctor").val() === '' ) {
            /* Alerta de Error */
            Swal.fire({
                icon: 'warning',
                title: 'Datos Incompletos',
                text: 'ATENCION! El Estudio debe tener asignado al menos un Equipo Médico o un Doctor.',
            });
            return false
        }

        if ( $("#id_medical_study_ammount").val() === '0' ) {
            /* Alerta de Error */
            Swal.fire({
                icon: 'warning',
                title: 'Datos Inválidos',
                text: 'ATENCION! El Estudio no puede valer 0.',
                footer: 'Póngase en contacto con el administrador para corregir estos datos.'
            });
            return false
        }

        var cover_type = parseInt($('#id_study_cover_type').val());

        if (cover_type === 0){
            $('.study_insurance_agreement_coverage_amount').val('0');
            $('.study_insurance_agreement_coverage_amount').trigger('input');
        } else {
            $('.study_insurance_agreement_coverage_percent').val('0');
            $('.study_insurance_agreement_coverage_percent').trigger('input');

        }

        if ($('.study_insurance_agreement_coverage_amount').val() === ''){
            $('.study_insurance_agreement_coverage_amount').val('0');
        }

        if ($('.study_insurance_agreement_coverage_percernt').val() === ''){
            $('.study_insurance_agreement_coverage_percent').val('0');
        }

        /* Se saca el disable de los select para que envíe los datos de estos */
        $('select').prop('disabled', false);

        /* Buscar entre insumos médicos el select de insumo no seleccionado para eliminar esa linea para correcto envío del form */
        $('.medical_supply_select').each( function(index, elem) {
            if($(this).val() === ''){
                var btn_delete = $(this).closest("tr.dynamic-form").find(".delete-formset-btn");
                btn_delete.trigger('click');
            }
        });

        $('#id_total_amount').unmask();
        $('#id_medical_study_ammount').unmask();
        $('#id_medical_supplies_ammount').unmask();

        $('#id_medical_study_ammount_to_pay_insurance').unmask();
        $('#id_medical_study_ammount_to_pay_patient').unmask();

        $('#id_medical_supplies_ammount_to_pay_insurance').unmask();
        $('#id_medical_supplies_ammount_to_pay_patient').unmask();

        $('#id_total_ammount_to_pay_insurance').unmask();
        $('#id_total_ammount_to_pay_patient').unmask();
        $('#id_discount').unmask();
        $('#id_total_ammount_to_pay_patient_with_discount').unmask();

        $('.medical_supply_price').unmask();
        $('.medical_supply_total_price').unmask();
        $('.ammount_to_pay_insurance').unmask();
        $('.ammount_to_pay_patient').unmask();
        $('.study_insurance_agreement_coverage_amount').unmask();
        $('.insurance_agreement_coverage_amount').unmask();
        $('#id_amount_paid').unmask();
        $('#id_patient_balance').unmask();



        $(this).find("[type=submit]").prop('disabled', true); //disable del boton enviar
        return true; // se envia el formulario
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
            step: 15,
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
            step: 15,
            format: 'd/m/Y',
            inline: false,
        });
    }

    /* Se inicializa datetimepicker de fecha de consulta */
    $('#id_consultation_date').datetimepicker({
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
        timepicker: true,
        step: 15,
        lang: 'es',
        locale: 'es',
        format: 'd/m/Y H:i',
        inline: false,
        defaultDate: new Date(),
    });

    /* Cambio en el select de pacientes */
    $("#id_patient").on('change', function (){
        if ($('#id_patient').val() === ''){
            console.log('no patient selected');
            $('#div_id_new_patient').show();
        } else {
            $.ajax({
                type: 'GET',
                url: get_patient_json_url.replace('9999', $('#id_patient').val() ),
                success: function (data, textStatus, jqXHR) {
                    $('#div_id_new_patient').hide();
                    get_patient_json_url = get_patient_json_url.replace($('#id_patient').val(), '9999');
                    $('#id_patient_insurance_plan').val(data.fields.insurance_plan);
                    $('#id_patient_insurance_plan').trigger("chosen:updated");
                    $('#id_patient_name').val(data.fields.name);
                    $('#id_patient_last_name').val(data.fields.last_name);
                    $('#id_patient_sex').val(data.fields.sex);
                    $('#id_patient_document_number').val(data.fields.document_number);
                    $('#id_contact_number').val(data.fields.phone_number);
                    $('#id_contact_email').val(data.fields.email);

                    $('#id_patient_birth_date').val(data.fields.birth_date);
                    $('#id_patient_weight').val(data.fields.weight);
                    $('#id_patient_city').val(data.fields.city);
                    $('#id_patient_address').val(data.fields.address);
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    /* Alerta de Error */
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        text: 'Error al tratar de obtener el plan de seguro del paciente.',
                        footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                    });
                    get_patient_json_url = get_patient_json_url.replace($('#id_patient').val(), '9999');
                }
            });
        }
    });

    $('.to-upper-case').keyup(function (){
        $(this).val( $(this).val().toUpperCase() );
    });

    /* Al elegir un plan de seguro */
    $('#id_patient_insurance_plan').change(function (){
        $("#id_medical_study").trigger('change');
    });

    /* Al elegir un estudio médico */
    $("#id_medical_study").change(function(){
        if ($("#id_medical_study").val() !== ''){
            var insurance_plan_val = $('#id_patient_insurance_plan').val();

            /* Traer costo estimado, covertura y duración */
            $.ajax({
                type: 'GET',
                url: get_medical_study_json_url.replace('9999', $("#id_medical_study").val() ),
                data: { insurance_plan_id: insurance_plan_val },
                success: function (data, textStatus, jqXHR) {
                    $('#id_medical_study_ammount').val(data.price.toString().replace('.0', ''));
                    $('#id_medical_study_ammount').trigger('input');

                    /* Pregunta si el equipo es de tipo ecografía para mostrar los doctores */
                    if(data.sector_code === 'ECO'){
                        $('#div_id_medical_equipment').hide();
                        $('#div_id_technician').hide();
                        $('#div_id_doctor').show();
                    }else{
                        $('#div_id_medical_equipment').show();
                        $('#div_id_technician').show();
                        $('#div_id_doctor').hide();
                    }

                    $('.study_insurance_agreement_coverage_percent').val(data.insurance_coverage_percent);
                    $('.study_insurance_agreement_coverage_percent').trigger('input');
                    $('.study_insurance_agreement_coverage_amount').val(data.insurance_coverage_amount);
                    $('.study_insurance_agreement_coverage_amount').trigger('input');
                    $('#id_study_cover_type').val(data.study_cover_type);
                    $('#id_study_cover_type').trigger("chosen:updated");
                    $('#id_study_cover_type').trigger("change");


                    get_medical_study_json_url = get_medical_study_json_url.replace($("#id_medical_study").val(), '9999');
                    calculateTotalAmmount();
                    calculateTotalAmmountToPayInsurance();
                    calculateTotalAmmountToPayPatient();
                    calculateDiscount();
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    /* Alerta de Error */
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        text: '"Error al tratar de obtener el precio del estudio.',
                        footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                    });
                    get_medical_study_json_url = get_medical_study_json_url.replace($("#id_medical_study").val(), '9999');
                }
            });

            /* Traer equipos de ese estudio */
            $.ajax({
                type: 'GET',
                url: list_medical_equiment_by_study_url.replace('9999', $("#id_medical_study").val() ),
                beforeSend: function(){
                    $('#id_medical_equipment').empty();
                    $('#id_medical_equipment').append('<option value="" selected="">---------</option>');
                },
                success: function (data, textStatus, jqXHR) {
                    data.forEach(function(item, index, array) {
                        $('#id_medical_equipment').append('<option value="' + item.id + '">' + item.name + '</option>');
                    });
                    if(initial_medical_equipment_val !== ''){
                        $('#id_medical_equipment').val(initial_medical_equipment_val);
                    }

                    $('#id_medical_equipment').trigger("chosen:updated");
                    list_medical_equiment_by_study_url = list_medical_equiment_by_study_url.replace($("#id_medical_study").val(), '9999');
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    /* Alerta de Error */
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        text: 'Error al tratar de obtener la lista de equipos para el estudio.',
                        footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                    });
                    list_medical_equiment_by_study_url = list_medical_equiment_by_study_url.replace($("#id_medical_study").val(), '9999');
                }
            });

            /* Traer doctores de ese estudio */
            $.ajax({
                type: 'GET',
                url: list_doctor_by_study_url.replace('9999', $("#id_medical_study").val() ),
                beforeSend: function(){
                    $('#id_doctor').empty();
                    $('#id_doctor').append('<option value="" selected="">---------</option>');
                },
                success: function (data, textStatus, jqXHR) {
                    data.forEach(function(item, index, array) {
                        $('#id_doctor').append('<option value="' + item.id + '">' + item.name + '</option>');
                    });
                    if(initial_doctor_val !== '') {
                        $('#id_doctor').val(initial_doctor_val);
                    }
                    $('#id_doctor').trigger("chosen:updated");
                    list_doctor_by_study_url = list_doctor_by_study_url.replace($("#id_medical_study").val(), '9999');
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    /* Alerta de Error */
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        text: 'Error al tratar de obtener la lista de doctores para el estudio.',
                        footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                    });
                    list_doctor_by_study_url = list_doctor_by_study_url.replace($("#id_medical_study").val(), '9999');
                }
            });

        } else {
            $('#id_medical_study_ammount').val('');
            calculateTotalAmmount();
            calculateTotalAmmountToPayInsurance();
            calculateTotalAmmountToPayPatient();
            calculateDiscount();
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

    /* Al cambiar el doctor */
    $('#id_doctor').change(function (){
        var doctor_id = $('#id_doctor').val();
        if(doctor_id !== ''){
            $('#id_reporting_doctor').val(doctor_id);
            $('#id_reporting_doctor').trigger("chosen:updated");
            $("#div_id_reporting_doctor").show();
        } else {
            $('#id_reporting_doctor').val(doctor_id);
            $('#id_reporting_doctor').trigger("chosen:updated");
            $("#div_id_reporting_doctor").hide();
        }
    });

    /* Al cambiar porcentaje de cobertura del estudio por el seguro */
    $('.study_insurance_agreement_coverage_percent').on('keyup', function (){
        if ($('.study_insurance_agreement_coverage_percent').val() === ''){
            $('.study_insurance_agreement_coverage_percent').val('0');
            $('.study_insurance_agreement_coverage_percent').trigger('input');
        }

        console.log('medical study coverage percent');
        calculateMedicalStudyCoverage();
        calculateTotalAmmountToPayInsurance();
        calculateTotalAmmountToPayPatient();
        calculateDiscount();
    });

    /* Al cambiar monto pagado por el paciente */
    $('#id_amount_paid').on('keyup', function () {
        if ($('#id_amount_paid').val() === '') {
            $('#id_amount_paid').val('0');
            $('#id_amount_paid').trigger('input');
        }
        calculatePatientBalance();
    });

    $('.study_insurance_agreement_coverage_percent').on('click', function (){
        $('.study_insurance_agreement_coverage_percent').select();
    });

    $('.study_insurance_agreement_coverage_amount').on('click', function (){
        $('.study_insurance_agreement_coverage_amount').select();
    });

    /* Al cambiar monto de cobertura del estudio por el seguro */
    $('.study_insurance_agreement_coverage_amount').on('keyup', function (){
        if ($('.study_insurance_agreement_coverage_amount').val() === ''){
            $('.study_insurance_agreement_coverage_amount').val('0');
            $('.study_insurance_agreement_coverage_amount').trigger('input');
        }
        console.log('medical study coverage amount');
        calculateMedicalStudyCoverage();
        calculateTotalAmmountToPayInsurance();
        calculateTotalAmmountToPayPatient();
        calculateDiscount();
    });

    /* Al cambiar descuento */
    $('#id_discount').on('keyup', function (){
        console.log('discount');
        calculateDiscount();
    });

    /* Al cambiar metodo de pago */
    $('#id_payment_method').on('change', function (){
        console.log('payment method');
        if( $('#id_payment_method').val() === '1' || $('#id_payment_method').val() === ''  ){
            $('#div_id_payment_reference').hide();
        }else{
            $('#div_id_payment_reference').show();
        }
    });

    /* Mask para monto estudio médico */
    if ($('#id_medical_study_ammount').val() !== ''){
        var medical_study_ammount = $('#id_medical_study_ammount').val().replace('.0', '');
        $('#id_medical_study_ammount').val('');
        $('#id_medical_study_ammount').val(medical_study_ammount);
        $('#id_medical_study_ammount').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_medical_study_ammount').mask("###.###.##0", {reverse: true});
    }

    /* Mask para monto cobertura estudio médico */
    if ($('.study_insurance_agreement_coverage_amount').val() !== ''){
        var study_insurance_agreement_coverage_amount = $('.study_insurance_agreement_coverage_amount').val().replace('.0', '');
        $('.study_insurance_agreement_coverage_amount').val('');
        $('.study_insurance_agreement_coverage_amount').val(study_insurance_agreement_coverage_amount);
        $('.study_insurance_agreement_coverage_amount').mask("###.###.##0", {reverse: true});
    } else {
        $('.study_insurance_agreement_coverage_amount').mask("###.###.##0", {reverse: true});
    }

    /* Mask para monto estudio médico a pagar por el seguro */
    if ($('#id_medical_study_ammount_to_pay_insurance').val() !== ''){
        var medical_study_ammount_to_pay_insurance = $('#id_medical_study_ammount_to_pay_insurance').val().replace('.0', '');
        $('#id_medical_study_ammount_to_pay_insurance').val('');
        $('#id_medical_study_ammount_to_pay_insurance').val(medical_study_ammount_to_pay_insurance);
        $('#id_medical_study_ammount_to_pay_insurance').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_medical_study_ammount_to_pay_insurance').mask("###.###.##0", {reverse: true});
    }

    /* Mask para monto estudio médico a pagar por el paciente */
    if ($('#id_medical_study_ammount_to_pay_patient').val() !== ''){
        var medical_study_ammount_to_pay_patient = $('#id_medical_study_ammount_to_pay_patient').val().replace('.0', '');
        $('#id_medical_study_ammount_to_pay_patient').val('');
        $('#id_medical_study_ammount_to_pay_patient').val(medical_study_ammount_to_pay_patient);
        $('#id_medical_study_ammount_to_pay_patient').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_medical_study_ammount_to_pay_patient').mask("###.###.##0", {reverse: true});
    }

    /* Mask para monto insumos médicos */
    if ($('#id_medical_supplies_ammount').val() !== ''){
        var medical_supplies_ammount = $('#id_medical_supplies_ammount').val().replace('.0', '');
        $('#id_medical_supplies_ammount').val('');
        $('#id_medical_supplies_ammount').val(medical_supplies_ammount);
        $('#id_medical_supplies_ammount').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_medical_supplies_ammount').mask("###.###.##0", {reverse: true});
    }

    /* Mask para monto insumo médico a pagar por el seguro */
    if ($('#id_medical_supplies_ammount_to_pay_insurance').val() !== ''){
        var medical_supplies_ammount_to_pay_insurance = $('#id_medical_supplies_ammount_to_pay_insurance').val().replace('.0', '');
        $('#id_medical_supplies_ammount_to_pay_insurance').val('');
        $('#id_medical_supplies_ammount_to_pay_insurance').val(medical_supplies_ammount_to_pay_insurance);
        $('#id_medical_supplies_ammount_to_pay_insurance').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_medical_supplies_ammount_to_pay_insurance').mask("###.###.##0", {reverse: true});
    }

    /* Mask para monto insumo médico a pagar por el paciente */
    if ($('#id_medical_supplies_ammount_to_pay_patient').val() !== ''){
        var medical_supplies_ammount_to_pay_patient = $('#id_medical_supplies_ammount_to_pay_patient').val().replace('.0', '');
        $('#id_medical_supplies_ammount_to_pay_patient').val('');
        $('#id_medical_supplies_ammount_to_pay_patient').val(medical_supplies_ammount_to_pay_patient);
        $('#id_medical_supplies_ammount_to_pay_patient').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_medical_supplies_ammount_to_pay_patient').mask("###.###.##0", {reverse: true});
    }

    /* Mask para monto total */
    if ($('#id_total_amount').val() !== ''){
        var total_amount = $('#id_total_amount').val().replace('.0', '');
        $('#id_total_amount').val('');
        $('#id_total_amount').val(total_amount);
        $('#id_total_amount').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_total_amount').mask("###.###.##0", {reverse: true});
    }

    /* Mask para monto total a pagar por el seguro */
    if ($('#id_total_ammount_to_pay_insurance').val() !== ''){
        var total_ammount_to_pay_insurance = $('#id_total_ammount_to_pay_insurance').val().replace('.0', '');
        $('#id_total_ammount_to_pay_insurance').val('');
        $('#id_total_ammount_to_pay_insurance').val(total_ammount_to_pay_insurance);
        $('#id_total_ammount_to_pay_insurance').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_total_ammount_to_pay_insurance').mask("###.###.##0", {reverse: true});
    }

    /* Mask para monto total a pagar por el paciente */
    if ($('#id_total_ammount_to_pay_patient').val() !== ''){
        var total_ammount_to_pay_patient = $('#id_total_ammount_to_pay_patient').val().replace('.0', '');
        $('#id_total_ammount_to_pay_patient').val('');
        $('#id_total_ammount_to_pay_patient').val(total_ammount_to_pay_patient);
        $('#id_total_ammount_to_pay_patient').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_total_ammount_to_pay_patient').mask("###.###.##0", {reverse: true});
    }

    /* Mask para descuento */
    if ($('#id_discount').val() !== ''){
        var discount = $('#id_discount').val().replace('.0', '');
        $('#id_discount').val('');
        $('#id_discount').val(discount);
        $('#id_discount').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_discount').val('0');
        $('#id_discount').mask("###.###.##0", {reverse: true});
    }

    /* Mask para monto total a pagar por el paciente con descuento */
    if ($('#id_total_ammount_to_pay_patient_with_discount').val() !== ''){
        var total_ammount_to_pay_patient_with_discount = $('#id_total_ammount_to_pay_patient_with_discount').val().replace('.0', '');
        $('#id_total_ammount_to_pay_patient_with_discount').val('');
        $('#id_total_ammount_to_pay_patient_with_discount').val(total_ammount_to_pay_patient_with_discount);
        $('#id_total_ammount_to_pay_patient_with_discount').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_total_ammount_to_pay_patient_with_discount').mask("###.###.##0", {reverse: true});
    }

    /* Mask para monto pagado */
    if ($('#id_amount_paid').val() !== ''){
        var amount_paid = $('#id_amount_paid').val().replace('.0', '');
        $('#id_amount_paid').val('');
        $('#id_amount_paid').val(amount_paid);
        $('#id_amount_paid').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_amount_paid').mask("###.###.##0", {reverse: true});
        $('#id_amount_paid').val('0');
        $('#id_amount_paid').trigger('input');
    }

    /* Mask para saldo paciente */
    if ($('#id_patient_balance').val() !== ''){
        var patient_balance = $('#id_patient_balance').val().replace('.0', '');
        $('#id_patient_balance').val('');
        $('#id_patient_balance').val(patient_balance);
        $('#id_patient_balance').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_patient_balance').mask("###.###.##0", {reverse: true});
        $('#id_patient_balance').val('0');
        $('#id_patient_balance').trigger('input');
    }

    /* Si ya se tienen datos iniciales */
    if (initial_medical_study_val === ''){
        $('#div_id_medical_equipment').hide();
        $('#div_id_doctor').hide();
        $('#div_id_technician').hide();
    } else {
        if(initial_doctor_val === ''){
            $('#div_id_doctor').hide();
        } else{
            $('#div_id_doctor').show();
        }
        if(initial_medical_equipment_val === ''){
            $('#div_id_medical_equipment').hide();
            $('#div_id_technician').hide();
        } else {
            $('#div_id_medical_equipment').show();
            $('#div_id_technician').show();
        }
        $('#id_medical_study').trigger('change');
    }

    /* Se esconden los inputs de pagos si nohay nada que pagar por el paciente */
    if ( $('#id_total_ammount_to_pay_patient').val() === '0' || $('#id_total_ammount_to_pay_patient').val() === '' ){
        $('#div_id_payment_method').hide();
        $('#div_id_payment_reference').hide();
        $('#div_id_discount').hide();
        $('#div_id_total_ammount_to_pay_patient_with_discount').hide();

    } else {
        $('#div_id_payment_method').show();
        $('#div_id_amount_paid').show();

        if( $('#id_payment_method').val() === '1' || $('#id_payment_method').val() === ''  ){
            $('#div_id_payment_reference').hide();
        }else{
            $('#div_id_payment_reference').show();
        }

        $('#div_id_discount').show();
        $('#div_id_total_ammount_to_pay_patient_with_discount').show();
    }

    /* Se esconde médico asignado si no hay doctor */
    if( $("#id_reporting_doctor").val() === ""){
        $("#div_id_reporting_doctor").hide();
    } else {
        $("#div_id_reporting_doctor").show();
    }

    $('#id_study_cover_type').change(function (){
        hideUnusedStudyCover();
        calculateMedicalStudyCoverage();
    });

    function hideUnusedStudyCover(){
        let input = $('#id_study_cover_type');
        console.log("valor de study_cover_type:");
        console.log(input.val());
        let coverage_amount = $('.study_insurance_agreement_coverage_amount').closest('#div_id_insurance_agreement_coverage_amount');
        let coverage_percent = $('.study_insurance_agreement_coverage_percent').closest('#div_id_insurance_agreement_coverage_percent');
        if(parseInt(input.val()) === 0) {
            console.log('estudio es por porcentaje');
            coverage_amount.hide();
            coverage_percent.show();
            $('.study_insurance_agreement_coverage_amount').val("0");
            $('.study_insurance_agreement_coverage_amount').trigger('input');
        }else{
            console.log('estudio es por monto');
            coverage_percent.hide();
            coverage_amount.show();
            $('.study_insurance_agreement_coverage_percent').val("0");
            $('.study_insurance_agreement_coverage_percent').trigger('input');
        }
    }

}