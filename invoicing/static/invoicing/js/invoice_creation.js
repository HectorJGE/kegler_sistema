function initializeInvoiceInputs() {

    $('#sidebarToggle').trigger('click');
    initializemasks();
    cleanEmptyInputs();
    keyupfunctions();
    getLastInvoiceNumberByCompany();
    calcTotal();

    $('#id_client_name').autocomplete({
        source: url_autocomplete_client_name,
        select: function (event, ui) {
            id_cliente = ui.item.value;
            event.preventDefault();
            $('#id_client_name').val(ui.item.name);
            $('#id_client_tax_identification_number').val(ui.item.ruc);
            $('#id_client_email').val(ui.item.email);
            $('#id_client_address').val(ui.item.address);
            $('#id_client_phone_number').val(ui.item.phone_number);
            $('#id_client_tax_payer').prop('checked', ui.item.is_taxpayer);
            $('#id_customer').val(id_cliente);
        }
    });

    $('#id_client_tax_identification_number').autocomplete({
        source: url_autocomplete_client_name,
        select: function (event, ui) {
            id_cliente = ui.item.id;
            event.preventDefault();
            $('#id_client_tax_identification_number').val(ui.item.ruc);
            $('#id_client_name').val(ui.item.name);
            $('#id_client_email').val(ui.item.email);
            $('#id_client_address').val(ui.item.address);
            $('#id_client_phone_number').val(ui.item.phone_number);
            $('#id_client_tax_payer').prop('checked', ui.item.is_taxpayer);
            $('#id_customer').val(id_cliente);
        }
    });

    $('#id_invoice_date').mask("00/00/0000");

    $('#id_invoice_date').click(function () {
        console.log('click en fecha de emision de factura');
        $(this).select();
    });

    /* Datetime picker */
    jQuery.datetimepicker.setLocale('es');

    /* se inicializa los select con chosen */
    $('select').chosen();

    $('.to-upper-case').keyup(function () {
        $(this).val($(this).val().toUpperCase());
    });
    /*
    $('#id_invoice_date').datetimepicker({
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
        defaultDate: new Date(),
        inline: false,
    });

     */
    $("#id_create_invoice_form").submit(function (e) {
        $('.unit_price').each(function (index, elem) {
            if ($(this).cleanVal() === '') {
                var btn_delete = $(this).closest("tr.dynamic-form").find(".delete-formset-btn");
                btn_delete.trigger('click');
            }
        });
        $('#id_total_exempt').unmask();
        $('#id_total_tax5').unmask();
        $('#id_total_tax10').unmask();
        $('#id_total_tax').unmask();
        $('#id_subtotal').unmask();
        $('#id_invoice_total').unmask();
        $('.unit_price').each(function (index, elem) {
            $(this).unmask();
        });
        $('.exempt').each(function (index, elem) {
            $(this).unmask();
        });
        $('.tax_5').each(function (index, elem) {
            $(this).unmask();
        });
        $('.tax_10').each(function (index, elem) {
            $(this).unmask();
        });
        $('#id_company').prop("disabled", false);
        $(this).find("[type=submit]").prop('disabled', true); //disable del boton enviar
        return true; // se envia el formulario
    });
}

function keyupfunctions() {

    $('#id_company').change(function (){
       getLastInvoiceNumberByCompany();
    });

    $('.quantity').keyup(function () {
        calcValues();
        calcTotal();
    });

    $('.unit_price').keyup(function () {
        calcValues();
        calcTotal();
    });
    $('.tax_5').change(function () {
        checkValues();
        calcTotal();
    });
    $('.tax_10').change(function () {
        checkValues();
        calcTotal();
    });
    $('.exempt').change(function () {
        checkValues();
        calcTotal();
    });
}

function getLastInvoiceNumberByCompany(){
    let company_id = $('#id_company').val();
    $.ajax({
                type: 'GET',
                url: url_get_last_invoice_number.replace('9999', $('#id_company').val() ),
                data: { company_id: company_id },
                success: function (data, textStatus, jqXHR) {
                    // console.log(data);
                    let msg = data[0].msg
                    if (msg !== ""){
                        Swal.fire({
                            icon: 'error',
                            title: 'Error...',
                            text: ''+msg,
                            footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                        });
                        $('#id_invoice_number').val(0);
                        $('#id_invoice_stamp').val(0);
                    } else {
                        $('#id_invoice_number').val(data[0].invoice_number);
                        $('#id_invoice_stamp').val(data[0].stamp_id);
                    }
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    /* Alerta de Error */
                    Swal.fire({
                        icon: 'error',
                        title: 'Error...',
                        text: 'Error al tratar de obtener el ultimo nro de factura de la empresa seleccionada.',
                        footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                    });

                }
        });
}


function initializeFormsets() {
    $('#id-table-details tbody tr').formset({
        'addText': '<i class="fas fa-plus"></i>',
        'deleteText': '<i class="fas fa-trash"></i>',
        'addCssClass': 'btn btn-default',
        'deleteCssClass': 'btn delete-formset-btn',
        'prefix': details_formset_prefix,
        added: function (elem) {
            setNewMaskedInputs();
            keyupfunctions();
            initializeAllInputs();
        },
        removed: function (elem) {
            cleanEmptyInputs();
            calcTotalTaxes();
        }
    });
}

/*
    Inicializa Inputs de formsets para que comiencen con valor 0.
 */
function initializeAllInputs() {
    $('.dynamic-form').each(function (index, elem) {
        let amount = $(this).closest("tr.dynamic-form").find(".quantity")
        let iva10 = $(this).closest("tr.dynamic-form").find(".tax_10")
        let iva5 = $(this).closest("tr.dynamic-form").find(".tax_5")
        let exempt = $(this).closest("tr.dynamic-form").find(".exempt")
        let unit_price = $(this).closest("tr.dynamic-form").find(".unit_price")

        if (amount.val() === "") {
            amount.val(0);
        }
        if (iva10.cleanVal() === "") {
            iva10.val(0);
        }
        if (iva5.cleanVal() === "") {
            iva5.val(0);
        }
        if (exempt.cleanVal() === "") {
            exempt.val(0);
        }
        if (unit_price.cleanVal() === "") {
            unit_price.val(0);
        }

    });
}

/* funcion para calculo de valores automaticos
  se calcula valores en IVA 10% de acuerdo a la cantidad y precio unitario.
  luego se calcula el total TAX. */
function calcValues() {
    let tax10 = 0;
    $('.dynamic-form').each(function (index, elem) {
        let amount = $(this).closest("tr.dynamic-form").find(".quantity").val();
        let unit_price = $(this).closest("tr.dynamic-form").find(".unit_price").cleanVal();
        let exempt = $(this).closest("tr.dynamic-form").find(".exempt");
        let autosum = parseFloat(parseFloat(amount) * parseFloat(unit_price)).toFixed(0);
        let iva10 = $(this).closest("tr.dynamic-form").find(".tax_10");
        let iva5 = $(this).closest("tr.dynamic-form").find(".tax_5");
        if(exempt.cleanVal() === '0' && iva5.cleanVal() === '0'){
            iva10.val(autosum);
            iva10.trigger('input');
        }
    });
    calcTotal();
}

function checkValues(){

    $('.dynamic-form').each(function (index, elem) {
        let amount = $(this).closest("tr.dynamic-form").find(".quantity");
        let iva10 = $(this).closest("tr.dynamic-form").find(".tax_10");
        let iva5 = $(this).closest("tr.dynamic-form").find(".tax_5");
        let exempt = $(this).closest("tr.dynamic-form").find(".exempt");

        if (iva10.cleanVal() === ""){
            iva10.val(0);
        }
        if (iva5.cleanVal() === ""){
            iva5.val(0);
        }
        if (exempt.cleanVal() === ""){
            exempt.val(0);
        }
        if (amount.val() === ""){
            amount.val(0);
        }


    });
}
// calculo total impuestos

function calcTotalTaxes() {
    let tax5 = $('#id_total_tax5').cleanVal();
    let tax10 = $('#id_total_tax10').cleanVal();
    let totaltax = parseFloat(tax5) + parseFloat(tax10);
    $('#id_total_tax').val(parseFloat(totaltax).toFixed(0));
    $('#id_total_tax').trigger('input');
}

//check values para que no sean undefined

function checkTaxes() {
    let tax5 = $('#id_total_tax5').cleanVal();
    let tax10 = $('#id_total_tax10').cleanVal();
    if (tax5 === "" && tax10 !== "") {
        $('#id_total_tax5').val(0);
    }
    if (tax5 !== "" && tax10 === "") {
        $('#id_total_tax10').val(0);
    }
    if (tax5 === 0 && tax10 === 0) {
        $('#id_total_tax').val(0);
    }

}

/*
    Funcion para el calculo del Total en IVA, Subtotal
    y tambien conversion del total a letras.
 */
function calcTotal() {
    let totaltax10 = 0;
    let totaltax5 = 0;
    let totalexempt = 0;
    $('.dynamic-form').each(function (index, elem) {
        let amount = $(this).closest("tr.dynamic-form").find(".quantity").val();
        let iva10 = $(this).closest("tr.dynamic-form").find(".tax_10").cleanVal();
        let iva5 = $(this).closest("tr.dynamic-form").find(".tax_5").cleanVal();
        let exempt = $(this).closest("tr.dynamic-form").find(".exempt").cleanVal();
        if (iva10 !== "") {
            totaltax10 += parseFloat(iva10);
        } else {
            totaltax10 += 0;
        }
        if (iva5 !== 0) {
            totaltax5 += parseFloat(iva5);
        } else {
            totaltax5 += 0;
        }
        if (exempt !== 0) {
            totalexempt += parseFloat(exempt);
        } else {
            totalexempt += 0;
        }
    });
    let total = parseFloat(parseFloat(totaltax10) + parseFloat(totaltax5) + parseFloat(totalexempt));

    //calculo exentas
    $('#id_total_exempt').val(parseFloat(totalexempt).toFixed(0));
    $('#id_total_exempt').trigger('input');

    //calculo IVA 10%
    let tax10 = totaltax10 / 11;
    $('#id_total_tax10').val(parseFloat(tax10).toFixed(0));
    $('#id_total_tax10').trigger('input');

    // calculo IVA 5%
    let tax5 = totaltax5 / 21;
    $('#id_total_tax5').val(parseFloat(tax5).toFixed(0));
    $('#id_total_tax5').trigger('input');

    calcTotalTaxes();

    $('#id_subtotal').val(parseFloat(total).toFixed(0));
    $('#id_subtotal').trigger('input');
    $('#id_invoice_total').val(parseFloat(total).toFixed(0));
    $('#id_invoice_total').trigger('input');
    totalletra();

}

//funcion para verificar los valores vacios e inicializarlos en 0.
function checkValues() {
    $('.dynamic-form').each(function (index, elem) {
        let amount = $(this).closest("tr.dynamic-form").find(".quantity");
        let iva10 = $(this).closest("tr.dynamic-form").find(".tax_10");
        let iva5 = $(this).closest("tr.dynamic-form").find(".tax_5");
        let exempt = $(this).closest("tr.dynamic-form").find(".exempt");

        if (iva10.cleanVal() === "") {
            iva10.val(0);
        }
        if (iva5.cleanVal() === "") {
            iva5.val(0);
        }
        if (exempt.cleanVal() === "") {
            exempt.val(0);
        }
        if (amount.val() === "") {
            amount.val(0);
        }
        calcTotal();
    });
}

// calculo total impuestos

function calcTotalTaxes() {
    let tax5 = $('#id_total_tax5').cleanVal();
    let tax10 = $('#id_total_tax10').cleanVal();
    let totaltax = parseFloat(tax5) + parseFloat(tax10);
    $('#id_total_tax').val(parseFloat(totaltax).toFixed(0));
    $('#id_total_tax').trigger('input');
}

function totalletra() {

    $('#id_invoice_total_letters').val(numeroALetras($('#id_invoice_total').cleanVal()), {
        plural: 'guaranies',
        singular: 'guarani',
        centPlural: 'centavos',
        centSingular: 'centavo'
    })
}

function cleanEmptyInputs() {
    $('.dynamic-form').each(function (index, elem) {
        if ($(this).is(':hidden')){
            $(this).closest("tr.dynamic-form").find(".quantity").val(0);
            $(this).closest("tr.dynamic-form").find(".tax_10").val(0);
            $(this).closest("tr.dynamic-form").find(".tax_5").val(0);
            $(this).closest("tr.dynamic-form").find(".exempt").val(0);
            $(this).closest("tr.dynamic-form").find(".unit_price").val(0);
            calcTotal();
        }
        let amount = $(this).closest("tr.dynamic-form").find(".quantity");
        let iva10 = $(this).closest("tr.dynamic-form").find(".tax_10");
        let iva5 = $(this).closest("tr.dynamic-form").find(".tax_5");
        let exempt = $(this).closest("tr.dynamic-form").find(".exempt");
        let unit_price = $(this).closest("tr.dynamic-form").find(".unit_price");

        if (iva10.cleanVal() === "") {
            iva10.val(0);
        }
        if (iva5.cleanVal() === "") {
            iva5.val(0);
        }
        if (exempt.cleanVal() === "") {
            exempt.val(0);
        }
        if (amount.val() === "") {
            amount.val(0);
        }
        if (unit_price.cleanVal() === "") {
            unit_price.val(0);
        }
    });

}

function initializemasks() {
    /* Mask para monto total de EXENTAS */
    if ($('#id_total_exempt').val() !== '') {
        var total_exempt = $('#id_total_exempt').val().replace('.0', '');
        $('#id_total_exempt').val('');
        $('#id_total_exempt').val(total_exempt);
        $('#id_total_exempt').mask("###.###.###.##0", {reverse: true});
    } else {
        $('#id_total_exempt').mask("###.###.###.##0", {reverse: true});
    }
    /* Mask para monto total de IVA 5% */
    if ($('#id_total_tax5').val() !== ''){
        var total_tax_5 = $('#id_total_tax5').val().replace('.0', '');
        $('#id_total_tax5').val('');
        $('#id_total_tax5').val(total_tax_5);
        $('#id_total_tax5').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_total_tax5').mask("###.###.##0", {reverse: true});
    }
    /* Mask para monto total de IVA 10% */
    if ($('#id_total_tax10').val() !== ''){
        var total_tax_10 = $('#id_total_tax10').val().replace('.0', '');
        $('#id_total_tax10').val('');
        $('#id_total_tax10').val(total_tax_10);
        $('#id_total_tax10').mask("###.###.###.##0", {reverse: true});
    } else {
        $('#id_total_tax10').mask("###.###.###.##0", {reverse: true});
    }
    /* Mask para monto total de TOTAL IVA */
    if ($('#id_total_tax').val() !== ''){
        var total_tax = $('#id_total_tax').val().replace('.0', '');
        $('#id_total_tax').val('');
        $('#id_total_tax').val(total_tax);
        $('#id_total_tax').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_total_tax').mask("###.###.##0", {reverse: true});
    }
    /* Mask para monto del subtotal */
    if ($('#id_subtotal').val() !== ''){
        var subtotal = $('#id_subtotal').val().replace('.0', '');
        $('#id_subtotal').val('');
        $('#id_subtotal').val(subtotal);
        $('#id_subtotal').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_subtotal').mask("###.###.##0", {reverse: true});
    }
    /* Mask para monto del Total */
    if ($('#id_invoice_total').val() !== ''){
        var total = $('#id_invoice_total').val().replace('.0', '');
        $('#id_invoice_total').val('');
        $('#id_invoice_total').val(total);
        $('#id_invoice_total').mask("###.###.##0", {reverse: true});
    } else {
        $('#id_invoice_total').mask("###.###.##0", {reverse: true});
    }
    setMaskedInputs();
}

function setMaskedInputs() {
    /* precio unitario */
        $('.unit_price').each( function(index, elem) {
            if ($(this).val() !== ''){
                var total = $(this).val().replace('.0', '');
                $(this).val('');
                $(this).val(total);
                $(this).mask("###.###.##0", {reverse: true});
            } else {
                $(this).mask("###.###.##0", {reverse: true});
            }
        });
    /* exentas */
        $('.exempt').each( function(index, elem) {
            if ($(this).val() !== ''){
                var total = $(this).val().replace('.0', '');
                $(this).val('');
                $(this).val(total);
                $(this).mask("###.###.##0", {reverse: true});
            } else {
                $(this).mask("###.###.##0", {reverse: true});
                $(this).trigger('input');
            }
        });
    /* IVA 5% */
        $('.tax_5').each( function(index, elem) {
            if ($(this).val() !== ''){
                var total = $(this).val().replace('.0', '');
                $(this).val('');
                $(this).val(total);
                $(this).mask("###.###.##0", {reverse: true});
            } else {
                $(this).mask("###.###.##0", {reverse: true});
            }
        });
    /* IVA 10% */
        $('.tax_10').each( function(index, elem) {
            if ($(this).val() !== ''){
                var total = $(this).val().replace('.0', '');
                $(this).val('');
                $(this).val(total);
                $(this).mask("###.###.##0", {reverse: true});
            } else {
                $(this).mask("###.###.##0", {reverse: true});
            }
        });
}

function setNewMaskedInputs() {
    /* precios unitarios */
    $('.unit_price').each(function (index, elem) {
        if ($(this).val() === '') {
            $(this).mask("###.###.##0", {reverse: true});
        }
    });
    /* exentas */
    $('.exempt').each(function (index, elem) {
        if ($(this).val() === '') {
            $(this).mask("###.###.##0", {reverse: true});
        }
    });
    /* IVA 5% */
    $('.tax_5').each(function (index, elem) {
        if ($(this).val() === '') {
            $(this).mask("###.###.##0", {reverse: true});
        }
    });
    /* IVA 10% */
    $('.tax_10').each(function (index, elem) {
        if ($(this).val() === '') {
            $(this).mask("###.###.##0", {reverse: true});
        }
    });
}

var numeroALetras = (function () {

// Código basado en https://gist.github.com/alfchee/e563340276f89b22042a
    function Unidades(num) {

        switch (num) {
            case 1:
                return 'UN';
            case 2:
                return 'DOS';
            case 3:
                return 'TRES';
            case 4:
                return 'CUATRO';
            case 5:
                return 'CINCO';
            case 6:
                return 'SEIS';
            case 7:
                return 'SIETE';
            case 8:
                return 'OCHO';
            case 9:
                return 'NUEVE';
        }

        return '';
    }//Unidades()

    function Decenas(num) {

        let decena = Math.floor(num / 10);
        let unidad = num - (decena * 10);

        switch (decena) {
            case 1:
                switch (unidad) {
                    case 0:
                        return 'DIEZ';
                    case 1:
                        return 'ONCE';
                    case 2:
                        return 'DOCE';
                    case 3:
                        return 'TRECE';
                    case 4:
                        return 'CATORCE';
                    case 5:
                        return 'QUINCE';
                    default:
                        return 'DIECI' + Unidades(unidad);
                }
            case 2:
                switch (unidad) {
                    case 0:
                        return 'VEINTE';
                    default:
                        return 'VEINTI' + Unidades(unidad);
                }
            case 3:
                return DecenasY('TREINTA', unidad);
            case 4:
                return DecenasY('CUARENTA', unidad);
            case 5:
                return DecenasY('CINCUENTA', unidad);
            case 6:
                return DecenasY('SESENTA', unidad);
            case 7:
                return DecenasY('SETENTA', unidad);
            case 8:
                return DecenasY('OCHENTA', unidad);
            case 9:
                return DecenasY('NOVENTA', unidad);
            case 0:
                return Unidades(unidad);
        }
    }//Unidades()

    function DecenasY(strSin, numUnidades) {
        if (numUnidades > 0)
            return strSin + ' Y ' + Unidades(numUnidades)

        return strSin;
    }//DecenasY()

    function Centenas(num) {
        let centenas = Math.floor(num / 100);
        let decenas = num - (centenas * 100);

        switch (centenas) {
            case 1:
                if (decenas > 0)
                    return 'CIENTO ' + Decenas(decenas);
                return 'CIEN';
            case 2:
                return 'DOSCIENTOS ' + Decenas(decenas);
            case 3:
                return 'TRESCIENTOS ' + Decenas(decenas);
            case 4:
                return 'CUATROCIENTOS ' + Decenas(decenas);
            case 5:
                return 'QUINIENTOS ' + Decenas(decenas);
            case 6:
                return 'SEISCIENTOS ' + Decenas(decenas);
            case 7:
                return 'SETECIENTOS ' + Decenas(decenas);
            case 8:
                return 'OCHOCIENTOS ' + Decenas(decenas);
            case 9:
                return 'NOVECIENTOS ' + Decenas(decenas);
        }

        return Decenas(decenas);
    }//Centenas()

    function Seccion(num, divisor, strSingular, strPlural) {
        let cientos = Math.floor(num / divisor)
        let resto = num - (cientos * divisor)

        let letras = '';

        if (cientos > 0)
            if (cientos > 1)
                letras = Centenas(cientos) + ' ' + strPlural;
            else
                letras = strSingular;

        if (resto > 0)
            letras += '';

        return letras;
    }//Seccion()

    function Miles(num) {
        let divisor = 1000;
        let cientos = Math.floor(num / divisor)
        let resto = num - (cientos * divisor)

        let strMiles = Seccion(num, divisor, 'UN MIL', 'MIL');
        let strCentenas = Centenas(resto);

        if (strMiles == '')
            return strCentenas;

        return strMiles + ' ' + strCentenas;
    }//Miles()

    function Millones(num) {
        let divisor = 1000000;
        let cientos = Math.floor(num / divisor)
        let resto = num - (cientos * divisor)

        let strMillones = Seccion(num, divisor, 'UN MILLON DE', 'MILLONES DE');
        let strMiles = Miles(resto);

        if (strMillones == '')
            return strMiles;

        return strMillones + ' ' + strMiles;
    }//Millones()

    return function NumeroALetras(num, currency) {
        currency = currency || {};
        let data = {
            numero: num,
            enteros: Math.floor(num),
            centavos: (((Math.round(num * 100)) - (Math.floor(num) * 100))),
            letrasCentavos: '',
            letrasMonedaPlural: currency.plural || 'GUARANIES',//'PESOS', 'Dólares', 'Bolívares', 'etcs'
            letrasMonedaSingular: currency.singular || 'GUARANI', //'PESO', 'Dólar', 'Bolivar', 'etc'
            letrasMonedaCentavoPlural: currency.centPlural || 'CENTAVOS DE GUARANI',
            letrasMonedaCentavoSingular: currency.centSingular || 'CENTAVO DE GUARANI'
        };

        if (data.centavos > 0) {
            data.letrasCentavos = 'CON ' + (function () {
                if (data.centavos == 1)
                    return Millones(data.centavos) + ' ' + data.letrasMonedaCentavoSingular;
                else
                    return Millones(data.centavos) + ' ' + data.letrasMonedaCentavoPlural;
            })();
        }
        ;

        if (data.enteros == 0)
            return 'CERO ' + data.letrasMonedaPlural + ' ' + data.letrasCentavos;
        if (data.enteros == 1)
            return Millones(data.enteros) + ' ' + data.letrasMonedaSingular + ' ' + data.letrasCentavos;
        else
            return Millones(data.enteros) + ' ' + data.letrasMonedaPlural + ' ' + data.letrasCentavos;
    };

})();

