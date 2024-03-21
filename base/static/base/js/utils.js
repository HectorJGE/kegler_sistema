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
        console.log('sending form');
        e.preventDefault();
        //let form_data = $(this).serialize();
        //let form_data = $(this).serializeArray();
        let form_data = new FormData(this);
        /*
        let image_files = $('input[name="appointment_documents-0-file"]').val();
        form_data.push({
            name: 'file',
            value: image_files
            }
        );
        */
        console.log(form_data);


        /* Send form */
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: form_data,
            //enctype: 'multipart/form-data',
            processData: false,
            contentType: false,
            success: function (xhr, ajaxOptions, thrownError) {
                /* Alerta */
                swal.fire("Datos guardados!");
                if ($(xhr).find('.has-error').length > 0) {
                    $(modal).find('.modal-body').html(xhr);
                } else {
                    $(modal).modal('toggle');
                    /* Recarga los eventos */
                    calendar.refetchEvents();
                }
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr);
                let error_html = '<p>Error al tratar de enviar este formulario!</p><br><ul>';
                let errors = xhr.responseJSON.errors;
                if (errors){
                    for (let i = 0; i < errors.length; i++) {
                        error_html += '<li>' + errors[i] + "</li>";
                    }
                }

                error_html = error_html + '</ul>'
                /* Alerta de Error */
                Swal.fire({
                    icon: 'error',
                    title: 'Error...',
                    html: error_html,
                    footer: '<p>Si sus datos son correctos y el error persiste, favor póngase en contacto con el administrador del sistema.</p>'
                });

            }
        });

    });
}

function calculatePercent(num, percent) {
    return (percent / 100) * num;
}


function validateAppointmentForm() {
    let date_start = $("#id_appointment_date_start").val();
    let date_end = $("#id_appointment_date_end").val();
    let patient = $('#id_patient').val();
    let new_patient = $("#id_new_patient").val();
    let patient_weight = $('#id_patient_weight').val();

    let medical_study = $('#id_medical_study').val();
    let medical_equipment = $("#id_medical_equipment").val();
    let doctor = $("#id_doctor").val();

    /* Invoicing */
    let tax_id_number = $('#id_patient_tax_id_number').val();
    let tax_id_name = $('#id_patient_tax_id_name').val();
    let patient_email = $('#id_contact_email').val();
    let contact_number = $('#id_contact_number').val();
    let patient_address = $('#id_patient_address').val();

    let error_messages = [];

    /* Datetime range */
    if (date_start === '' || date_end === '') {
        error_messages.push('Ingrese una fecha válida');
    }

    /* Patient */
    if (patient === '' && new_patient === '') {
        error_messages.push('Elija o cree un nuevo paciente');
    }

    /* Patient weight */
    if (patient_weight === '') {
        error_messages.push('Ingrese un peso válido');
    }

    /* Contact number */
    if (contact_number === '') {
        error_messages.push('Ingrese un nro de teléfono valido');
    }

    /* Medical Study */
    if (medical_study === '') {
        error_messages.push('Elija un estudio válido');
    }

    /* Doctor and equipment validation */
    if (medical_equipment === '' && doctor === '') {
        error_messages.push('ATENCION! El Turno debe tener asignado al menos un Equipo Médico o un Doctor.');
    }

    /* Tax ID number */
    // if (tax_id_number === '') {
    //     error_messages.push('Ingrese un RUC válido');
    // }

    /* Tax ID name */
    // if (tax_id_name === '') {
    //     error_messages.push('Ingrese un Nombre o Razón Social válida');
    // }

    /* patient email */
    // if (patient_email === '') {
    //     error_messages.push('Ingrese un email válido');
    // }

    /* patient_address */
    if (patient_address === '') {
        error_messages.push('Ingrese una dirección válida');
    }

    return error_messages;

}

/* Función submit ajax de formulario de modal */
var formAjaxSubmitForSoundFile = function (form, soundfile) {
    $(form).submit(function (e) {
        console.log('sending form');
        e.preventDefault();
        //let form_data = $(this).serialize();

        let csrf = $('input[name="csrfmiddlewaretoken"]').val();
        let report_date = $('input[name="report_date"]').val();
        let initial_report_date = $('input[name="initial-report_date"]').val();
        let doctor = $('select[name="doctor"]').val();
        let patient = $('input[name="patient"]').val();
        let consultations = $('input[name="consultations"]').val();
        let report_title = $('input[name="report_title"]').val();
        let template = $('select[name="template"]').val();
        let report = CKEDITOR.instances['id_report'].getData();

        let form_data = new FormData();
        form_data.append('csrfmiddlewaretoken', csrf);
        form_data.append('report_date', report_date);
        form_data.append('initial-report_date', initial_report_date);
        form_data.append('doctor', doctor);
        form_data.append('patient', patient);
        form_data.append('consultations', consultations);
        form_data.append('report_title', report_title);
        form_data.append('template', template);
        form_data.append('report', report);
        form_data.append('sound_file', soundfile);


        /* Send form */
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: form_data,
            cache: false,
            contentType: false,
            processData: false,
            success: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr);
                if (xhr.success === 'False') {
                    let error_html = "<p>"+xhr.messages+"</p>";
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        html: error_html,
                        footer: '<p>Si sus datos son correctos y el error persiste, favor póngase en contacto con el administrador del sistema.</p>'
                    });
                } else {
                    swal.fire("Datos guardados!");
                    waitForRedirection(2000, xhr.success_url);
                }
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr);
                let error_html = '<p>Error al tratar de enviar este formulario!</p><br><ul>';
                let errors = xhr.responseJSON.errors;
                if (errors){
                    for (let i = 0; i < errors.length; i++) {
                        error_html += '<li>' + errors[i] + "</li>";
                    }
                }

                error_html = error_html + '</ul>'
                /* Alerta de Error */
                Swal.fire({
                    icon: 'error',
                    title: 'Error...',
                    html: error_html,
                    footer: '<p>Si sus datos son correctos y el error persiste, favor póngase en contacto con el administrador del sistema.</p>'
                });

            }
        });

    });

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async function waitForRedirection(miliseconds, url) {
        console.log('Taking a break...');
        await sleep(miliseconds);
        window.location.replace(url);
    }
}