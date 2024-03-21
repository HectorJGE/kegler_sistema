function initializeFormsets(){
    /* Inicializar tabla de formset de documentos */
    $('#id-table-documents tbody tr').formset({
        'addText': '<i class="fa fa-plus"></i>',
        'deleteText': '<i class="fa fa-trash tiny"></i>',
        'addCssClass': 'btn btn-default',
        'deleteCssClass': 'btn delete-formset-btn',
        'prefix': documents_formset_prefix,
        added: function (elem) {
            $('select').chosen();
            setDropifyInputs();
        },
        removed: function () {
        }
    });

    /* Inicializar tabla de formset de insumos */
    $('#id-table-medical-supplys tbody tr').formset({
        'addText': '<i class="fa fa-plus"></i>',
        'deleteText': '<i class="fa fa-trash tiny"></i>',
        'addCssClass': 'btn btn-default',
        'deleteCssClass': 'btn delete-formset-btn',
        'prefix': medical_supplys_formset_prefix,
        'keepFieldValues': '#id_medical_supplies_used-0-currency',
        added: function (elem) {
            $('select').chosen();
            setMedicalSupplySelectOnChange();
            setMedicalSupplyQuantityOnChange();
            setMedicalSupplyPriceOnChange();
            setMedicalSupplyCoverPercentageOnChange();
            setNewMaskedInputs();
            setCoverTypeSelectOnChange();
            hideUnUsedSupplyCover();
            setMedicalSupplyCoverAmountOnChange();
            setMedicalSuplyCoverageClickEvent();
        },
        removed: function () {
            calculateTotalAmmount();
            calculateTotalAmmountToPayInsurance();
            calculateTotalAmmountToPayPatient();
            calculateDiscount();
        }
    });

    /* Al elegir un producto */
    setMedicalSupplySelectOnChange();

    /* Al cambiar la cantidad de un producto */
    setMedicalSupplyQuantityOnChange();

    /* Al cambiar el precio de un producto */
    setMedicalSupplyPriceOnChange();

    /* Set masked */
    setMaskedInputs();

    /* Al cambiar el porcentaje de cobertura del insumo */
    setMedicalSupplyCoverPercentageOnChange();

    /* Al cambiar el tipo de covertura */
    setCoverTypeSelectOnChange();

    hideUnUsedSupplyCover();

    setMedicalSupplyCoverAmountOnChange();

    setMedicalSuplyCoverageClickEvent();

    /* Dropify */
    setDropifyFileData();
    setDropifyInputs();

    /* Setea data de dropify a archivos existentes */
    function setDropifyFileData(){
        /* File */
        $('.dropify').each( function(index, elem) {
                $(this).data('default-file', documents_files[index]);
        });
    }

    /* Setea los inputsde medical supply con mask */
    function setMaskedInputs(){
        /* precios */
        $('.medical_supply_price').each( function(index, elem) {
            if ($(this).val() === ''){
                $(this).mask("###.###.##0", {reverse: true});
            }
        });
        /* precios totales */
        $('.medical_supply_total_price').each( function(index, elem) {
            if ($(this).val() === ''){
                $(this).mask("###.###.##0", {reverse: true});
            }
        });
        /* monto a pagar seguro */
        $('.ammount_to_pay_insurance').each( function(index, elem) {
            if ($(this).val() === ''){
                $(this).mask("###.###.##0", {reverse: true});
            }
        });
        /* monto a pagar paciente */
        $('.ammount_to_pay_patient').each( function(index, elem) {
            if ($(this).val() === ''){
                $(this).mask("###.###.##0", {reverse: true});
            }
        });
        /* monto de covertura */
        $('.insurance_agreement_coverage_amount').each( function(index, elem) {
            if ($(this).val() === ''){
                $(this).mask("###.###.##0", {reverse: true});
            }
        });
    }

    /* Setea los NUEVOS inputs existentes de medical supply con mask */
    function setNewMaskedInputs(){
        /* precios */
        $('.medical_supply_price').each( function(index, elem) {
            if ($(this).val() === ''){
                $(this).mask("###.###.##0", {reverse: true});
            }
        });
        /* precios totales */
        $('.medical_supply_total_price').each( function(index, elem) {
            if ($(this).val() === ''){
                $(this).mask("###.###.##0", {reverse: true});
            }
        });
        /* monto a pagar seguro */
        $('.ammount_to_pay_insurance').each( function(index, elem) {
            if ($(this).val() === ''){
                $(this).mask("###.###.##0", {reverse: true});
            }
        });
        /* monto a pagar paciente */
        $('.ammount_to_pay_patient').each( function(index, elem) {
            if ($(this).val() === ''){
                $(this).mask("###.###.##0", {reverse: true});
            }
        });
        /* monto de covertura */
        $('.insurance_agreement_coverage_amount').each( function(index, elem) {
            if ($(this).val() === ''){
                $(this).mask("###.###.##0", {reverse: true});
            }
        });

    }

    /* Setea los NUEVOS inputs de archivos de documents con dropify */
    function setDropifyInputs(){
        $('.dropify').dropify(
            {
                messages: {
                    'default': 'Haga click o arrastre un archivo',
                    'replace': 'Haga click o arrastre un archivo para reemplazarlo',
                    'remove':  'Eliminar',
                    'error':   'Ocurrió un error.'
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

    /* Al cambiar la cantidad del insumo */
    function setMedicalSupplyQuantityOnChange(){
        $('.medical_supply_quantity').on('input', function(){
            console.log('quantity');
            let select_cover_type = $(this).closest("tr.dynamic-form").find(".cover_type");
            let input_coverage_amount = $(this).closest("tr.dynamic-form").find(".insurance_agreement_coverage_amount");
            let input_coverage_percent = $(this).closest("tr.dynamic-form").find(".insurance_agreement_coverage_percent");

            calculateMedicalSupplyAmountToPay($(this));
            if (parseInt(select_cover_type.val() === 0)){
                input_coverage_percent.trigger('keyup');
            }else{
                input_coverage_amount.trigger('keyup');
            }

            calculateTotalAmmount();
            calculateTotalAmmountToPayInsurance();
            calculateTotalAmmountToPayPatient();
            calculateDiscount();
        });
    }

    /* Al cambiar el porcentaje de cobertura del insumo */
    function setMedicalSupplyCoverPercentageOnChange(){
        $('.insurance_agreement_coverage_percent').keyup(function(event){
            var input = $(this);
            console.log('insurance_agreement_coverage_percent');
            if (input.val() === ''){
                input.val('0');
                input.trigger('input');
            }
            var medical_supply_price = input.closest("tr.dynamic-form").find(".medical_supply_price");
            var medical_supply_total_price = input.closest("tr.dynamic-form").find(".medical_supply_total_price");
            var medical_supply_cover_percentage = input.closest("tr.dynamic-form").find(".insurance_agreement_coverage_percent");
            var medical_supply_ammount_to_pay_insurance = input.closest("tr.dynamic-form").find(".ammount_to_pay_insurance");
            var medical_supply_ammount_to_pay_patient = input.closest("tr.dynamic-form").find(".ammount_to_pay_patient");

            var amount = parseFloat(medical_supply_total_price.cleanVal());
            var percent = parseFloat(medical_supply_cover_percentage.val());
            var amount_to_pay_insurance = calculatePercent(amount, percent);
            var amount_to_pay_patient = amount - amount_to_pay_insurance;

            medical_supply_ammount_to_pay_insurance.val(amount_to_pay_insurance);
            medical_supply_ammount_to_pay_insurance.trigger('input');
            medical_supply_ammount_to_pay_patient.val(amount_to_pay_patient);
            medical_supply_ammount_to_pay_patient.trigger('input');

            calculateTotalAmmount();
            calculateTotalAmmountToPayInsurance();
            calculateTotalAmmountToPayPatient();
            calculateDiscount();
        });
    }

    function setMedicalSuplyCoverageClickEvent(){
        $('.insurance_agreement_coverage_percent').click(function (){
            $(this).select();
        });

        $('.insurance_agreement_coverage_amount').click(function (){
            $(this).select();
        });
    }

    /* Al cambiar el monto de cobertura del insumo insumo */
    function setMedicalSupplyCoverAmountOnChange(){
        $('.insurance_agreement_coverage_amount').keyup(function(event){
            var input = $(this);
            console.log('insurance_agreement_coverage_amount');
            if (input.val() === ''){
                input.val('0');
                input.trigger('input');
            }
            var medical_supply_price = input.closest("tr.dynamic-form").find(".medical_supply_price");
            var medical_supply_total_price = input.closest("tr.dynamic-form").find(".medical_supply_total_price");
            var medical_supply_cover_percentage = input.closest("tr.dynamic-form").find(".insurance_agreement_coverage_percent");
            var medical_supply_cover_amount = input.closest("tr.dynamic-form").find(".insurance_agreement_coverage_amount");
            var cover_type = input.closest("tr.dynamic-form").find(".cover_type");
            var medical_supply_ammount_to_pay_insurance = input.closest("tr.dynamic-form").find(".ammount_to_pay_insurance");
            var medical_supply_ammount_to_pay_patient = input.closest("tr.dynamic-form").find(".ammount_to_pay_patient");

            var amount = parseFloat(medical_supply_total_price.cleanVal());
            var percent = parseFloat(medical_supply_cover_percentage.val());
            var amount_to_pay_insurance;

            if (parseInt(cover_type.val()) === 0){
                amount_to_pay_insurance = calculatePercent(amount, percent);
            }else{
                amount_to_pay_insurance = medical_supply_cover_amount.cleanVal();
            }

            var amount_to_pay_patient = amount - amount_to_pay_insurance;

            medical_supply_ammount_to_pay_insurance.val(amount_to_pay_insurance);
            medical_supply_ammount_to_pay_insurance.trigger('input');
            medical_supply_ammount_to_pay_patient.val(amount_to_pay_patient);
            medical_supply_ammount_to_pay_patient.trigger('input');

            calculateTotalAmmount();
            calculateTotalAmmountToPayInsurance();
            calculateTotalAmmountToPayPatient();
            calculateDiscount();
        });
    }

    /* Al Cambiar el precio */
    function setMedicalSupplyPriceOnChange() {
        $('.medical_supply_price').keyup(function (event) {
            console.log('price');
            calculateMedicalSupplyCoverage($(this));
            calculateTotalAmmount();
            calculateTotalAmmountToPayInsurance();
            calculateTotalAmmountToPayPatient();
        });
    }

    /* Al elegir un insumo médico */
    function setMedicalSupplySelectOnChange(){
        $(".medical_supply_select").change(function(event){
            var select = $(this);
            if (select.val() !== ''){
                var insurance_plan_id = $('#id_patient_insurance_plan').val();
                /* Traer precio del producto */
                $.ajax({
                    type: 'GET',
                    url: get_product_json_url.replace('9999', $(this).val() ),
                    data:{'insurance_plan_id': insurance_plan_id},
                    success: function (data, textStatus, jqXHR) {
                        var medical_supply_price = select.closest("tr.dynamic-form").find(".medical_supply_price");
                        var medical_supply_total_price = select.closest("tr.dynamic-form").find(".medical_supply_total_price");
                        var medical_supply_quantity = select.closest("tr.dynamic-form").find(".medical_supply_quantity");
                        var medical_supply_currency = select.closest("tr.dynamic-form").find(".medical_supply_currency");
                        var medical_supply_cover_percentage = select.closest("tr.dynamic-form").find(".insurance_agreement_coverage_percent");
                        var medical_supply_cover_amount = select.closest("tr.dynamic-form").find(".insurance_agreement_coverage_amount");
                        var medical_supply_cover_type = select.closest("tr.dynamic-form").find(".cover_type");

                        medical_supply_price.val(data.price.toString().replace('.0', ''));
                        medical_supply_total_price.val(data.price.toString().replace('.0', ''));
                        medical_supply_quantity.val("1");
                        medical_supply_currency.val(data.currency);
                        medical_supply_price.trigger('input');
                        medical_supply_total_price.trigger('input');

                        medical_supply_cover_percentage.val(data.insurance_coverage_percent);
                        medical_supply_cover_amount.val(data.insurance_coverage_amount.toString().replace('.0', ''));
                        medical_supply_cover_amount.trigger('input');
                        medical_supply_cover_type.val(data.cover_type);
                        medical_supply_cover_type.trigger("chosen:updated");
                        medical_supply_cover_type.trigger("change");

                        if (parseInt(medical_supply_cover_type.val() === 0)){
                            medical_supply_cover_percentage.trigger('keyup');
                        }else{
                            medical_supply_cover_amount.trigger('keyup');
                        }

                        get_product_json_url = get_product_json_url.replace(select.val(), '9999');
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
                            text: 'Error al tratar de obtener el precio del producto.',
                            footer: '<p>Favor póngase en contacto con el administrador del sistema.</p>'
                        });
                        get_product_json_url = get_product_json_url.replace(select.val(), '9999');
                    }
                });
            }

        });
    }

    function setCoverTypeSelectOnChange(){
        $('.cover_type').change(function (){
            hideUnUsedSupplyCover();
            let cover_type_select = $(this);
            calculateMedicalSupplyCoverage(cover_type_select);
        });
    }

    function hideUnUsedSupplyCover(){
        $('.medical-supply').each(function (){
            let tr = $(this);
            let cover_type_input = tr.find('.cover_type');
            let td_coverage_amount = cover_type_input.closest("tr.dynamic-form").find(".coverage-amount");
            let td_coverage_percent = cover_type_input.closest("tr.dynamic-form").find(".coverage-percent");
            let coverage_percent = cover_type_input.closest("tr.dynamic-form").find(".insurance_agreement_coverage_percent");
            let coverage_amount = cover_type_input.closest("tr.dynamic-form").find(".insurance_agreement_coverage_amount");
            if(parseInt(cover_type_input.val()) === 0) {
                console.log('insumo es por porcentaje');
                td_coverage_amount.hide();
                td_coverage_percent.show();
                coverage_amount.val("0");
                coverage_amount.trigger('input');
            }else{
                console.log('insumo es por monto');
                td_coverage_percent.hide();
                td_coverage_amount.show();
                coverage_percent.val("0");
                coverage_percent.trigger('input');
            }
        });
    }

    function calculateMedicalSupplyCoverage(select){

        let medical_supply_price = select.closest("tr.dynamic-form").find(".medical_supply_price");
        let medical_supply_total_price = select.closest("tr.dynamic-form").find(".medical_supply_total_price");
        let medical_supply_cover_percentage = select.closest("tr.dynamic-form").find(".insurance_agreement_coverage_percent");
        let medical_supply_cover_amount = select.closest("tr.dynamic-form").find(".insurance_agreement_coverage_amount");
        let medical_supply_cover_type = select.closest("tr.dynamic-form").find(".cover_type");

        let medical_supply_ammount_to_pay_insurance = select.closest("tr.dynamic-form").find(".ammount_to_pay_insurance");
        let medical_supply_ammount_to_pay_patient = select.closest("tr.dynamic-form").find(".ammount_to_pay_patient");

        let amount = parseFloat(medical_supply_total_price.cleanVal());
        let percent = parseFloat(medical_supply_cover_percentage.val());
        let amount_to_pay_insurance;

        if (parseInt(medical_supply_cover_type.val()) === 0){
            amount_to_pay_insurance = calculatePercent(amount, percent);
        }else {
            amount_to_pay_insurance = medical_supply_cover_amount.cleanVal();
        }

        var amount_to_pay_patient = amount - amount_to_pay_insurance;

        medical_supply_ammount_to_pay_insurance.val(amount_to_pay_insurance);
        medical_supply_ammount_to_pay_insurance.trigger('input');
        medical_supply_ammount_to_pay_patient.val(amount_to_pay_patient);
        medical_supply_ammount_to_pay_patient.trigger('input');
    }

    function calculateTotalPrice(select){
        let quantity_input = select.closest("tr.dynamic-form").find(".medical_supply_quantity");
        let price_input = select.closest("tr.dynamic-form").find(".medical_supply_price");
        let total_price_input = select.closest("tr.dynamic-form").find(".medical_supply_total_price");

        let quantity = parseFloat(quantity_input.val());
        let price = parseFloat(price_input.cleanVal());

        let total_price = quantity * price

        total_price_input.val(total_price);
        total_price_input.trigger('input');

    }

    function calculateMedicalSupplyAmountToPay(select){
        calculateTotalPrice(select);
        let total_price_input = select.closest("tr.dynamic-form").find(".medical_supply_total_price");
        let ammount_to_pay_insurance_input = select.closest("tr.dynamic-form").find(".ammount_to_pay_insurance");
        let amount_to_pay_patient_input = select.closest("tr.dynamic-form").find(".ammount_to_pay_patient");

        let total_price = parseFloat(total_price_input.cleanVal());
        let ammount_to_pay_insurance = parseFloat(ammount_to_pay_insurance_input.cleanVal());
        let amount_to_pay_patient = total_price - ammount_to_pay_insurance;

        amount_to_pay_patient_input.val(amount_to_pay_patient);
        amount_to_pay_patient_input.trigger('input');

    }

}