
/* Calcular monto total  */
function calculateTotalAmmount() {
    var total_amount = $('#id_total_amount');
    var medical_supplies_ammount = $('#id_medical_supplies_ammount');
    var medical_study_ammount_val = $('#id_medical_study_ammount').cleanVal();

    if (medical_study_ammount_val === '') {
        medical_study_ammount_val = 0;
    } else {
        medical_study_ammount_val = parseFloat(medical_study_ammount_val);
    }

    var medical_supplies_quantitys = $('.medical_supply_quantity');
    var medical_supplies_prices = $('.medical_supply_price');

    var total_medical_supplies_prices_sum = 0;

    medical_supplies_quantitys.each(function (index, elem) {
        let delete_input = $(this).closest("tr.dynamic-form").find("#next_to_delete").next();
        if (delete_input.val() !== 'on') {
            var quantity = $(this).val();

            if (quantity === '') {
                quantity = 0;
            } else {
                quantity = parseFloat($(this).val());
            }

            var price = $(medical_supplies_prices[index]).cleanVal();
            if (price === '') {
                price = 0;
            } else {
                price = parseFloat(price);
            }

            total_medical_supplies_prices_sum = total_medical_supplies_prices_sum + (quantity * price);
        }
    });
    medical_supplies_ammount.val(total_medical_supplies_prices_sum);
    medical_supplies_ammount.trigger('input');
    total_amount.val(medical_study_ammount_val + total_medical_supplies_prices_sum);
    total_amount.trigger('input');

}

/* Calcular monto total a pagar por el seguro */
function calculateTotalAmmountToPayInsurance() {
    var total_amount_to_pay_insurance = $('#id_total_ammount_to_pay_insurance');
    var medical_supplies_ammount_to_pay_insurance = $('#id_medical_supplies_ammount_to_pay_insurance');
    var medical_study_ammount_to_pay_insurance_val = $('#id_medical_study_ammount_to_pay_insurance').cleanVal();

    if (medical_study_ammount_to_pay_insurance_val === '') {
        medical_study_ammount_to_pay_insurance_val = 0;
    } else {
        medical_study_ammount_to_pay_insurance_val = parseFloat(medical_study_ammount_to_pay_insurance_val);
    }

    var medical_supplies_quantitys = $('.medical_supply_quantity');
    var medical_supplies_amounts_to_pay_insurance = $('.ammount_to_pay_insurance');

    var total_medical_supplies_amount_to_pay_insurance_sum = 0;

    medical_supplies_quantitys.each(function (index, elem) {
        let delete_input = $(this).closest("tr.dynamic-form").find("#next_to_delete").next();
        if (delete_input.val() !== 'on') {
            var quantity = $(this).val();

            if (quantity === '') {
                quantity = 0;
            } else {
                quantity = parseFloat($(this).val());
            }

            var price = $(medical_supplies_amounts_to_pay_insurance[index]).cleanVal();
            if (price === '') {
                price = 0;
            } else {
                price = parseFloat(price);
            }

            total_medical_supplies_amount_to_pay_insurance_sum = total_medical_supplies_amount_to_pay_insurance_sum + price;
        }

    });
    medical_supplies_ammount_to_pay_insurance.val(total_medical_supplies_amount_to_pay_insurance_sum);
    medical_supplies_ammount_to_pay_insurance.trigger('input');
    total_amount_to_pay_insurance.val(medical_study_ammount_to_pay_insurance_val + total_medical_supplies_amount_to_pay_insurance_sum);
    total_amount_to_pay_insurance.trigger('input');

}

/* Calcular monto total a pagar por el paciente */
function calculateTotalAmmountToPayPatient() {
    var total_amount_to_pay_patient = $('#id_total_ammount_to_pay_patient');
    var medical_supplies_ammount_to_pay_patient = $('#id_medical_supplies_ammount_to_pay_patient');
    var medical_study_ammount_to_pay_patient_val = $('#id_medical_study_ammount_to_pay_patient').cleanVal();

    if (medical_study_ammount_to_pay_patient_val === '') {
        medical_study_ammount_to_pay_patient_val = 0;
    } else {
        medical_study_ammount_to_pay_patient_val = parseFloat(medical_study_ammount_to_pay_patient_val);
    }

    var medical_supplies_quantitys = $('.medical_supply_quantity');
    var medical_supplies_amounts_to_pay_patient = $('.ammount_to_pay_patient');

    var total_medical_supplies_amount_to_pay_patient_sum = 0;

    medical_supplies_quantitys.each(function (index, elem) {
        let delete_input = $(this).closest("tr.dynamic-form").find("#next_to_delete").next();
        if (delete_input.val() !== 'on') {
            var quantity = $(this).val();

            if (quantity === '') {
                quantity = 0;
            } else {
                quantity = parseFloat($(this).val());
            }

            var price = $(medical_supplies_amounts_to_pay_patient[index]).cleanVal();
            if (price === '') {
                price = 0;
            } else {
                price = parseFloat(price);
            }

            total_medical_supplies_amount_to_pay_patient_sum = total_medical_supplies_amount_to_pay_patient_sum + price;
        }
    });
    medical_supplies_ammount_to_pay_patient.val(total_medical_supplies_amount_to_pay_patient_sum);
    medical_supplies_ammount_to_pay_patient.trigger('input');
    total_amount_to_pay_patient.val(medical_study_ammount_to_pay_patient_val + total_medical_supplies_amount_to_pay_patient_sum);
    total_amount_to_pay_patient.trigger('input');

    /* Se esconden los inputs de pagos si nohay nada que pagar por el paciente */
    if ( $('#id_total_ammount_to_pay_patient').val() === '0' || $('#id_total_ammount_to_pay_patient').val() === '' ){
        $('#div_id_payment_method').hide();
        $('#div_id_payment_reference').hide();
        $('#div_id_discount').hide();
        $('#div_id_total_ammount_to_pay_patient_with_discount').hide();

    } else {
        $('#div_id_payment_method').show();
        $('#div_id_payment_reference').show();
        $('#div_id_discount').show();
        $('#div_id_total_ammount_to_pay_patient_with_discount').show();
    }

}

/* Abrir una url en una nueva pestaña */
function openInNewTab(url) {
    var win = window.open(url, '_blank');
    win.focus();
}

/* Calcular el x% de un numero */
function calculatePercent(num, percent){
    return parseInt((percent / 100) * num);
}

/* Calcular monto de cobertura del estudio médico */
function calculateMedicalStudyCoverage(){
    var amount = parseFloat($('#id_medical_study_ammount').cleanVal());
    var percent = parseFloat($('#id_insurance_agreement_coverage_percent').val());
    var cover_amount = parseFloat($('.study_insurance_agreement_coverage_amount').cleanVal());
    var cover_type = parseInt($('#id_study_cover_type').val());
    var amount_to_pay_insurance;
    if (cover_type === 0){
        amount_to_pay_insurance = calculatePercent(amount, percent);
        $('.study_insurance_agreement_coverage_amount').val('0');
    } else {
        amount_to_pay_insurance = cover_amount;
        $('.study_insurance_agreement_coverage_percent').val('0');
    }
    var amount_to_pay_patient = amount - amount_to_pay_insurance;
    $('#id_medical_study_ammount_to_pay_insurance').val(amount_to_pay_insurance);
    $('#id_medical_study_ammount_to_pay_insurance').trigger('input');
    $('#id_medical_study_ammount_to_pay_patient').val(amount_to_pay_patient);
    $('#id_medical_study_ammount_to_pay_patient').trigger('input');
}

/* Calcular descuento */
function calculateDiscount(){
    var total_amount_to_pay_patient = $('#id_total_ammount_to_pay_patient');
    var discount = $('#id_discount');
    var total_amount_to_pay_patient_with_discount = $('#id_total_ammount_to_pay_patient_with_discount');
    var total_amount_val = parseFloat(total_amount_to_pay_patient.cleanVal());
    var discount_val = parseFloat(discount.cleanVal());
    if (isNaN(discount_val)){
        discount_val = 0;
        discount.val('0');
    }
    var difference = total_amount_val - discount_val

    total_amount_to_pay_patient_with_discount.val(difference);
    total_amount_to_pay_patient_with_discount.trigger('input');

    /* Se esconden los inputs de pagos si no hay nada que pagar por el paciente */
    if ( $('#id_total_ammount_to_pay_patient_with_discount').val() === '0' || $('#id_total_ammount_to_pay_patient_with_discount').val() === '' ){
        $('#div_id_payment_method').hide();
        $('#div_id_payment_reference').hide();
        $('#id_amount_paid').val($('#id_total_ammount_to_pay_patient_with_discount').cleanVal());
        $('#id_amount_paid').trigger('input');
        $('#id_patient_balance').val('0');
    } else {
        $('#div_id_payment_method').show();
        $('#div_id_amount_paid').show();
        $('#id_amount_paid').val($('#id_total_ammount_to_pay_patient_with_discount').cleanVal());
        $('#id_amount_paid').trigger('input');
        $('#id_patient_balance').val('0');

        if( $('#id_payment_method').val() === '1' || $('#id_payment_method').val() === ''  ){
            $('#div_id_payment_reference').hide();
        }else{
            $('#div_id_payment_reference').show();
        }
    }

}

/* Calcular saldo paciente */
function calculatePatientBalance(){
    let total_amount_to_pay_patient_with_discount = $('#id_total_ammount_to_pay_patient_with_discount').cleanVal();
    let amount_paid = $('#id_amount_paid').cleanVal();
    let patient_balance = $('#id_patient_balance');

    let balance = parseFloat(total_amount_to_pay_patient_with_discount) - parseFloat(amount_paid);
    patient_balance.val('');
    patient_balance.val(balance);
    patient_balance.trigger('input');

}